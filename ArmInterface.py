import tkinter as tk
from enum import Enum
from Subsystems.Claw import ClawGUI
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
        self.claw_gui.frame.place(x=0,y=0)
        self.controller_gui = ControllerGUI(self.root)

    def update(self):
        self.claw_gui.update(Robot.claw)
        self.root.update()


class SubsystemGUI:
    TELEMETRY_TEXT_COLOR = "#00FF00"
    def __init__(self,tk,root):
        self.frame = tk.Frame(root)
        self.frame.place(width=200, height=200)
        self.frame.configure(bg="#1C1E1C")
    def create_telemetry(self,title):
        self.telemetryFrame = tk.Frame(self.frame)
        self.telemetryFrame.place(width=200, height=100)
        self.telemetryFrame.configure(bg="#000000")
        self.telemetryTilte = tk.Label(self.frame)
        self.telemetryFrame.configure(fg=SubsystemGUI.TELEMETRY_TEXT_COLOR)
        self.telemetryFrame.config(text=title)

class ControllerGUI:
    def __init__(self,root):
        self.enabled = False
        self.button = tk.Button(root, text=self.status())
        self.button.config(command=lambda: self.flip())
        self.button.pack()
    def flip(self):
        self.enabled = not self.enabled
        self.button.config(text=self.status())
    def status(self):
        status = "enabled"
        if (not self.enabled):
            status= "disabled"
        return f"Controller is {status}"