from ArmInterface import Interface
from Robot import Robot
from Controller import XboxController
import time
robot = Robot()
interface = Interface()
xbox_controller = XboxController()

TARGET_HZ = 60
DT = 1 / TARGET_HZ

while Robot.on:
    start = time.perf_counter()

    interface.update()
    robot.update()

    Robot.control(
        xbox_controller.RightJoystickY,
        xbox_controller.LeftJoystickY,
        xbox_controller.RightJoystickX,
        xbox_controller.RightBumper
    )

    elapsed = time.perf_counter() - start
    sleep_time = DT - elapsed

    if sleep_time > 0:
        time.sleep(sleep_time)