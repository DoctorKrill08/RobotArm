from ArmInterface import Interface
from Robot import Robot
from Controller import XboxController



Running = True
robot = Robot()
interface = Interface()
#controller = XboxController()
while True:
    interface.update()
    #print(controller.read())
    