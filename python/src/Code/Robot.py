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

    joystick_sensitivity = 0.5

    turret_sensitivity = 100

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
        return q1
    def set_goal(x,y):
        if y < Robot.min_y:
            y = Robot.min_y

        r = math.hypot(x,y)

        r_max = Shoulder.length + Elbow.length
        r_min = abs(Shoulder.length - Elbow.length)

    # prevent divide by zero
        if r < 1e-6:
            return

    # outside max reach
        if r > r_max:
            scale = r_max / r
            x *= scale
            y *= scale

    # inside minimum reach hole
        elif r < r_min:
            scale = r_min / r
            x *= scale
            y *= scale

        Robot.goal_x = x
        Robot.goal_y = y

    def x_up():
        Robot.set_goal(Robot.goal_x + Robot.goal_increment,Robot.goal_y)
    def x_down():
        Robot.set_goal(Robot.goal_x - Robot.goal_increment,Robot.goal_y)
    def y_up():
        Robot.set_goal(Robot.goal_x,Robot.goal_y + Robot.goal_increment)
    def y_down():
        Robot.set_goal(Robot.goal_x, Robot.goal_y - Robot.goal_increment)
    
    def control(ry,ly,rx,rb):
        if (not rb):
            Robot.prev_rb = False
        if (rb and not Robot.prev_rb):
            Robot.prev_rb = True
            Robot.claw.flip_claw_state()
        if (not Robot.inverse_kinematics):
            return
        Robot.set_goal(Robot.goal_x + (ly * Robot.joystick_sensitivity),Robot.goal_y + (ry * Robot.joystick_sensitivity))
        Robot.turret.set_target((rx ** 3) * -Robot.turret_sensitivity)
    def __init__(self):
        Motor.all_motors.clear()
        Robot.claw = Claw()
        Robot.elbow = Elbow()
        Robot.turret = Turret()
        Robot.shoulder = Shoulder()
        Robot.wrist = Wrist()
    read_update_index = 0
    def update(self):
        if (not Robot.on):
            Robot.end()
            return
        self.read_update_index += 1
        if (self.read_update_index == 3):
            Robot.claw.update()
            Robot.elbow.update()
            Robot.turret.update()
            Robot.shoulder.update()
            Robot.wrist.update()
            self.read_update_index = 0

        Robot.calculateKinematics()
        
        q2a = Robot.calculate_elbow()
        q2b = - q2a

        q1a = Robot.calculate_shoulder(q2a)
        q1b = Robot.calculate_shoulder(q2b)

        if (q1a > q1b):
            Robot.elbow_angle = math.degrees(q2a)
            Robot.shoulder_angle = math.degrees(q1a)
        else:
            Robot.elbow_angle = math.degrees(q2b)
            Robot.shoulder_angle = math.degrees(q1b)

        if (Robot.inverse_kinematics == False):
            Robot.goal_x = Robot.x
            Robot.goal_y = Robot.y
        else:
            Robot.shoulder.set_angle(Robot.shoulder_angle)
            Robot.elbow.set_angle(Robot.elbow_angle)
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