import utime

class Task():

    def __init__(self):
        self.countdown = self.interval = 1

    def update(self, scheduler):
        pass

class Scheduler():

    def __init__(self):
        self.tasks = []

    def register(self, task):
        if task not in self.tasks:
            self.tasks.append(task)

    def loop_forever(self, sleep):
        while True:
            for task in self.tasks:
                if task.countdown <= 0:
                    task.countdown = task.interval + task.countdown
                    task.update(self)
                else:
                    task.countdown -= sleep
            utime.sleep(sleep)
