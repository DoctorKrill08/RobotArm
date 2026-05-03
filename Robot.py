from Subsystems import *
class Robot:
    claw = None
    elbow = None
    def __init__(self):
        Robot.claw = Claw()
        Robot.elbow = Elbow()
    def update(self):
        Robot.claw.update()
        Robot.elbow.update()