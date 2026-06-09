from arm_interface import Interface
from controller import XboxController
from robot import Robot

import time

Robot.start()
interface = Interface()

gamepad_connected = False

def attempt_connect_controller():
    xbox_controller = None
    gamepad_connected = False
    try:
        xbox_controller = XboxController()
        gamepad_connected = True
    finally:
        pass
    return xbox_controller, gamepad_connected
    
xbox_controller,Robot.controller_connected = attempt_connect_controller()

TARGET_HZ = 60
DT = 1 / TARGET_HZ

INTERFACE_FRAME_RATE = 1
update_interface_index = 0

while Robot.on:
    start = time.perf_counter()
    update_interface_index += 1
    if (update_interface_index == INTERFACE_FRAME_RATE):
        interface.update()
        update_interface_index = 0
    
    Robot.update()

    if (xbox_controller.is_connected() == False):
        Robot.controller_connected = False

    Robot.control(xbox_controller)
    
    elapsed = time.perf_counter() - start
    sleep_time = DT - elapsed

    if sleep_time > 0:
        time.sleep(sleep_time)