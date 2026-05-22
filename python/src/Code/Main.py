from ArmInterface import Interface
from Robot import Robot
from Controller import XboxController

Running = True
robot = Robot()





interface = Interface()
xbox_controller = XboxController()
while Robot.on:
    interface.update()
    robot.update()
    Robot.control(xbox_controller.RightJoystickY,xbox_controller.LeftJoystickY,xbox_controller.RightJoystickX,xbox_controller.RightBumper)
