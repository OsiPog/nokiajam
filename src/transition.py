from src.timer import Timer

class Transition:
    def __init__(self, handler, frames):
        self.handler = handler
        self.frames = round(frames)
        self.since = 0

        self.all_params = True

        self.timer = Timer(self.update)

    def update(self):
        t = self.since/self.frames
        self.handler(t)

        if self.since == self.frames:
            Timer.instances.remove(self.timer)
        else:
            self.since += 1

    def cancel(self):
        Timer.instances.remove(self.timer)