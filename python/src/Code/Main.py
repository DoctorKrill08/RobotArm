from ArmInterface import Interface
from Robot import Robot

Running = True
robot = Robot()
interface = Interface()
while Robot.on:
    interface.update()
    robot.update()
