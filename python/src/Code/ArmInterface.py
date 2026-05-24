import tkinter as tk
from enum import Enum
from Robot import Robot
#Buttons:
#Open/Close Claw
#Up/Down Forearm
#Forward/Backward Shoulder
#Left/Right Turret

class Interface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Arm Interface")
        self.root.geometry("600x600")
        self.root.configure(bg='black')
        self.claw_gui = ClawGUI(tk,self.root,Robot.claw)
        self.claw_gui.place(0,0)
        self.elbow_gui = ArmGUI(tk,self.root,Robot.elbow)
        self.elbow_gui.place(0,200)
        self.shoulder_gui = ArmGUI(tk,self.root,Robot.shoulder)
        self.shoulder_gui.place(400,0)
        self.turret_gui = ArmGUI(tk,self.root,Robot.turret)
        self.turret_gui.place(0,400)
        self.robot_gui = RobotGUI(tk,self.root)
        self.robot_gui.place(200,0)
        self.wrist_gui = ArmGUI(tk,self.root,Robot.wrist)
        self.wrist_gui.place(200,400)
    update_index = 0
    def update(self):
        if (not self.update_index == 2):
            self.update_index += 1
            return
        self.update_index = 0
        self.claw_gui.update(Robot.claw)
        self.elbow_gui.update(Robot.elbow)
        self.turret_gui.update(Robot.turret)
        self.shoulder_gui.update(Robot.shoulder)
        self.wrist_gui.update(Robot.wrist)
        self.robot_gui.update(tk)
        self.root.update()


class SystemGUI:
    TELEMETRY_TEXT_COLOR = "#00FF00"
    INCREMENT_COLOR = "#00FF00"
    DECREMENT_COLOR = "#FF0000"
    FRAME_COLOR = "#1C1E1C"
    TEXT_COLOR = "#FFFFFF"
    TELEMETRY_BACKGROUND_COLOR = "#141414"
    def __init__(self,tk,root,title):
        self.tk = tk
        self.frame = tk.Frame(root)
        self.frame.place(width=200, height=200)
        self.frame.configure(bg=SystemGUI.FRAME_COLOR)
        self.titleLabel = self.tk.Label(self.frame,font='Helvetica 14 bold')
        self.titleLabel.config(text = title)
        self.titleLabel.pack(fill = 'x')
        self.titleLabel.configure(bg=SystemGUI.FRAME_COLOR)
        self.titleLabel.config(fg = SystemGUI.TEXT_COLOR)
    def create_telemetry(self):
        self.telemetryFrame = self.tk.Frame(self.frame)
        self.telemetryFrame.place(width=200, height=100, rely=0.5)
        self.telemetryFrame.configure(bg=SystemGUI.TELEMETRY_BACKGROUND_COLOR)
        self.telemtryText = self.tk.Label(self.telemetryFrame)
        self.telemtryText.config(bg = SystemGUI.TELEMETRY_BACKGROUND_COLOR,fg = SystemGUI.TELEMETRY_TEXT_COLOR,justify="left")
        self.telemtryText.pack(side="top", anchor="nw")
    def place(self,X,Y):
        self.frame.place(x=X,y=Y)
    def size(self,w,h):
        self.telemetryFrame.place(width=w, height=h, rely=0.5)
    def setTelemetry(self, string):
        self.telemtryText.config(text=string)
        
class RobotGUI(SystemGUI):
    def __init__(self,tk,root):
        super().__init__(tk, root,"Robot")
        self.frame.place(width=200,height=400)
        self.end_button = tk.Button(self.frame, text="Turn Off Robot", bg = SystemGUI.FRAME_COLOR, fg = SystemGUI.TEXT_COLOR)
        self.end_button.config(command=lambda: Robot.turn_off())
        self.end_button.pack(fill = 'x')

        self.kinematics_button = tk.Button(self.frame, text="Inverse Kinematics Off", bg = SystemGUI.FRAME_COLOR, fg = SystemGUI.TEXT_COLOR)
        self.kinematics_button.config(command=lambda: Robot.flip_kinematics())
        self.kinematics_button.pack(fill = 'x')

        self.autonomous_button = tk.Button(self.frame, text="Autonomous Off", bg = SystemGUI.FRAME_COLOR, fg = SystemGUI.TEXT_COLOR)
        self.autonomous_button.config(command=lambda: Robot.flip_autonomous())
        self.autonomous_button.pack(fill = 'x')

        self.x_up_button = tk.Button(self.frame, text="X Up", bg = SystemGUI.FRAME_COLOR, fg = SystemGUI.INCREMENT_COLOR)
        self.x_up_button.config(command=lambda: Robot.x_up())
        self.x_up_button.pack(fill = 'x')

        self.x_down_button = tk.Button(self.frame, text="X Down", bg = SystemGUI.FRAME_COLOR, fg = SystemGUI.DECREMENT_COLOR)
        self.x_down_button.config(command=lambda: Robot.x_down())
        self.x_down_button.pack(fill = 'x')

        self.y_up_button = tk.Button(self.frame, text="Y Up", bg = SystemGUI.FRAME_COLOR, fg = SystemGUI.INCREMENT_COLOR)
        self.y_up_button.config(command=lambda: Robot.y_up())
        self.y_up_button.pack(fill = 'x')

        self.y_down_button = tk.Button(self.frame, text="Y Down", bg = SystemGUI.FRAME_COLOR, fg = SystemGUI.DECREMENT_COLOR)
        self.y_down_button.config(command=lambda: Robot.y_down())
        self.y_down_button.pack(fill = 'x')

        self.create_telemetry()
        self.size(200,200)
        

    def update(self,tk):
        self.setTelemetry(Robot.telemetry)
        self.kinematics_button.config(text=f"Inverse Kinematics On: {Robot.inverse_kinematics}")
        self.autonomous_button.config(text=f"Autonomous On: {Robot.autonomous}")


class SubsystemGUI(SystemGUI):
    def __init__(self,tk,root,subsystem):
        super().__init__(tk, root,subsystem.name)
        self.create_telemetry()
        self.flip_button = tk.Button(self.frame, text="...", bg = SystemGUI.FRAME_COLOR, fg = SystemGUI.TEXT_COLOR)
        self.flip_button.config(command=lambda: subsystem.flip())
        self.flip_button.pack(fill = 'x')
    def update(self,subsystem):
        self.flip_button.config(text=f"{subsystem.name} on: {subsystem.on}")
        self.setTelemetry(subsystem.telemetry)
class ClawGUI(SubsystemGUI):
    def __init__(self,tk,root,claw):
        super().__init__(tk, root,claw)
        self.claw_button = tk.Button(self.frame, text="...", bg = SystemGUI.FRAME_COLOR, fg = SystemGUI.TEXT_COLOR)
        self.claw_button.config(command=lambda: claw.flip_claw_state())
        self.claw_button.pack(fill = 'x')
    def update(self,claw):
        super().update(claw)
        self.claw_button.config(text=f"{claw.name} is: {claw.state.value}")

class ArmGUI(SubsystemGUI):
    INCREMENT_COLOR = "#00FF00"
    DECREMENT_COLOR = "#FF0000"
    def __init__(self,tk,root,arm):
        super().__init__(tk, root,arm)
        self.up_button = tk.Button(self.frame, text="increase", bg = SystemGUI.FRAME_COLOR, fg = ArmGUI.INCREMENT_COLOR)
        self.up_button.config(command=lambda: arm.increment())
        self.up_button.pack(fill = 'x')

        self.down_button = tk.Button(self.frame, text="decrease", bg = SystemGUI.FRAME_COLOR, fg = ArmGUI.DECREMENT_COLOR)
        self.down_button.config(command=lambda: arm.decrement())
        self.down_button.pack(fill = 'x')