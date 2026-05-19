from enum import Enum
from dynamixel_sdk import *
import math
class Motor():
    all_motors = []
    portHandler = PortHandler("COM3")
    packetHandler = PacketHandler(2.0)
    portHandler.setBaudRate(57600)
    torque_on_address = 64

    @staticmethod
    def close_port():
        #Motor.portHandler.closePort()
        pass
    @staticmethod
    def end_motor(id):
        Motor.packetHandler.write1ByteTxRx(Motor.portHandler, id, Motor.torque_on_address, 0)

    TORQUE_ADDRESS = 64
    TARGET_POSITION_ADDRESS = 116
    TARGET_VELOCITY_ADDRESS = 104
    TARGET_CURRENT_ADDRESS = 102
    AMPERAGE_ADDRESS = 126
    VOLTAGE_ADDRESS = 130
    POSITION_ADDRESS = 132
    VELOCITY_ADDRESS = 128
    OPERATING_MODE_ADDRESS = 11
    VELOCITY_OPERATING_ID = 1
    POSITION_OPERATING_ID = 3
    CURRENT_BASED_POSITION_OPERATING_ID = 5
    CURRENT_OPERATING_ID = 0

    @staticmethod
    def mode_to_id(mode):
        if mode == Modes.VELOCITY:
            return Motor.VELOCITY_OPERATING_ID
        elif mode == Modes.POSITION:
            return Motor.POSITION_OPERATING_ID
        elif mode == Modes.CURRENT_BASED_POSITION:
            return Motor.CURRENT_BASED_POSITION_OPERATING_ID
        return Motor.CURRENT_OPERATING_ID
    
    def __init__(self,id,mode):
        self.all_motors.append(id)
        self.position = None
        self.amperage = None
        self.velocity = None
        self.max_power = 0
        self.max_amperage = 0
        self.target = 0
        self.amperage = 0
        self.voltage = 0
        self.power = 0
        self.dxl_id = id
        self.data = 1
        self.comm_result, self.error = Motor.packetHandler.write1ByteTxRx(Motor.portHandler, self.dxl_id, Motor.TORQUE_ADDRESS, self.data)
        self.set_mode(mode)
        if self.comm_result != COMM_SUCCESS:
            print("%s" % Motor.packetHandler.getTxRxResult(self.comm_result))
        elif self.error != 0:
            print("%s" % Motor.packetHandler.getRxPacketError(self.error))
        else:
            print("Dynamixel has been successfully connected")
    def set_current(self,target):
        target = round(target)
        if target > 400:
            target = 400
        self.max_amperage = target
        self.comm_result, self.error = Motor.packetHandler.write4ByteTxRx(Motor.portHandler, self.dxl_id, Motor.TARGET_CURRENT_ADDRESS, self.max_amperage)
    def set_position(self,target):
        self.target = target
        self.comm_result, self.error = Motor.packetHandler.write4ByteTxRx(Motor.portHandler, self.dxl_id, Motor.TARGET_POSITION_ADDRESS, self.target)
    def set_velocity(self,target):
        self.target = target
        self.comm_result, self.error = Motor.packetHandler.write4ByteTxRx(Motor.portHandler, self.dxl_id, Motor.TARGET_VELOCITY_ADDRESS, self.target)
    def set_mode(self,mode):
        self.mode = mode
        self.comm_result, self.error = Motor.packetHandler.write4ByteTxRx(Motor.portHandler, self.dxl_id, Motor.OPERATING_MODE_ADDRESS, Motor.mode_to_id(mode))
    def set_on(self,on):
        #convert boolean to binary
        data = 0
        if on:
            data = 1
        Motor.packetHandler.write1ByteTxRx(Motor.portHandler, self.dxl_id, Motor.TORQUE_ADDRESS, data)
    def update(self):
        self.position, self.comm_result, self.error = Motor.packetHandler.read4ByteTxRx(Motor.portHandler, self.dxl_id, Motor.POSITION_ADDRESS)
        self.velocity = Motor.packetHandler.read2ByteTxRx(Motor.portHandler, self.dxl_id, Motor.VELOCITY_ADDRESS)
        self.amperage = Motor.packetHandler.read2ByteTxRx(Motor.portHandler, self.dxl_id, Motor.AMPERAGE_ADDRESS)
        self.voltage = Motor.packetHandler.read2ByteTxRx(Motor.portHandler, self.dxl_id, Motor.VOLTAGE_ADDRESS)
    
    def status(self):
        return f"Mode: {self.mode.value}\nPosition: {self.position}\nAmperage: {self.amperage}\nVelocity: {self.velocity}\nTarget {self.mode.value}: {self.target}"
    @staticmethod
    def empty_status_with_target(mode,target):
        return f"Mode: {mode.value} Present: N/A\nAmperage: N/A\nTarget: {round(target, 4)}"

    
class Modes(Enum):
    VELOCITY = "VELOCITY",
    POSITION = "POSITION" 
    CURRENT = "CURRENT"
    CURRENT_BASED_POSITION = "CURRENT_BASED_POSITION"
class Subsystem():
    def __init__(self):
        self.state = "N/A"
        self.on = True
        self.telemetry = "N/A"
        self.name = "Subsystem"
        self.target = 0
        self.mode = Modes.POSITION
        self.max = 4095
        self.min = 0
    def flip(self):
        self.on = not self.on
    def update(self):
        self.telemetry = f"On: {self.on}\nState: {self.state}\n{Motor.empty_status_with_target(self.mode,self.target)}"

class ClawStates(Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"

class Claw(Subsystem):
    KP = .1
    #Open = min
    #Closed = max
    def __init__(self):
        super().__init__()
        self.state = ClawStates.OPEN
        self.mode = Modes.CURRENT_BASED_POSITION
        self.min = 1100
        self.max = 2500
        self.target = self.min
        self.name = "CLAW"
        self.motor0 = Motor(15,self.mode)
        self.motor0.set_mode(self.mode)
        self.motor0.update()
    def flip_claw_state(self):
        if (self.state == ClawStates.OPEN):
            self.state = ClawStates.CLOSE
            self.target = self.max
        else:
            self.state = ClawStates.OPEN
            self.target = self.min
    def update(self):
        self.motor0.set_position(self.target)
        pos_error = abs(self.target - self.motor0.position)
        if self.state == ClawStates.OPEN:
            self.motor0.set_current(400)
        else:
            self.motor0.set_current(pos_error * self.KP)
        self.telemetry = self.motor0.status()
        self.motor0.set_on(self.on)
        self.motor0.update()

class Arm(Subsystem):
    def __init__(self):
        super().__init__()
        self.move_increment = 0
        self.name = "Arm"
    def increment(self):
        self.target += self.move_increment
        if (self.target > self.max):
            self.target = self.max
    def decrement(self):
        self.target -= self.move_increment
        if (self.target < self.min):
            self.target = self.min
class Elbow(Arm):
    def __init__(self):
       super().__init__()
       self.name = "ELBOW"
       self.move_increment = 40
       self.motor0 = Motor(13,self.mode)
       self.motor0.set_mode(self.mode)
       self.motor0.update()
       self.target = self.motor0.position
       self.max = 3700
       self.min = 400
    def flip(self):
        super().flip()
        self.target = self.motor0.position
    def update(self):
        self.motor0.set_position(self.target)
        self.telemetry = self.motor0.status()
        self.motor0.set_on(self.on)
        self.motor0.update()

class Shoulder(Arm):
    def __init__(self):
       super().__init__()
       self.name = "SHOULDER"
       self.move_increment = 40
       self.motor0 = Motor(11,self.mode)
       self.motor0.set_mode(self.mode)
       self.motor0.update()
       self.target = self.motor0.position
       self.max = 3165
       self.min = 1150
    def flip(self):
        super().flip()
        self.target = self.motor0.position
    def update(self):
        self.motor0.set_position(self.target)
        self.telemetry = self.motor0.status()
        self.motor0.set_on(self.on)
        self.motor0.update()

class Wrist(Arm):
    def __init__(self):
       super().__init__()
       self.name = "WRIST"
       self.move_increment = 60
       self.motor0 = Motor(14,self.mode)
       self.motor0.set_mode(self.mode)
       self.motor0.update()
       self.target = self.motor0.position
       self.max = 2572
       self.min = 431
    def flip(self):
        super().flip()
        self.target = self.motor0.position
    def update(self):
        self.motor0.set_position(self.target)
        self.telemetry = self.motor0.status()
        self.motor0.set_on(self.on)
        self.motor0.update()

class Turret(Subsystem):
    def __init__(self):
        super().__init__()
        self.mode = Modes.VELOCITY
        self.move_increment = 8
        self.name = "Turret"
        self.motor0 = Motor(10,self.mode)
        self.motor0.set_mode(self.mode)
    def increment(self):
        self.target += self.move_increment
    def decrement(self):
        self.target -= self.move_increment
    def update(self):
        self.motor0.set_velocity(self.target)
        self.telemetry = self.motor0.status()
        if not self.on:
            self.target = 0
        self.motor0.update()

       

