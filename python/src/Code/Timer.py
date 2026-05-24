import time

class Timer():
    def __init__(self):
        self.start_time = time.perf_counter()
    def go(self):
        self.start_time = time.perf_counter()
    def time_passed_seconds(self):
        return (time.perf_counter() - self.start_time)