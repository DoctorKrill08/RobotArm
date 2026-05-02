from Subsystems.Claw import Claw
class Robot:
    claw = None
    def __init__(self):
        Robot.claw = Claw()