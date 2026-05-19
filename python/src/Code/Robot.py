from Subsystems import *
import atexit
class Robot:
    claw = None
    elbow = None
    turret = None
    shoulder = None
    wrist = None
    on = True
    def __init__(self):
        Motor.all_motors.clear()
        Robot.claw = Claw()
        Robot.elbow = Elbow()
        Robot.turret = Turret()
        Robot.shoulder = Shoulder()
        Robot.wrist = Wrist()
    def update(self):
        if (not Robot.on):
            Robot.end()
            return
        Robot.claw.update()
        Robot.elbow.update()
        Robot.turret.update()
        Robot.shoulder.update()
        Robot.wrist.update()
    def flip():
        Robot.on = not Robot.on
    def end():
        Motor.data = 0
        for id in Motor.all_motors:
            Motor.end_motor(id)
        Motor.all_motors.clear()
        Motor.close_port()