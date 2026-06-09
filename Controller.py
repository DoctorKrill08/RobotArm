from inputs import get_gamepad
import math
import threading

class XboxController(object):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self):

        self.LeftJoystickY = 0
        self.LeftJoystickX = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0
        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.LeftBumper = 0
        self.RightBumper = 0
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftThumb = 0
        self.RightThumb = 0
        self.Back = 0
        self.Start = 0
        self.LeftDPad = 0
        self.RightDPad = 0
        self.UpDPad = 0
        self.DownDPad = 0

        self.prevLeftTrigger = 0
        self.prevRightTrigger = 0
        self.prevLeftBumper = 0
        self.prevRightBumper = 0
        self.prevA = 0
        self.prevX = 0
        self.prevY = 0
        self.prevB = 0
        self.prevBack = 0
        self.prevStart = 0
        self.prevLeftDPad = 0
        self.prevRightDPad = 0
        self.prevUpDPad = 0
        self.prevDownDPad = 0

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def rb_was_pressed(self):
        result = self.RightBumper and not self.prevRightBumper
        if (result):
            self.prevRightBumper = self.RightBumper
        return result
    def lb_was_pressed(self):
        result = self.LeftBumper and not self.prevLeftBumper
        if (result):
            self.prevLeftBumper = self.LeftBumper
        return result


    def _monitor_controller(self):
        while True:
            events = get_gamepad()
            for event in events:
                if event.code == 'ABS_Y':
                    self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_X':
                    self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_RY':
                    self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_RX':
                    self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_Z':
                    self.prevLeftTrigger = self.LeftTrigger
                    self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
                elif event.code == 'ABS_RZ':
                    self.prevRightTrigger = self.RightTrigger
                    self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
                elif event.code == 'BTN_TL':
                    self.prevLeftBumper = self.LeftBumper
                    self.LeftBumper = event.state
                elif event.code == 'BTN_TR':
                    self.prevRightBumper = self.RightBumper
                    self.RightBumper = event.state
                elif event.code == 'BTN_SOUTH':
                    self.prevA = self.A
                    self.A = event.state
                elif event.code == 'BTN_NORTH':
                    self.prevY = self.Y
                    self.Y = event.state #previously switched with X
                elif event.code == 'BTN_WEST':
                    self.prevX = self.X
                    self.X = event.state #previously switched with Y
                elif event.code == 'BTN_EAST':
                    self.prevB = self.B
                    self.B = event.state
                elif event.code == 'BTN_THUMBL':
                    self.LeftThumb = event.state
                elif event.code == 'BTN_THUMBR':
                    self.RightThumb = event.state
                elif event.code == 'BTN_SELECT':
                    self.prevBack = self.Back
                    self.Back = event.state
                elif event.code == 'BTN_START':
                    self.prevStart = self.Start
                    self.Start = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY1':
                    self.prevLeftDPad = self.LeftDPad
                    self.LeftDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY2':
                    self.prevRightBumper = self.RightDPad
                    self.RightDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY3':
                    self.prevUpDPad = self.UpDPad
                    self.UpDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY4':
                    self.prevDownDPad = self.DownDPad
                    self.DownDPad = event.state