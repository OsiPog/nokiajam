import math

class Vec2:
    def __init__(self, x: int = 0, y: int = 0, random: tuple[float,float,float,float] = None) -> None:
        self.x = x
        self.y = y
    
    def tuple(self) -> tuple:
        return (self.x, self.y)
        
    def length(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)
    
    def distance(v0: "Vec2", v1: "Vec2") -> float:
        return math.sqrt((v1.x - v0.x)**2 + (v1.y - v0.y)**2)

    def unit(self) -> "Vec2":
        return self*(1/self.length())
    
    def angle(v0: "Vec2", v1: "Vec2") -> float:
        length = Vec2.distance(v0, v1)
        if length == 0: return 0
        
        x = (v1.x - v0.x)/length
        y = (v1.y - v0.y)/length
        return math.atan2(x,y)
   
    def __add__(self, v: "Vec2") -> "Vec2":
        return Vec2(self.x + v.x, self.y + v.y)

    def __sub__(self, v: "Vec2") -> "Vec2":
        return Vec2(self.x - v.x, self.y - v.y)
        
    def __mul__(self, fac: float) -> "Vec2":
        return Vec2(self.x * fac, self.y * fac)


class Line:
    def __init__(self, p, v):
        self.p = p
        self.v = v
    def intersection_with(self, line, return_params=False):
        v = self.p
        d = self.v
        w = line.p
        c = line.v

        s = (d.y*v.x - d.y*w.x -d.x * v.y + d.x*w.y)/(c.x*d.y-c.y*d.x)

        if (d.x != 0):
            r = (w.x + s*c.x - v.x)/d.x
        else:
            r = (w.y + s*c.y - v.y)/d.y

        S = self.p + self.v*r

        if (return_params):
            return S, r, s
        else:
            return S