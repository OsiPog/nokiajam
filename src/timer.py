import time

class Timer:
    instances = [] #list to keep track of all instances
    
    def __init__(self, function, speed=1, multiplier=100):

        self.speed = speed
        self.function = function
        self.multiplier = multiplier

        self._oldTimer = 0
        self._mod = 0

        Timer.instances.append(self)

    def update(self):
        if (self.speed == 0): return
        if self.speed == 1:
            self.function()
            return

        currentMod = round(time.time()*self.multiplier) % self.speed #calculating the current mod of the time (times multiplier) and the timer speed
        if self._mod >= currentMod: #if this mod was 0 or surpassed it
            self.function()

        self._mod = currentMod #setting the mod