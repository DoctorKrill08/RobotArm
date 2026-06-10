from enum import Enum
import math
from motor import *
from timer import *

class Subsystem():
    def __init__(self):
        self.state = "N/A"
        self.on = True
        self.telemetry = "N/A"
        self.name = "Subsystem"
        self.target = 0
        self.motor0 = None
        self.mode = Modes.POSITION
        self.max = 4095
        self.min = 0
    def increment(self):
        self.set_target(self.target + self.move_increment)
    def decrement(self):
        self.set_target(self.target - self.move_increment)
    def flip(self):
        self.on = not self.on
    def read(self):
        self.telemetry = f"On: {self.on}\nState: {self.state}\n{Motor.empty_status_with_target(self.mode,self.target)}"

class ClawStates(Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"

class Claw(Subsystem):
    #Open = min
    #Closed = max
    OPEN_AMP = 200
    CLOSE_AMP = 80

    def __init__(self):
        super().__init__()
        self.state = ClawStates.OPEN
        self.mode = Modes.CURRENT_BASED_POSITION
        self.min = 1100
        self.max = 2500
        self.target = self.min
        self.name = "CLAW"
        self.motor0 = Motor(15,self.mode)
        self.motor0.read()
    def set_target(self,target):
        self.target = target
        if (self.target > self.max):
            self.target = self.max
        if (self.target < self.min):
            self.target = self.min
        self.motor0.set_position(target)
    def set_state(self,state):
        self.state = state
        if (state == ClawStates.OPEN):
            self.set_target(self.min)
            self.motor0.set_current(self.OPEN_AMP)
        if (state == ClawStates.CLOSE):
            self.set_target(self.max)
            self.motor0.set_current(self.CLOSE_AMP)
    def flip_claw_state(self):
        if (self.state == ClawStates.OPEN):
            self.state = ClawStates.CLOSE
            self.set_target(self.max)
            self.motor0.set_current(self.CLOSE_AMP)
        else:
            self.state = ClawStates.OPEN
            self.set_target(self.min)
            self.motor0.set_current(self.OPEN_AMP)
    def read(self):
        super().read()
        self.telemetry = f"{self.telemetry}\n Target Amperage: {self.motor0.target_amp}"

class Arm(Subsystem):
    length = 0
    def __init__(self):
        super().__init__()
        self.move_increment = 0
        self.name = "Arm"
    def set_target(self,target):
        if (self.target == target):
            return
        self.target = target
        if (self.target > self.max):
            self.target = self.max
        if (self.target < self.min):
            self.target = self.min
        self.motor0.set_position(target)
    def read(self):
        super().read()
        self.telemetry = f"{self.telemetry}\n Angle: {self.motor0.angle}"
    def flip(self):
        super().flip()
        self.target = self.motor0.position
        self.motor0.set_on(self.on)

class Elbow(Arm):
    length = 9 #inches
    def __init__(self):
       super().__init__()
       self.name = "ELBOW"
       self.move_increment = 40
       self.motor0 = Motor(13,self.mode)
       self.motor0.set_mode(self.mode)
       self.motor0.read()
       self.target = self.motor0.position
       self.max = 3700
       self.min = 400
       self.angle = 0
    def set_angle(self,angle):
        if abs(angle - self.angle) < 0.3:
            return
        self.angle = angle
        self.set_target((angle + 180) / Motor.POS_TO_ANGLE)
    def read(self):
        self.telemetry = self.motor0.status()
        self.motor0.read()
         #special angle calculations for elbow (degrees)
        self.angle =self.motor0.angle - 180
        self.telemetry = f"{self.telemetry}\nAdjusted Angle: {self.angle}"

class Shoulder(Arm):
    length = 10 #inches
    def __init__(self):
       super().__init__()
       self.name = "SHOULDER"
       self.move_increment = 40
       self.motor0 = Motor(11,self.mode)
       self.motor0.set_mode(self.mode)
       self.motor0.read()
       self.target = self.motor0.position
       self.max = 3165
       self.min = 1150
       self.angle = 0
    def set_angle(self,angle):
        if abs(angle - self.angle) < 0.5:
            return
        self.angle = angle
        self.set_target(((angle - 280) * -1) / Motor.POS_TO_ANGLE)
    def read(self):
        self.telemetry = self.motor0.status()
        self.motor0.read()
        #special angle calculations for shoulder (degrees)
        self.angle =(-1 * self.motor0.angle) + 280
        self.telemetry = f"{self.telemetry}\nAdjusted Angle: {self.angle}"
        

class Wrist(Arm):
    STRAIGHT_POS = 2500
    SIDE_POS = 1450
    def __init__(self):
       super().__init__()
       self.name = "WRIST"
       self.move_increment = 60
       self.motor0 = Motor(14,self.mode)
       self.motor0.set_mode(self.mode)
       self.motor0.read()
       self.target = self.motor0.position
       self.max = 2572
       self.min = 431
    def rotate(self):
        if (self.target == self.STRAIGHT_POS):
            self.set_target(self.SIDE_POS)
        else:
            self.set_target(self.STRAIGHT_POS)
    def read(self):
        self.telemetry = self.motor0.status()
        self.motor0.read()

class Turret(Subsystem):
    MODE = Modes.VELOCITY
    def __init__(self):
        super().__init__()
        self.mode = Turret.MODE
        self.move_increment = 8
        self.name = "Turret"
        self.motor0 = Motor(10,self.mode)
        self.motor0.set_mode(self.mode)

        #Psuedo positional control stuff
        self.target_angle = 0
        self.current_angle = 0
        self.done_tracking = False
        self.tracking = False
        self.stopwatch = Stopwatch()

    #Used in pair with camera vision, technically can work with anything that can tell it where to rotate to relative to its current position
    #returns boolean if it thinks the target is reached
    def rotate_to(self,target_angle):
        print("Real target angle", target_angle)
        #Within 5 degrees, probably talking about the same object
        DEGREE_THRESHOLD = 5    
        #target angle changed significantly (camera measured) or not already tracking -> start a new tracking prosses
        if (abs(target_angle) - DEGREE_THRESHOLD < abs(self.target_angle) and abs(target_angle + DEGREE_THRESHOLD) > abs(self.target_angle) or self.tracking == False):
            self.target_angle = target_angle
            #Whenever the target angle changes, the current angle is reset to 0. This is to mitigate problems with low framerate camera inputs
            self.current_angle = 0
            self.stopwatch.go()
            self.tracking = True
            self.done_tracking = False
        velocity = self.target
        delta_angle = velocity * self.stopwatch.time_passed_seconds()
        self.current_angle += delta_angle
        print(f"Velocity: {self.target}\n current angle: {self.current_angle}\n target angle: {self.target_angle} \n delta_angle: {delta_angle}\n delta time: {self.stopwatch.time_passed_seconds()}")
        #camera error: left = -, right = + but turret - is right, + is left
        P = -10
        angle_error = target_angle - self.current_angle
        ticks_error = angle_error * Motor.POS_TO_ANGLE
        #Estimated within 5 degrees? Stop moving, signal back the target is reached
        if (abs(angle_error) < DEGREE_THRESHOLD):
            self.set_target(0)
            self.stopwatch.stop()
            self.done_tracking = True
            return
        self.stopwatch.go()
        #Velocity is in ticks per sec
        self.set_target(P * ticks_error)
        self.done_tracking = False
    def set_target(self,target):
        if (abs(target) < 1):
            target = 0
            self.target_angle = 0
            self.target = 0
        self.target = target
        self.motor0.set_velocity(target)
    def flip(self):
        super().flip()
        self.target = 0
        self.motor0.set_on(self.on)
        self.motor0.set_mode(Turret.MODE)
    def read(self):
        self.telemetry = self.motor0.status()
        if not self.on:
            self.target = 0
        self.motor0.read()

       

