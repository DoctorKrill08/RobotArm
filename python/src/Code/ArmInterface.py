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
        self.turret_gui = ArmGUI(tk,self.root,Robot.turret)
        self.turret_gui.place(0,400)

    def update(self):
        self.claw_gui.update(Robot.claw)
        self.elbow_gui.update(Robot.elbow)
        self.turret_gui.update(Robot.turret)
        self.root.update()


class SystemGUI:
    TELEMETRY_TEXT_COLOR = "#00FF00"
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
    def setTelemetry(self, string):
        self.telemtryText.config(text=string)
        
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