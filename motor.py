from enum import Enum
class Modes(Enum):
    VELOCITY = "VELOCITY",
    POSITION = "POSITION" 
    CURRENT = "CURRENT"
    CURRENT_BASED_POSITION = "CURRENT_BASED_POSITION"

class Motor():
    dynamixel_connected = True
    all_motors = []
    port_handler = None;
    packet_handler = None
    group_bulk_read = None
    group_bulk_write = None
    
    @staticmethod
    def initiate_all_motors():
        Motor.all_motors.clear()
        if (not Motor.dynamixel_connected):
            return
        try:
            Motor.port_handler = PortHandler("COM3")
            Motor.port_handler.openPort()
            Motor.packet_handler = PacketHandler(2.0)
            Motor.group_bulk_read = GroupBulkRead(Motor.port_handler, Motor.packet_handler)
            Motor.group_bulk_write = GroupBulkRead(Motor.port_handler, Motor.packet_handler)
            Motor.port_handler.setBaudRate(57600)
        except:
            Motor.dynamixel_connected = False

    torque_on_address = 64

    @staticmethod
    def end_motor(id):
        Motor.packet_handler.write1ByteTxRx(Motor.port_handler, id, Motor.torque_on_address, 0)

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
        self.target_amp = 0
        self.target = 0
        self.amperage = 0
        self.voltage = 0
        self.angle = 0
        self.power = 0
        self.dxl_id = id
        self.data = 1
        self.set_mode(mode)
        if (Motor.dynamixel_connected == False):
            return
        self.comm_result, self.error = Motor.packet_handler.write1ByteTxRx(Motor.port_handler, self.dxl_id, Motor.TORQUE_ADDRESS, self.data)
        
        if self.comm_result != COMM_SUCCESS:
            print("%s" % Motor.packet_handler.getTxRxResult(self.comm_result))
        elif self.error != 0:
            print("ERROR")
            print("%s" % Motor.packet_handler.getRxPacketError(self.error))
        else:
            print("Dynamixel has been successfully connected")
    def set_current(self,target):
        target = round(target)
        if target > 400:
            target = 400
        if (target == self.target):
            return
        self.target_amp = target
        self.comm_result, self.error = Motor.packet_handler.write2ByteTxRx(Motor.port_handler, self.dxl_id, Motor.TARGET_CURRENT_ADDRESS, target)
    def set_position(self,target):
        target = round(target)
        if (target == self.target):
            return
        self.target = target
        if (Motor.dynamixel_connected == False):
            return
        self.comm_result, self.error = Motor.packet_handler.write4ByteTxRx(Motor.port_handler, self.dxl_id, Motor.TARGET_POSITION_ADDRESS, self.target)
    def set_velocity(self,target):
        target = round(target)
        if (target == self.target):
            return
        self.target = target
        if (Motor.dynamixel_connected == False):
            return
        self.comm_result, self.error = Motor.packet_handler.write4ByteTxRx(Motor.port_handler, self.dxl_id, Motor.TARGET_VELOCITY_ADDRESS, self.target)
    def set_mode(self,mode):
        self.mode = mode
        if (mode == self.mode):
            return
        if (Motor.dynamixel_connected == False):
            return
        self.comm_result, self.error = Motor.packet_handler.write1ByteTxRx(Motor.port_handler, self.dxl_id, Motor.OPERATING_MODE_ADDRESS, Motor.mode_to_id(mode))
    def set_on(self,on):
        #convert boolean to binary
        data = 0
        if on:
            data = 1
        if (Motor.dynamixel_connected == False):
            return
        Motor.packet_handler.write1ByteTxRx(Motor.port_handler, self.dxl_id, Motor.TORQUE_ADDRESS, data)
    def read(self):
        if (Motor.dynamixel_connected == False):
            return
        if (self.mode == Modes.POSITION or self.mode == Modes.CURRENT_BASED_POSITION):
            self.position, self.comm_result, self.error = Motor.packet_handler.read4ByteTxRx(Motor.port_handler, self.dxl_id, Motor.POSITION_ADDRESS)
            self.angle = self.position * 0.088
        elif (self.mode == Modes.VELOCITY):
            self.velocity,_, _ = Motor.packet_handler.read4ByteTxRx(Motor.port_handler, self.dxl_id, Motor.VELOCITY_ADDRESS)
    def status(self):
        return f"Target {self.mode.value}: {self.target}"
    @staticmethod
    def empty_status_with_target(mode,target):
        return f"Mode: {mode.value} Present: N/A\nAmperage: N/A\nTarget: {round(target, 4)}"

Motor.dynamixel_connected = True
try:
    from dynamixel_sdk import *
except:
    print("Dynamixel Disconnected")
    Motor.dynamixel_connected = False