# Packages
import pygame
import math

# Modules
from src.vec2 import Vec2

class Engine:
    def __init__(self, base_map: pygame.Surface, output: pygame.Surface):
        this.base_map = base_map
        this.output = output

        this.position = Vec2()
        this.binary_palette = []
        this.rotation = 0
        this.start_width = 10.0
        this.end_width = 100.0
        this.length = 20.0

    def project() -> list:
        forward_vec = Vec2(cos(this.rotation), sin(this.rotation))
        left_vec = Vec2(cos(this.rotation + 90), sin(this.rotation + 90))
        width, height = this.output.get_size()

        A = this.position + left_vec*this.start_width*0.5
        B = this.position - left_vec*this.start_width*0.5

        C = A + left_vec*(this.end_width - this.start_width)*0.5 + forward_vec*this.length
        D = B - left_vec*(this.end_width - this.start_width)*0.5 + forward_vec*this.length

        pixel_array = []
        for y in range(height):
            for x in range(width):



