# Packages
import pygame
from math import cos, sin
import numpy as np

# Modules
from src.vec2 import Vec2

class Engine:
    def __init__(self, base_map: pygame.Surface, output: pygame.Surface):
        self.base_map = base_map
        self.output = output

        self.position = Vec2(64, 64)
        self.binary_palette = [(67, 82, 61), (199, 240, 216)]
        self.rotation = 0
        self.start_width = 20.0
        self.end_width = 120.0
        self.length = 100.0

        # convert given surface to list of 0..1
        self.updateMap(base_map)

    def updateMap(self, surface):
        self.map = []
        for y in range(surface.get_height()):
            self.map.append([])
            for x in range(surface.get_width()):
                pixel = surface.get_at((x,y))
                # takes average of r, g, b to determine if light (1) or dark (0) color
                if (sum(pixel)/len(pixel)) > 127:
                    self.map[-1].append(1)
                else:
                    self.map[-1].append(0)

    def project(self):
        forward_vec = Vec2(cos(self.rotation), sin(self.rotation))
        left_vec = Vec2(cos(self.rotation + 3.14/2), sin(self.rotation + 3.14/2))
        width, height = self.output.get_size()

        A = self.position + left_vec*self.start_width*0.5
        B = A - left_vec*self.start_width

        C = A + forward_vec*self.length + left_vec*(self.end_width - self.start_width)*0.5

        # action for every pixel on output
        output_array = []
        for y in range(height):
            for x in range(width):
                p_m = A + (C - A)*(y/height)
                p_m = p_m + (B - A).unit()*(x/width)*(y/height)*(self.end_width)
                p_m = p_m + (B - A).unit()*(x/width)*(1 - y/height)*(self.start_width)
                output_array.append(p_m)
                color = None
                try:
                    color = self.binary_palette[
                                self.map[round(p_m.x)][round(p_m.y)]
                            ]
                except IndexError:
                    color = self.binary_palette[0]

                self.output.set_at((width - x -1,height - y -1), color)

        #return A, B, C, output_array


