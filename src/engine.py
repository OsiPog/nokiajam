# Packages
import pygame
from math import cos, sin, atan2
import numpy

# Modules
from src.vec2 import Vec2, Line
from src.animation import Animation
from src.timer import Timer

class Level:

    def __init__(self, base_map: pygame.Surface, collision_map, output: pygame.Surface):
        self.base_map = base_map
        self.output = output

        self.position = Vec2(64, 64)
        self.binary_palette = [(67, 82, 61), (199, 240, 216)]
        self.rotation = 0

        self.perspective = [84.0, 130.0, 200.0]
        self.start_width = self.perspective[0] # 20
        self.end_width = self.perspective[1] # 50
        self.length = self.perspective[2] # 80

        self.free_rotate = False
        self.free_move = False

        self.collision_map = collision_map
        self.collision = {
            "drive": (0,255,0),
            "blocked": (255,0,0),
            "offroad": (0,0,255),
            "boost": (255,255,0),
            "finish": (255,255,255),
        }

        self.checkpoints = []
        self.laps = 0
        self.lap_handler = None
        self.checkpoint_handler = None

        # entity list
        self.entities = []

        self.update_variables()

    def update_variables(self):
        self.forward_vec = Vec2(cos(self.rotation), sin(self.rotation))
        self.left_vec = Vec2(cos(self.rotation + 3.14/2), sin(self.rotation + 3.14/2))
        self.width, self.height = self.output.get_size()

        self.A = self.position + self.left_vec*self.start_width*0.5
        self.B = self.A - self.left_vec*self.start_width 

        self.C = self.A + self.forward_vec*self.length + self.left_vec*(self.end_width - self.start_width)*0.5

        self.D = self.C + (self.B-self.A).unit()*self.end_width

    def project(self):
        self.update_variables()
        # action for every pixel on output
        for y in range(self.height):
            for x in range(self.width):
                p_m = self.screen_to_plane_pos(Vec2(x,y))
                color = None
                try:
                    pixel = self.base_map.get_at((round(p_m.x),round(p_m.y)))
                    # takes average of r, g, b to determine if light (1) or dark (0) color
                    if (sum(pixel)/len(pixel)) > 127:
                        color = self.binary_palette[1]
                    else:
                        color = self.binary_palette[0]
                except IndexError:
                    color = self.binary_palette[1]

                self.output.set_at((self.width - x -1,self.height - y -1), color)

        # Draw entities
        for entity in self.entities:
            p_s = self.plane_to_screen_pos(entity.position)
            if not (p_s.x >= 0 and p_s.x < self.width and p_s.y >= 0 and p_s.y < self.height): 
                continue
            
            sprite = entity.animation.get_current_frame()

            # scale sprite according to distance to camera
            scale = (
                (1 - p_s.y/self.height)
                    *(self.start_width/self.end_width)
                + (self.end_width - self.start_width)/self.end_width 
                + 0.1
            )*self.width/self.start_width
            scaled_sprite = pygame.transform.scale(sprite, (sprite.get_width()*scale, sprite.get_height()*scale))

            self.output.blit(scaled_sprite, (
                self.width - p_s.x - scaled_sprite.get_width()//2 -1, 
                self.height - p_s.y - scaled_sprite.get_height() -1))



    def move_forward(self, amount):
        self.position = self.position + Vec2(cos(self.rotation), sin(self.rotation))*amount

    def scale(self, scale):
        self.start_width = self.perspective[0]*scale
        self.end_width = self.perspective[1]*scale
        self.length = self.perspective[2]*scale

    def screen_to_plane_pos(self, screen_pos):
        x = screen_pos.x
        y = screen_pos.y
        A = self.A
        B = self.B
        C = self.C
        width = self.width
        height = self.height
        return A + (C - A)*(y/height) + (B - A).unit()*(x/width)*(y/height)*(self.end_width) + (B - A).unit()*(x/width)*(1 - y/height)*(self.start_width)
    
    def plane_to_screen_pos(self, plane_pos):
        line_AC = Line(self.A, (self.C-self.A).unit())
        line_PAB = Line(plane_pos, (self.A-self.B).unit())

        S, r, s = line_PAB.intersection_with(line_AC, True)

        line_BD = Line(self.B, (self.D-self.B).unit())
        S2 = line_PAB.intersection_with(line_BD)

        x = (r/(S2-S).length())*self.width
        y = (s/(self.C-self.A).length())*self.height

        return Vec2(x,y)

    def get_collision_at(self, plane_pos):
        color = self.collision_map.get_at((round(plane_pos.x), round(plane_pos.y)))
        for collision in self.collision:
            if self.collision[collision] == color:
                return collision

class SpriteEntity:
    def __init__(self, level, position, sprite_size, spritesheet, anim_speed=1):
        
        self.position = position
        self.sprite_size = sprite_size

        # splitting up spritesheet into animations with frames
        self.animation = Animation(spritesheet, sprite_size.tuple(), anim_speed)
        
        
        self.level = level
        level.entities.append(self)

class Player(SpriteEntity):
    def __init__(self, level, position, sprite_size, spritesheet, anim_speed=1):
        super().__init__(level, position, sprite_size, spritesheet, anim_speed)
        
        self.player_offset = 5

        self.velocity = Vec2()
        self.max_v = 3

        self.rotation = 0

        self.acceleration = 0.15
        self.back_accel = 0.05

        self.steer_sensi = 0.03

        self.drift_sensi = 0.001
        self.drift_increase = 0.4
        self.drift_max = 0.06
        self.drift_since_frames = 0

        self.paused = False

        self.checkpoint = 0
        self.lap = 0

        self.start_time = 0

        # fix for fast anim bug on spawn
        self.animation.timer.speed = 500

    def update(self):
        # Adjust level camera
        if not self.level.free_move:
            self.level.position = self.position - self.level.forward_vec*self.player_offset


        rot_diff = self.rotation - self.level.rotation

        #normalize difference
        while abs(rot_diff) > 6.28: rot_diff -= 6.28*(abs(rot_diff)/rot_diff)

        if ((abs(rot_diff) > 0.01) and not self.level.free_rotate):
            self.level.rotation += rot_diff*0.3

        # Adjust sprite on perspective
        if (abs(rot_diff) <= 0.1):
            self.animation.selected_animation = 0
        elif (abs(rot_diff) <= (3*3.14)/8):
            if (rot_diff > 0):
                self.animation.selected_animation = 1
            else:
                self.animation.selected_animation = 7
        elif (abs(rot_diff) <= (5*3.14)/8):
            if (rot_diff > 0):
                self.animation.selected_animation = 2
            else:
                self.animation.selected_animation = 6
        elif (abs(rot_diff) <= (7*3.14)/8):
            if (rot_diff > 0):
                self.animation.selected_animation = 3
            else:
                self.animation.selected_animation = 5
        elif (abs(rot_diff) <= (9*3.14)/8):
            self.animation.selected_animation = 4
        elif (abs(rot_diff) <= (11*3.14)/8):
            if (rot_diff > 0):
                self.animation.selected_animation = 5
            else:
                self.animation.selected_animation = 3
        elif (abs(rot_diff) <= (13*3.14)/8):
            if (rot_diff > 0):
                self.animation.selected_animation = 6
            else:
                self.animation.selected_animation = 2
        elif (abs(rot_diff) <= (15*3.14)/8):
            if (rot_diff > 0):
                self.animation.selected_animation = 7
            else:
                self.animation.selected_animation = 1

        if self.paused: return

        # # Calculate
        # if (self.velocity.length() > 0):
        #     self.rotation = atan2(*self.velocity.unit().tuple()) 

        # Controls
        keys = pygame.key.get_pressed()

        # Flags to determine action
        self.is_moving = False
        self.is_steering_left = False
        self.is_steering_right = False
        self.is_drifting = False

        # driving back and forth
        if keys[pygame.K_w]:
            if self.velocity.length() < self.max_v:
                self.velocity = self.velocity + Vec2(cos(self.rotation), sin(self.rotation))*self.acceleration
            self.is_moving = True
        if keys[pygame.K_s]:
            if self.velocity.length() < self.max_v: # max velocity
                self.velocity = self.velocity + Vec2(cos(self.rotation), sin(self.rotation))*-self.back_accel
            self.is_moving = True
            #print(round(self.position.x),",", round(self.position.y))

        # steering
        if self.is_moving:
            if keys[pygame.K_a]:
                self.rotation = self.rotation - self.steer_sensi
                self.is_steering_left = True
            if keys[pygame.K_d]:
                self.rotation = self.rotation + self.steer_sensi
                self.is_steering_right = True

        if self.is_steering_left or self.is_steering_right:
            if keys[pygame.K_SPACE]:
                rot_increase = min(self.drift_max, 
                    self.drift_sensi*(1 + self.drift_increase*self.drift_since_frames)
                )

                if (self.is_steering_left):
                    rot_increase *= -1

                
                self.rotation += rot_increase    
                self.drift_since_frames += 1
                self.is_drifting = True
        else:
            self.drift_since_frames = 0


        # Changing animation speed
        self.animation.timer.speed = round((1 - self.velocity.length()/self.max_v)*10000 + 1)

        # checkpoint check
        if self.checkpoint < len(self.level.checkpoints):
            if ((self.position - self.level.checkpoints[self.checkpoint]).length() < 45):
                self.checkpoint += 1
                # fire handler for checkpoint events (LEVELS)
                if self.level.checkpoint_handler:
                    self.level.checkpoint_handler(self.checkpoint, self)

        # adding velocity to position after collision check
        collision = self.level.get_collision_at(self.position + self.velocity)

        if collision == "drive":
            pass
        if collision == "offroad":
            self.velocity *= 0.9
        if collision == "blocked":
            self.velocity = Vec2()
        if collision == "boost":
            self.velocity = self.velocity.unit()*self.max_v*1.8
        if collision == "finish":
            if self.checkpoint == len(self.level.checkpoints):
                self.lap += 1
                self.checkpoint = 0
                # fire the handler for lap events (LEVELS)
                if self.level.lap_handler: 
                    self.level.lap_handler(self.lap, self)
        
        self.position = self.position + self.velocity
        # losing velocity
        if (self.velocity.length() < 0.009): 
            self.velocity = Vec2()
            self.animation.timer.speed = 0
        else:
            self.velocity -= self.velocity.unit()*min(self.velocity.length()*0.1, 0.1)
    
