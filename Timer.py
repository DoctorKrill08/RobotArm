import time

class Timer():
    def __init__(self):
        self.start_time = time.perf_counter()
    def go(self):
        self.start_time = time.perf_counter()
    def time_passed_seconds(self):
        return (time.perf_counter() - self.start_time)

class Stopwatch(Timer):
    def __init__(self):
        super().__init__()
        self.on = False
    def go(self):
        super().go()
        self.on = True
    def reset(self):
        super().go()
    def stop(self):
        self.on = False
    def time_passed_seconds(self):
        if (self.on == False):
            return 0
        return super().time_passed_seconds()
    