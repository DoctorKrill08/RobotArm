from Subsystems import *
class Robot:
    claw = None
    elbow = None
    turret = None
    def __init__(self):
        Robot.claw = Claw()
        Robot.elbow = Elbow()
        Robot.turret = Turret()
    def update(self):
        Robot.claw.update()
        Robot.elbow.update()
        Robot.turret.update()