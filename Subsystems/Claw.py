from enum import Enum
class ClawStates(Enum):
    OPEN = "opened"
    CLOSE = "closed"

class Claw:
    def __init__(self):
        self.state = ClawStates.OPEN
    def flip(self):
        if (self.state == ClawStates.OPEN):
            self.state = ClawStates.CLOSE
        else:
            self.state = ClawStates.OPEN

class ClawGUI():
    def __init__(self,tk,root,claw):
        self.frame = tk.Frame(root)
        self.frame.place(width=200, height=200)
        self.frame.configure(bg="#1C1E1C")
        self.button = tk.Button(self.frame, text="Claw is opened")
        self.button.config(command=lambda: claw.flip())
        self.button.pack()
    def update(self,claw):
        self.button.config(text=f"Claw is {claw.state.value}")