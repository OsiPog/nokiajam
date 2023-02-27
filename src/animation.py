# Packages
import pygame
import numpy as np

# Modules
from src.timer import Timer

class Animation:

    def __init__(self, surface, frame_size, speed=1):

        #getting animation frames
        self.animations = []

        for y in range(round(surface.get_height()/frame_size[1])): #every line of sprites in an animation file is an animation
            animation = []

            for x in range(round(surface.get_width()/frame_size[0])): #every sprite in an animation is an animation frame

                #cropping the tile
                cropped = pygame.Surface(frame_size, pygame.SRCALPHA)
                cropped.blit(surface, [0, 0], [x*frame_size[0], y*frame_size[1], x*frame_size[0] + frame_size[0], y*frame_size[1] + frame_size[1]]) # start x, start y; end x, end y
                    
                if not np.any(pygame.surfarray.pixels_alpha(cropped) != 0): #checking the whole frame if every pixel is alpha 0 ,thanks numpy
                    break
                    
                else:

                    animation.append(cropped)

            self.animations.append(animation)


        self.timer = Timer(self.next_frame, speed)

        self.selected_animation = 0
        self._currentFrame = 0 #current frame in the selected animation


        self.get_current_frame()


    def get_current_frame(self):
        if self._currentFrame >= len(self.animations[self.selected_animation]): #if the animation frame is non existent then just revert the variable back to 0
            self._currentFrame = 0
        return self.animations[self.selected_animation][self._currentFrame] #returning the current frame


    #function which gets called by the timer class
    def next_frame(self):
        self._currentFrame += 1

