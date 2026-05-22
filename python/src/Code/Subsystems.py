from enum import Enum
from dynamixel_sdk import *
import math
class Modes(Enum):
    VELOCITY = "VELOCITY",
    POSITION = "POSITION" 
    CURRENT = "CURRENT"
    CURRENT_BASED_POSITION = "CURRENT_BASED_POSITION"

class Motor():
    all_motors = []
    portHandler = PortHandler("COM3")
    portHandler.openPort()
    packetHandler = PacketHandler(2.0)
    groupBulkWrite = GroupBulkWrite(portHandler, packetHandler)
    groupBulkRead = GroupBulkRead(portHandler, packetHandler)
    portHandler.setBaudRate(1000000)


    torque_on_address = 64

    @staticmethod
    def close_port():
        #Motor.portHandler.closePort()
        pass
    @staticmethod
    def end_motor(id):
        Motor.packetHandler.write1ByteTxRx(Motor.portHandler, id, Motor.torque_on_address, 0)

    POS_TO_ANGLE = 0.088

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
        self.angle = 0
        self.power = 0
        self.dxl_id = id
        self.data = 1
        self.comm_result, self.error = Motor.packetHandler.write1ByteTxRx(Motor.portHandler, self.dxl_id, Motor.TORQUE_ADDRESS, self.data)
        self.set_mode(mode)
        if self.comm_result != COMM_SUCCESS:
            print("%s" % Motor.packetHandler.getTxRxResult(self.comm_result))
        elif self.error != 0:
            print("ERROR")
            print("%s" % Motor.packetHandler.getRxPacketError(self.error))
        else:
            print("Dynamixel has been successfully connected")
    def set_current(self,target):
        target = round(target)
        if target > 400:
            target = 400
        self.max_amperage = target
        self.comm_result, self.error = Motor.packetHandler.write2ByteTxRx(Motor.portHandler, self.dxl_id, Motor.TARGET_CURRENT_ADDRESS, self.max_amperage)
    def set_position(self,target):
        target = round(target)
        self.target = target
        self.comm_result, self.error = Motor.packetHandler.write4ByteTxRx(Motor.portHandler, self.dxl_id, Motor.TARGET_POSITION_ADDRESS, self.target)
    def set_velocity(self,target):
        target = round(target)
        self.target = target
        self.comm_result, self.error = Motor.packetHandler.write4ByteTxRx(Motor.portHandler, self.dxl_id, Motor.TARGET_VELOCITY_ADDRESS, self.target)
    def set_mode(self,mode):
        self.mode = mode
        self.comm_result, self.error = Motor.packetHandler.write1ByteTxRx(Motor.portHandler, self.dxl_id, Motor.OPERATING_MODE_ADDRESS, Motor.mode_to_id(mode))
    def set_on(self,on):
        #convert boolean to binary
        data = 0
        if on:
            data = 1
        Motor.packetHandler.write1ByteTxRx(Motor.portHandler, self.dxl_id, Motor.TORQUE_ADDRESS, data)
    def update(self):
        if (self.mode == Modes.POSITION or self.mode == Modes.CURRENT_BASED_POSITION):
            self.position, self.comm_result, self.error = Motor.packetHandler.read4ByteTxRx(Motor.portHandler, self.dxl_id, Motor.POSITION_ADDRESS)
            self.angle = self.position * 0.088
        elif (self.mode == Modes.VELOCITY):
            self.velocity,_, _ = Motor.packetHandler.read4ByteTxRx(Motor.portHandler, self.dxl_id, Motor.VELOCITY_ADDRESS)
    def status(self):
        return f"Mode: {self.mode.value}\nPosition: {self.position}\nAmperage: {self.amperage}\nVelocity: {self.velocity}\nTarget {self.mode.value}: {self.target}\nAngle: {self.angle}"
    @staticmethod
    def empty_status_with_target(mode,target):
        return f"Mode: {mode.value} Present: N/A\nAmperage: N/A\nTarget: {round(target, 4)}"


class Subsystem():
    def __init__(self):
        self.state = "N/A"
        self.on = True
        self.telemetry = "N/A"
        self.name = "Subsystem"
        self.target = 0
        self.motor0 = None
        self.mode = Modes.POSITION
        self.max = 4095
        self.min = 0
    def increment(self):
        self.set_target(self.target + self.move_increment)
    def decrement(self):
        self.set_target(self.target - self.move_increment)
    def flip(self):
        self.on = not self.on
    def update(self):
        self.telemetry = f"On: {self.on}\nState: {self.state}\n{Motor.empty_status_with_target(self.mode,self.target)}"

class ClawStates(Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"

class Claw(Subsystem):
    KP = 0.045
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
    def set_target(self,target):
        self.target = target
        if (self.target > self.max):
            self.target = self.max
        if (self.target < self.min):
            self.target = self.min
        self.motor0.set_position(target)
    def flip_claw_state(self):
        if (self.state == ClawStates.OPEN):
            self.state = ClawStates.CLOSE
            self.set_target(self.max)
            self.motor0.set_current(400)
        else:
            pos_error = abs(self.target - self.motor0.position)
            self.state = ClawStates.OPEN
            self.set_target(self.min)
            self.motor0.set_current(50)
    def update(self):
        self.telemetry = self.motor0.status()
        self.motor0.set_on(self.on)
        self.motor0.update()

class Arm(Subsystem):
    length = 0
    def __init__(self):
        super().__init__()
        self.move_increment = 0
        self.name = "Arm"
    def set_target(self,target):
        self.target = target
        if (self.target > self.max):
            self.target = self.max
        if (self.target < self.min):
            self.target = self.min
        self.motor0.set_position(target)
    def flip(self):
        super().flip()
        self.target = self.motor0.position
        self.motor0.set_on(self.on)

class Elbow(Arm):
    length = 9 #inches
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
       self.angle = 0
    def set_angle(self,angle):
        if abs(angle - self.angle) < 0.3:
            return
        self.angle = angle
        self.set_target((angle + 180) / Motor.POS_TO_ANGLE)
    def update(self):
        self.telemetry = self.motor0.status()
        self.motor0.update()
         #special angle calculations for elbow (degrees)
        self.angle =self.motor0.angle - 180
        self.telemetry = f"{self.telemetry}\nAdjusted Angle: {self.angle}"

class Shoulder(Arm):
    length = 10 #inches
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
       self.angle = 0
    def set_angle(self,angle):
        if abs(angle - self.angle) < 1:
            return
        self.angle = angle
        self.set_target(((angle - 280) * -1) / Motor.POS_TO_ANGLE)
    def update(self):
        self.telemetry = self.motor0.status()
        self.motor0.update()
        #special angle calculations for shoulder (degrees)
        self.angle =(-1 * self.motor0.angle) + 280
        self.telemetry = f"{self.telemetry}\nAdjusted Angle: {self.angle}"
        

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
    def update(self):
        self.telemetry = self.motor0.status()
        self.motor0.update()

class Turret(Subsystem):
    def __init__(self):
        super().__init__()
        self.mode = Modes.VELOCITY
        self.move_increment = 8
        self.name = "Turret"
        self.motor0 = Motor(10,self.mode)
        self.motor0.set_mode(self.mode)
    def set_target(self,target):
        if (abs(target) < 2):
            if (self.motor0.velocity == 0):
                return
            else:
                target = 0
        self.target = target
        self.motor0.set_velocity(target)
    def flip(self):
        super().flip()
        self.target = 0
        self.motor0.set_on(self.on)
    def update(self):
        self.telemetry = self.motor0.status()
        if not self.on:
            self.target = 0
        self.motor0.update()

       

