from Subsystems import *
import atexit
class Robot:
    claw = None
    elbow = None
    turret = None
    shoulder = None
    wrist = None
    on = True
    telemetry = ""

    inverse_kinematics = False
    x = 0
    y = 0
    goal_x = 0
    goal_y = 0
    heading = 0

    min_y = -2.2

    shoulder_angle = 0
    elbow_angle = 0

    goal_increment = 1

    joystick_sensitivity = 1

    prev_rb = False

    def status():
        return f"x: {Robot.x}\ny: {Robot.y}\ngoal x: {Robot.goal_x}\ngoal y: {Robot.goal_y}\nshoulder angle: {Robot.shoulder_angle}\nelbow angle: {Robot.elbow_angle}"


    def calculateKinematics():
        Robot.x = Shoulder.length * math.cos(math.radians(Robot.shoulder.angle)) + Elbow.length * math.cos(math.radians(Robot.shoulder.angle + Robot.elbow.angle))
        Robot.y = Shoulder.length * math.sin(math.radians(Robot.shoulder.angle)) + Elbow.length * math.sin(math.radians(Robot.shoulder.angle + Robot.elbow.angle))

    
    #returns elbow angle in rads
    def calculate_elbow():
        inner = ((Robot.goal_x ** 2) + (Robot.goal_y ** 2) - (Shoulder.length ** 2) - (Elbow.length ** 2)) / (2 * Shoulder.length * Elbow.length)
        if (inner > 1):
            inner = 1
        elif (inner < -1):
            inner = -1
        return math.acos(inner)
        #requires elbow angle -> rads
    def calculate_shoulder(q2):
        q1 = math.atan2(Robot.goal_y , Robot.goal_x) - math.atan2((Elbow.length * math.sin(q2)),(Shoulder.length + (Elbow.length * math.cos(q2))))
        if (q1 > 1):
            return 1
        if (q1 < -1):
            return -1
        return q1
    def set_goal_x(target):
        if (abs(Robot.goal_x - target) < 0.2):
            return
        r = math.sqrt((target **2) + (Robot.goal_y **2))
        if r > Shoulder.length + Elbow.length:
            r = Shoulder.length + Elbow.length
        if r < Shoulder.length - Elbow.length:
            r = Shoulder.length - Elbow.length
        if (abs(target) > r):
            target = r * (target / abs(target))
            Robot.goal_y = 0
            Robot.goal_x = target
            return
        Robot.goal_x = target
        theta = math.atan2(Robot.goal_y,Robot.goal_x)
        Robot.goal_y = r * math.sin(theta)
        if (Robot.goal_y < Robot.min_y):
           Robot.goal_y = Robot.min_y
    def set_goal_y(target):
        if (abs(Robot.goal_y - target) < 0.2):
            return
        r = math.sqrt((target **2) + (Robot.goal_y **2))
        if r > Shoulder.length + Elbow.length:
            r = Shoulder.length + Elbow.length
        if r < Shoulder.length - Elbow.length:
            r = Shoulder.length - Elbow.length
        if (abs(target) > r):
            target = r * (target / abs(target))
            Robot.goal_y = target
            Robot.goal_x = 0
            return
        Robot.goal_y = target
        theta = math.atan2(Robot.goal_y,Robot.goal_x)
        if (Robot.goal_y < Robot.min_y):
           Robot.goal_y = Robot.min_y
        Robot.goal_x = r * math.cos(theta)
    def x_up():
        Robot.set_goal_x(Robot.goal_x + Robot.goal_increment)
    def x_down():
        Robot.set_goal_x(Robot.goal_x - Robot.goal_increment)
    def y_up():
        Robot.set_goal_y(Robot.goal_y + Robot.goal_increment)
    def y_down():
        Robot.set_goal_y(Robot.goal_y - Robot.goal_increment)
    
    def control(lx,ly,rx,rb):
        if (not rb):
            Robot.prev_rb = False
        if (rb and not Robot.prev_rb):
            Robot.prev_rb = True
            Robot.claw.flip_claw_state()
        if (not Robot.inverse_kinematics):
            return
        Robot.set_goal_y(Robot.goal_y + (lx * Robot.joystick_sensitivity))
        Robot.set_goal_x(Robot.goal_x + (ly * Robot.joystick_sensitivity))
        Robot.turret.set_target(rx * 50)
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
        Robot.calculateKinematics()
        
        #Unfortunately inverse kinematics gives 2 angles so more work yay!!!

        q2a = Robot.calculate_elbow()
        q2b = - q2a

        q1a = Robot.calculate_shoulder(q2a)
        q1b = Robot.calculate_shoulder(q2b)

        #find closest angle to determine which pair of angles to use
        current_q1 = math.radians(Robot.shoulder.angle)
        current_q2 = math.radians(Robot.elbow.angle)

        dist_up = abs(q1a - current_q1) + abs(q2a - current_q2)
        dist_down = abs(q1a - current_q1) + abs(q2b - current_q2)

        if dist_up < dist_down:
            Robot.elbow_angle = math.degrees(q2a)
            Robot.shoulder_angle = math.degrees(q1a)
        else:
            Robot.elbow_angle = math.degrees(q2b)
            Robot.shoulder_angle = math.degrees(q1b)

        if (Robot.inverse_kinematics == False):
            Robot.goal_x = Robot.x
            Robot.goal_y = Robot.y
        else:
         #   Robot.shoulder.set_angle(Robot.shoulder_angle)
            #Robot.elbow.set_angle(Robot.elbow_angle)
            pass
        

        Robot.telemetry = Robot.status()
    def flip():
        Robot.inverse_kinematics = not Robot.inverse_kinematics
    def turn_off():
        Robot.on = False
    def end():
        Motor.data = 0
        for id in Motor.all_motors:
            Motor.end_motor(id)
        Motor.all_motors.clear()
        Motor.close_port()