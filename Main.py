from ArmInterface import Interface
from Robot import Robot



Running = True
robot = Robot()
interface = Interface()
while True:
    interface.update()
    robot.update()
    