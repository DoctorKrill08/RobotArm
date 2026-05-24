from Subsystems import *
import atexit
from BlobCountor import Camera
from Timer import Timer

def lerp(start,goal,time_passed,total_time):
        x = time_passed / total_time
        if (x > 1):
            x = 1
        if (x < 0):
            x = 0
        y = start + (x * (goal - start))
        return y

class AutoState(Enum):
    SCOUTING = "SCOUTING"
    REACHING = "REACHING"
    GRAB = "GRAB"
    RESTING = "RESTING"
class Robot:
    claw = None
    elbow = None
    turret = None
    shoulder = None
    wrist = None
    on = True
    telemetry = ""

    auto_state = AutoState.RESTING

    inverse_kinematics = False
    autonomous = False

    SCOUTING_X = 3
    SCOUTING_Y = 5

    REACH_X = 18
    REACH_Y = 2.5


    x = 0
    y = 0
    goal_x = 0
    goal_y = 0
    heading = 0

    FLOOR_Y = 0.5
    BASE_X = 5.5
    BASE_Y = 5

    shoulder_angle = 0
    elbow_angle = 0

    goal_increment = 1

    JOYSTICK_SENSITIVITY = 0.4

    TURRET_SENSITIVITY = 100

    READ_RATE = 20

    CAMERA_WITHIN_ERROR = 5
    SCOUT_TIME = 4
    REACH_TIME = 4
    GRAB_TIME = 2

    camera_error = 0

    auto_state_timer = Timer()



    def status():
        return f"Auto State: {Robot.auto_state.value}\n Camera Error: {Robot.camera_error}\n Auto Time Passed: {Robot.auto_state_timer.time_passed_seconds()}\n x: {Robot.x}\ny: {Robot.y}\ngoal x: {Robot.goal_x}\ngoal y: {Robot.goal_y}\nshoulder angle: {Robot.shoulder_angle}\nelbow angle: {Robot.elbow_angle}\n{Camera.status()}"


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
        if y < Robot.FLOOR_Y:
            y = Robot.FLOOR_Y
        if abs(x) < Robot.BASE_X:
            if (y < Robot.BASE_Y):
                y = Robot.BASE_Y
        if (abs(x - Robot.goal_x) < 0.1):
            return
        if (abs(y - Robot.goal_y) < 0.1):
            return

        r = math.hypot(x,y)

        r_max = Shoulder.length + Elbow.length
        r_min = abs(Shoulder.length - Elbow.length)

        if r < 1e-6:
            return

        if r > r_max:
            scale = r_max / r
            x *= scale
            y *= scale

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
    
    def control(right_stick_y,left_stick_y,right_stick_x,rb_was_pressed,lb_was_pressed):
        if (rb_was_pressed):
            Robot.prev_rb = True
            Robot.claw.flip_claw_state()
        if (lb_was_pressed):
            Robot.prev_lb = True
            Robot.wrist.rotate()
        if (not Robot.inverse_kinematics):
            return
        Robot.set_goal(Robot.goal_x + (left_stick_y * Robot.JOYSTICK_SENSITIVITY),Robot.goal_y + (right_stick_y * Robot.JOYSTICK_SENSITIVITY))
        Robot.turret.set_target((right_stick_x ** 3) * -Robot.TURRET_SENSITIVITY)
    
    def __init__(self):
        Motor.all_motors.clear()
        Robot.claw = Claw()
        Robot.elbow = Elbow()
        Robot.turret = Turret()
        Robot.shoulder = Shoulder()
        Robot.wrist = Wrist()
    
    def read_subsystems():
        Robot.claw.read()
        Robot.elbow.read()
        Robot.turret.read()
        Robot.shoulder.read()
        Robot.wrist.read()
    def set_auto_state(state):
        if state == Robot.auto_state:
            return
        Robot.auto_state = state
        Robot.auto_state_timer.go()

    def auto_update():
        Robot.wrist.set_target(Wrist.STRAIGHT_POS)
        if (Robot.auto_state == AutoState.RESTING):
            Robot.set_goal(Robot.SCOUTING_X,Robot.SCOUTING_Y)
            return
        if (Robot.auto_state == AutoState.SCOUTING):
            Camera.update()
            Robot.claw.set_state(ClawStates.OPEN)
            Robot.set_goal(Robot.SCOUTING_X,Robot.SCOUTING_Y)
            Robot.camera_error = 0
            if (Robot.auto_state_timer.time_passed_seconds() < Robot.SCOUT_TIME):
                return
            if Camera.visible:
                error = Camera.CENTER_X - Camera.target_x
                if (Robot.camera_error == error):
                    return
                Robot.camera_error = error
                if (abs(Robot.camera_error) < Robot.CAMERA_WITHIN_ERROR):
                    Robot.set_auto_state(AutoState.REACHING)
                    Camera.end()
            Robot.rotate_to(Robot.camera_error)
            return
        if (Robot.auto_state == AutoState.REACHING):
            Robot.set_goal(lerp(Robot.SCOUTING_X,Robot.REACH_X,Robot.auto_state_timer.time_passed_seconds(),Robot.REACH_TIME),
                           lerp(Robot.SCOUTING_Y,Robot.REACH_Y,Robot.auto_state_timer.time_passed_seconds(),Robot.REACH_TIME))
            if (Robot.auto_state_timer.time_passed_seconds() > Robot.REACH_TIME):
                Robot.set_auto_state(AutoState.GRAB)
            return
        if (Robot.auto_state == AutoState.GRAB):
            Robot.claw.set_state(ClawStates.CLOSE)
            if (Robot.auto_state_timer.time_passed_seconds() > Robot.GRAB_TIME):
                Robot.set_auto_state(AutoState.RESTING)
                Robot.autonomous = False
            return

    def rotate_to(error):
        P = -0.3
        Robot.turret.set_target(error * P)

    read_index = 0
    def update(self):
        if (Robot.autonomous):
            Robot.auto_update()
        if (not Robot.on):
            Robot.end()
            return
        Robot.read_index += 1
        if (Robot.read_index == Robot.READ_RATE):
            Robot.read_index = 0
            Robot.read_subsystems()
        
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
    
    def flip_kinematics():
        Robot.inverse_kinematics = not Robot.inverse_kinematics
    
    def flip_autonomous():
        Robot.autonomous = not Robot.autonomous
        if (Robot.autonomous):
            Camera.start()
            Robot.set_auto_state(AutoState.SCOUTING)
            Robot.inverse_kinematics = True
        else:
            Camera.end()
            Robot.set_auto_state(AutoState.RESTING)
    
    def turn_off():
        Robot.on = False
    
    def end():
        Motor.data = 0
        for id in Motor.all_motors:
            Motor.end_motor(id)
        Motor.all_motors.clear()
        Motor.close_port()
        Camera.end()