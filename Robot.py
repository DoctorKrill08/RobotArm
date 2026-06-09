from subsystems import *
import atexit
from CameraStuff.blob_contour import Camera
from timer import Timer
from motor import *
from subsystems import Subsystem

def truncate(number, decimals=0):
    factor = 10 ** decimals
    return int(number * factor) / factor

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


    telemetry = ""


    auto_state = AutoState.RESTING

    inverse_kinematics = False
    autonomous = False

    SCOUTING_X = 3
    SCOUTING_Y = 5.5

    REACH_X = 18
    REACH_Y = 1.5


    x = 0
    y = 0
    goal_x = 0
    goal_y = 0
    heading = 0

    FLOOR_Y = 1
    BASE_X = 6.5
    BASE_Y = 5

    shoulder_angle = 0
    elbow_angle = 0

    goal_increment = 1

    JOYSTICK_SENSITIVITY = 0.4

    TURRET_SENSITIVITY = 100

    READ_RATE = 60

    CAMERA_WITHIN_ERROR = 3
    SCOUT_LOAD_TIME = 1
    SCOUTING_TIME = 3.5
    REACH_TIME = 2.5
    GRAB_TIME = 1

    camera_error = 0

    auto_state_timer = Timer()

    on = True

    controller_connected = False


    def status():
        return f"Auto State: {Robot.auto_state.value}\n Camera Error: {Robot.camera_error}\n Auto Time Passed: {truncate(Robot.auto_state_timer.time_passed_seconds(),3)}\n x: {Robot.x}\ny: {Robot.y}\ngoal x: {Robot.goal_x}\ngoal y: {Robot.goal_y}\nshoulder angle: {Robot.shoulder_angle}\nelbow angle: {Robot.elbow_angle}\n{Camera.status()}"


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
    
    def control(gamepad):
        if Robot.autonomous and not Robot.auto_state == AutoState.SCOUTING:
            Robot.turret.set_target(0)
        if not Robot.controller_connected:
            return
        rb_was_pressed = gamepad.rb_was_pressed()
        lb_was_pressed = gamepad.lb_was_pressed()
        rt_was_pressed = gamepad.rt_was_pressed()
        y_was_pressed = gamepad.y_was_pressed()
        a_was_pressed = gamepad.a_was_pressed()
        b_was_pressed = gamepad.b_was_pressed()
        x_was_pressed = gamepad.x_was_pressed()


        left_stick_y = gamepad.LeftJoystickY
        right_stick_y = gamepad.RightJoystickY
        right_stick_x = gamepad.RightJoystickX
        
        if (a_was_pressed):
            Robot.flip_autonomous()
        if (x_was_pressed):
            Robot.flip_camera()
        if (rt_was_pressed):
            if (not Robot.auto_state == AutoState.RESTING):
                Robot.set_auto_state(AutoState.RESTING)
            else:
                Robot.autonomous = True
                Robot.set_auto_state(AutoState.REACHING)
        if (b_was_pressed):
            Robot.end()

        if (Robot.autonomous):
            return

        if (rb_was_pressed):
            Robot.claw.flip_claw_state()
        if (lb_was_pressed):
            Robot.wrist.rotate()
        if (y_was_pressed):
            Robot.flip_kinematics()
        if (not Robot.inverse_kinematics):
            return
        deltaLeft = (left_stick_y * Robot.JOYSTICK_SENSITIVITY)
        if (abs(deltaLeft) < 0.05):
            deltaLeft = 0
        deltaRight = (right_stick_y * Robot.JOYSTICK_SENSITIVITY)
        if (abs(deltaRight) < 0.05):
            deltaRight = 0
        Robot.set_goal(Robot.goal_x + deltaLeft,Robot.goal_y + deltaRight)
        Robot.turret.set_target((right_stick_x ** 3) * -Robot.TURRET_SENSITIVITY)
    
    def start():
        Motor.initiate_all_motors()
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
        if state == AutoState.REACHING or state == AutoState.SCOUTING:
            Robot.claw.set_state(ClawStates.OPEN)
        Robot.auto_state = state
        Robot.auto_state_timer.go()

    def auto_update():
        Robot.wrist.set_target(Wrist.STRAIGHT_POS)
        if (Robot.auto_state == AutoState.RESTING):
            Robot.set_goal(Robot.SCOUTING_X,Robot.SCOUTING_Y)
            if (Robot.auto_state_timer.time_passed_seconds() > Robot.GRAB_TIME):
                Robot.autonomous = False
                Camera.destroy_windows()
            return
        if (Robot.auto_state == AutoState.SCOUTING):
            Camera.update()
            Robot.claw.set_state(ClawStates.OPEN)
            Robot.set_goal(Robot.SCOUTING_X,Robot.SCOUTING_Y)
            Robot.camera_error = 0
            if (Robot.auto_state_timer.time_passed_seconds() < Robot.SCOUT_LOAD_TIME):
                return
            if (Robot.auto_state_timer.time_passed_seconds() - Robot.SCOUT_LOAD_TIME > Robot.SCOUTING_TIME):
                Robot.set_auto_state(AutoState.RESTING)
            if Camera.visible:
                error = Camera.CENTER_X - Camera.target_x
                if (Robot.camera_error == error):
                    return
                Robot.camera_error = error
                if (abs(Robot.camera_error) < Robot.CAMERA_WITHIN_ERROR):
                    Robot.set_auto_state(AutoState.REACHING)
                Robot.rotate_to(Robot.camera_error)
            else:
                Robot.turret.set_target(0)
            return
        if (Robot.auto_state == AutoState.REACHING):
            Robot.turret.set_target(0)
            Robot.set_goal(lerp(Robot.SCOUTING_X,Robot.REACH_X,Robot.auto_state_timer.time_passed_seconds(),Robot.REACH_TIME),
                           lerp(Robot.SCOUTING_Y,Robot.REACH_Y,Robot.auto_state_timer.time_passed_seconds(),Robot.REACH_TIME))
            if (Robot.auto_state_timer.time_passed_seconds() > Robot.REACH_TIME):
                Robot.set_auto_state(AutoState.GRAB)
            return
        if (Robot.auto_state == AutoState.GRAB):
            Robot.claw.set_state(ClawStates.CLOSE)
            if (Robot.auto_state_timer.time_passed_seconds() > Robot.GRAB_TIME):
                Robot.set_auto_state(AutoState.RESTING)
            return

    def rotate_to(error):
        P = -0.3
        Robot.turret.set_target(error * P)

    read_index = 0
    def update():
        if (Robot.autonomous):
            Robot.auto_update()
        if (not Robot.on):
            Robot.end()
            return
        Robot.read_index += 1
        if (Robot.read_index >= Robot.READ_RATE and not Robot.autonomous):
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
    def turn_off():
        Robot.on = False
    def flip_autonomous():
        Robot.autonomous = not Robot.autonomous
        if (Robot.autonomous):
            if (not Camera.Ready):
                Camera.start()
            Robot.set_auto_state(AutoState.SCOUTING)
            Robot.inverse_kinematics = True
        else:
            Robot.camera_stop()
            Robot.set_auto_state(AutoState.RESTING)
    def flip_camera():
        if Camera.Ready:
            Camera.end()
        else:
            Camera.start()
    def camera_stop():
        Camera.destroy_windows()

    def end():
        Motor.data = 0
        for id in Motor.all_motors:
            Motor.end_motor(id)
        Motor.all_motors.clear()
        Camera.end()
