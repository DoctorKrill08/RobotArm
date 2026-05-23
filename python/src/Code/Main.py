from ArmInterface import Interface
from Robot import Robot
from Controller import XboxController
import time
robot = Robot()
interface = Interface()
xbox_controller = XboxController()

TARGET_HZ = 60
DT = 1 / TARGET_HZ

INTERFACE_FRAME_RATE = 18
update_interface_index = 0

while Robot.on:
    start = time.perf_counter()
    update_interface_index += 1
    if (update_interface_index == INTERFACE_FRAME_RATE):
        interface.update()
        Robot.update_subsystems()
        update_interface_index = 0
    robot.update()

    Robot.control(
        xbox_controller.RightJoystickY,
        xbox_controller.LeftJoystickY,
        xbox_controller.RightJoystickX,
        xbox_controller.rb_was_pressed(),
        xbox_controller.lb_was_pressed()
    )

    elapsed = time.perf_counter() - start
    sleep_time = DT - elapsed

    if sleep_time > 0:
        time.sleep(sleep_time)