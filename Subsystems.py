from enum import Enum
from dynamixel_sdk import *
import math
class Motor():
    TORQUE_ADDRESS = 64
    TARGET_POSITION_ADDRESS = 116
    AMPERAGE_ADDRESS = 126
    VOLTAGE_ADDRESS = 130
    def __init__(self,port):
        self.max_power = 0
        self.max_amperage = 0
        self.target_position = 0
        self.amperage = 0
        self.voltage = 0
        self.power = 0
        self.portHandler = PortHandler(port)
        self.packetHandler = PacketHandler(2.0)
        self.dxl_id = 1
        self.data = 1
        self.comm_result, self.error = self.packetHandler.write1ByteTxRx(self.portHandler, self.dxl_id, Motor.TORQUE_ADDRESS, self.data)
        if self.comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(self.comm_result))
        elif self.error != 0:
            print("%s" % self.packetHandler.getRxPacketError(self.error))
        else:
            print("Dynamixel has been successfully connected")
    def set_position(self,target):
        self.target_position = target
        self.comm_result, self.error = self.packetHandler.write4ByteTxRx(self.portHandler, self.dxl_id, Motor.TARGET_POSITION_ADDRESS, self.target_position)
    def update(self):
        self.position, self.comm_result, self.error = self.packetHandler.read4ByteTxRx(self.portHandler, self.dxl_id, self.present_position_address)
        self.amperage = self.packetHandler.read2ByteTxRx(self.portHandler, self.dxl_id, Motor.AMPERAGE_ADDRESS)
        self.voltage = self.packetHandler.read2ByteTxRx(self.portHandler, self.dxl_id, Motor.VOLTAGE_ADDRESS)
    def status(self):
        return f"Position: {self.position}\nAmperage: {self.amperage}\nPower: {self.power}\nTargetPosition: {self.target_position}"
    @staticmethod
    def empty_status_with_target_pos(target_pos):
        return f"Position: N/A\nAmperage: N/A\nPower: N/A\nTarget Position: {round(target_pos, 4)}"
    @staticmethod
    def status():
        return Motor.empty_status_with_target_pos("N/A")

    
class Subsystem():
    def __init__(self):
        self.state = "N/A"
        self.on = False
        self.telemetry = "N/A"
        self.name = "Subsystem"
        self.target_pos = 0
    def flip(self):
        self.on = not self.on
    def update(self):
        self.telemetry = f"On: {self.on}\nState: {self.state}\n{Motor.empty_status_with_target_pos(self.target_pos)}"

class ClawStates(Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"

class Claw(Subsystem):
    CLOSE_POS = 0.5
    OPEN_POS = 0.7
    def __init__(self):
        super().__init__()
        self.state = ClawStates.OPEN
        self.target_pos = self.OPEN_POS
        self.name = "Claw"
    def flip_claw_state(self):
        if (self.state == ClawStates.OPEN):
            self.state = ClawStates.CLOSE
            self.target_pos = self.CLOSE_POS
        else:
            self.state = ClawStates.OPEN
            self.target_pos = self.OPEN_POS

class Arm(Subsystem):
    def __init__(self):
        super().__init__()
        self.move_increment = 0
        self.name = "Arm"
    def increment(self):
        self.target_pos += self.move_increment
    def decrement(self):
        self.target_pos -= self.move_increment
class Elbow(Arm):
    def __init__(self):
       super().__init__()
       self.name = "ELBOW"
       self.move_increment = .0001
       

