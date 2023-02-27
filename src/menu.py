# Packages
import pygame

# Modules
from src.vec2 import Vec2
from src.animation import Animation

# A menu consists of an optional background and buttons
class Menu:
    instances = []

    def hide_all_and_show(menu_to_show):
        for menu in Menu.instances:
            if menu is menu_to_show: menu.disabled = False
            else: menu.disabled = True

    def __init__(   self, 
                    screen, 
                    next_btn=pygame.K_s, 
                    prev_btn=pygame.K_w, 
                    click_btn=pygame.K_SPACE, 
                    background=None, 
                    offset=Vec2(), 
                    loop_selection=False,
                    disabled=False,
                    disable_input=False):
        self.screen = screen
        self.background = background
        self.offset = offset

        self.buttons = []

        self.next_btn = next_btn
        self.prev_btn = prev_btn
        self.click_btn = click_btn
        self.is_pressed = True # to avoid too fast scrolling

        self.loop_selection = loop_selection

        self.selected_button = 0

        self.disabled = disabled

        self.disable_input = disable_input

        Menu.instances.append(self)

    def update(self):
        if self.disabled: return
        
        if self.background:
            self.screen.blit(self.background, self.offset.tuple())

        # key actions
        if not self.disable_input:
            keys = pygame.key.get_pressed()

            if not self.is_pressed:
                if keys[self.next_btn]:
                    if not self.is_pressed:
                        self.move_selection(1)

                if keys[self.prev_btn]:
                    if not self.is_pressed:
                        self.move_selection(-1)
                if keys[self.click_btn]:
                    handler = self.buttons[self.selected_button].handler
                    if (handler): handler()
            self.is_pressed = keys[self.prev_btn] or keys[self.next_btn] or keys[self.click_btn]


        # Draw buttons
        for button in self.buttons:
            if button.hidden: continue
            self.screen.blit(button.draw(), (button.position - button.size*0.5).tuple())

    def move_selection(self, change):
        btn_id = self.selected_button + change

        if ((btn_id > len(self.buttons)-1) or btn_id < 0):
            if self.loop_selection:
                if btn_id > len(self.buttons)-1:
                    btn_id -= len(self.buttons)
                else:
                    btn_id += len(self.buttons)
            else: 
                return
        
        if (
            self.buttons[self.selected_button].animation
        and self.buttons[btn_id].animation
        ):
            self.buttons[self.selected_button].animation.selected_animation = 0
            self.buttons[btn_id].animation.selected_animation = 1
        self.selected_button = btn_id
        if (not self.buttons[btn_id].selectable) and change != 0:
            new_change = round(change/abs(change))
            if (not self.loop_selection) and ((btn_id == len(self.buttons)-1) or btn_id == 0):
                new_change *= -1

            self.move_selection(new_change)

# Is in a Menu, has a size and position, background image if wanted
# doesnt have to be a button
class MenuButton:
    def __init__(   self, 
                    menu, 
                    size, 
                    position, 
                    bg_sheet=None, 
                    bg=None,
                    text=None, 
                    text_color=None, 
                    font=None,   
                    tag=None,
                    handler=None,
                    selectable=True,
                    hidden=False):
        self.position = position
        self.size = size
        if bg_sheet:
            self.animation = Animation(bg_sheet, size.tuple(), 30)
        else:
            self.animation = None

        self.bg = bg

        self.tag = tag
        self.text = text
        self.text_color = text_color
        self.font = font
        self.handler = handler
        self.selectable = selectable
        self.hidden = hidden

        menu.buttons.append(self)
        # Update the menu selection (maybe the just added button is the selected one?)
        menu.move_selection(0)
    
    def draw(self):
        if self.animation and not self.hidden:
            background = self.animation.get_current_frame()
        elif self.bg and not self.hidden:
            background = pygame.transform.scale(self.bg, self.size.tuple())
        else:
            background = pygame.Surface(self.size.tuple(), flags=pygame.SRCALPHA)

        if self.hidden: return background

        if self.text:
            rendered = self.font.render(self.text, False, self.text_color)

            background.blit(rendered,
                (
                    round(self.size.x/2 - rendered.get_width()/2),
                    round(self.size.y/2 - rendered.get_height()/2),
                )
            )

        return background