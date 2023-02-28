import os
print("Installing python packages. Please wait...")
os.system("pip install pygame")
os.system("pip install numpy")

# Packages
import pygame
import json
import time
import asyncio

# Modules
from src.engine import Level, Vec2, sin, cos, Timer, SpriteEntity, Player
from src.menu import Menu, MenuButton
from src.transition import Transition

# Constants
NOKIA_RES = (84, 48)
BOTTOM_SCREEN_RES = (84, 40)
SCALE = 10
BOTTOM_SCREEN_OFFSET = (0,(NOKIA_RES[1]-BOTTOM_SCREEN_RES[1]))
SCREEN_RES = (NOKIA_RES[0]*SCALE, NOKIA_RES[1]*SCALE)

PALETTE = ((67, 82, 61), (199, 240, 216))

# Menu constants
MENU_BIG_BTN_SIZE = Vec2(37, 14)
MENU_LEVEL_BTN_SIZE = Vec2(80, 14)

# global
Game_Running = True
Invert_Screen = False

# level handlers
def handler_quiet_meadows(lap, player):
    if lap == 3:
        p = Vec2(555, 180)
        # place cow on shortcut
        cow = SpriteEntity(   player.level, 
                        p, 
                        ENTITIES["cow"]["sprite_size"], 
                        ENTITIES["cow"]["spritesheet"])
        # fix player still on top
        player.level.entities.remove(cow)
        player.level.entities.insert(0,cow)

        # collision of cow
        pygame.draw.circle( player.level.collision_map, 
                            player.level.collision["blocked"],
                            p.tuple(True),
                            25)

def handler_tutorial(checkpoint, player):
    def close(t):
        if t == 1:
            menu_ingame_tut0.hidden = True
            menu_ingame_tut1.hidden = True
    
    menu_ingame_tut0.hidden = False
    menu_ingame_tut1.hidden = False

    if (checkpoint == 1):
        menu_ingame_tut0.text = "Press W to drive"
        menu_ingame_tut1.text = "and S for reverse."
    if (checkpoint == 2):
        menu_ingame_tut0.text = "Use A and D to"
        menu_ingame_tut1.text = "steer."
    if (checkpoint == 3):
        menu_ingame_tut0.text = "Drift with SPACE"
        menu_ingame_tut1.text = "around sharp corners."
    if (checkpoint == 4):
        menu_ingame_tut0.text = "Use boost panels"
        menu_ingame_tut1.text = "to gain much speed"
    

    Transition(close, 180)

def handler_mount(lap, player):
    if lap == 2:
        # remove rock from shortcut
        pygame.draw.circle( player.level.collision_map, 
                            player.level.collision["drive"],
                            (893, 1371),
                            40)
        player.level.entities[0].position = Vec2(956, 1382)


ENTITIES = {
    "cow": {
        "sprite_size": Vec2(18, 16),
        "spritesheet": pygame.image.load("src/img/cow.png")
    },
    "rock": {
        "sprite_size": Vec2(32, 32),
        "spritesheet": pygame.image.load("src/img/rock.png")
    }
}

LEVELS = [
    {
        "name": "Tutorial",
        "map": pygame.image.load("src/img/level/level1.png"),
        "collision_map": pygame.image.load("src/img/level/level1_coll.png"),
        "start_pos": Vec2(460, 900),
        "start_rot": -3.14/2,
        "checkpoints": [
            Vec2(460, 890),
            Vec2(460, 645),
            Vec2(400, 180),
            Vec2(570, 310)
        ],
        "checkpoint_handler": handler_tutorial,
        "entities": [],
        "laps": 1,
        "lap_handler": None,
        "goals": [
            300,
            200,
            100,
        ],
        
        "is_visible": True,
    },
    {
        "name": "Quiet Farm",
        "map": pygame.image.load("src/img/level/level0.png"),
        "collision_map": pygame.image.load("src/img/level/level0_coll.png"),
        "start_pos": Vec2(96, 498),
        "start_rot": -3.14/2,
        "checkpoints": [
            Vec2(404,180),
            Vec2(704,310),
            Vec2(630,815)
        ],
        "checkpoint_handler": None,
        "entities": [
            {
                "entity": ENTITIES["cow"],
                "position": Vec2(483, 199)
            },
            {
                "entity": ENTITIES["cow"],
                "position": Vec2(511 , 211)
            },
            {
                "entity": ENTITIES["cow"],
                "position": Vec2(623 , 285)
            },
            {
                "entity": ENTITIES["cow"],
                "position": Vec2(727 , 75)
            },
            {
                "entity": ENTITIES["cow"],
                "position": Vec2(632 , 160)
            },
            {
                "entity": ENTITIES["cow"],
                "position": Vec2(744 , 276)
            },
            {
                "entity": ENTITIES["cow"],
                "position": Vec2(874 , 464)
            },
            {
                "entity": ENTITIES["cow"],
                "position": Vec2(730 , 188)
            },
        ],
        "laps": 3,
        "lap_handler": handler_quiet_meadows,
        "goals": [
            85,
            70,
            62,
        ],
        
        "is_visible": True,
    },
    {
        "name": "Lonely Mount",
        "map": pygame.image.load("src/img/level/level2.png"),
        "collision_map": pygame.image.load("src/img/level/level2_coll.png"),
        "start_pos": Vec2(1420, 780),
        "start_rot": -3.14/2,
        "checkpoints": [
            Vec2(1212, 94),
            Vec2(194, 412),
            Vec2(404, 974),
        ],
        "checkpoint_handler": None,
        "entities": [
            {
                "entity": ENTITIES["rock"],
                "position": Vec2(885, 1377)
            }
        ],
        "laps": 2,
        "lap_handler": handler_mount,
        "goals": [
            130,
            110,
            102,
        ],
        
        "is_visible": True,
    },
]
# save game loading
SAVE = [
    {
        "best": -1,
        "is_unlocked": True
    },
    {
        "best": -1,
        "is_unlocked": False
    },
    {
        "best": -1,
        "is_unlocked": False
    }
]
try:
    with open("save.json", "r") as file:
        SAVE = json.load(file)
except FileNotFoundError:
    with open("save.json", "w") as file:
        json.dump(SAVE, file)

# Inverts color of an image to the opposite on the palette
def invert(surf):
    result = pygame.Surface(surf.get_size())
    for y in range(surf.get_height()):
        for x in range(surf.get_width()):
            if surf.get_at((x,y)) == PALETTE[0]: result.set_at((x,y), PALETTE[1])
            if surf.get_at((x,y)) == PALETTE[1]: result.set_at((x,y), PALETTE[0])
    surf.blit(result, (0,0))

def secs_to_mins(raw_secs):
    mins_frac = raw_secs/60
    mins = int(mins_frac)
    secs = int((mins_frac - mins)*60)
    return str(mins) + ":" + "0"*(secs < 10) + str(secs)

def milisecs_to_mins(raw_milisecs):
    secs_frac = raw_milisecs/1000
    secs = int(secs_frac)
    milisecs = int((secs_frac-secs)*1000)
    return secs_to_mins(secs) + ":" + "0"*(milisecs < 10) + "0"*(milisecs < 100) + str(milisecs)

def quit_game():
    global Game_Running

    Game_Running = False

    # save game
    with open("save.json", "w") as file:
        json.dump(SAVE, file)


async def main():
    global menu_ingame_tut0
    global menu_ingame_tut1

    # functions which use variables in this scope
    def show_keys_screen():
        Menu.hide_all_and_show(menu_keys_menu)

    def show_keys_ingame_screen():
        Menu.hide_all_and_show(menu_keys_ingame)

    def show_start_screen():
        Menu.hide_all_and_show(start_menu)

    def show_level_selection():
        level_select_menu.buttons = []
        for i, level_dict in enumerate(LEVELS):
            if not level_dict["is_visible"]: continue

            new_btn = MenuButton(
                            menu=level_select_menu, 
                            size=MENU_LEVEL_BTN_SIZE, 
                            position=Vec2(42, 8+15*i),
                            bg_sheet=img_menu_level_btn,
                            text=level_dict["name"],
                            text_color=PALETTE[0],
                            font=font_ark,
                            handler=show_level_confirm
            )

            if not SAVE[i]["is_unlocked"]:
                new_btn.text = "---Locked---"
                new_btn.handler = None
        Menu.hide_all_and_show(level_select_menu)

    def show_pause_screen():
        if player.paused: return # dont pause when paused already
        player.paused = True
        menu_pause.selected_button = 2
        Menu.hide_all_and_show(menu_pause)

    def close_pause_screen():
        player.paused = False
        Menu.hide_all_and_show(menu_ingame)

    def show_level_confirm():
        level_id = level_select_menu.selected_button
        # Level name
        level_confirm_title.text = LEVELS[level_id]["name"]

        # Personal record
        record = SAVE[level_id]["best"]
        stars = 0
        if record != -1:
            level_confirm_current_time.text = secs_to_mins(record)

            for goal in LEVELS[level_id]["goals"]:
                if record < goal: stars += 1
        else:
            level_confirm_current_time.text = "-:-"

        # Stars and next
        level_confirm_stars.bg = img_menu_stars[stars] # star image
        if (stars < 3):
            level_confirm_next_time.text = "Next: "+ secs_to_mins(LEVELS[level_id]["goals"][stars])
        else:
            level_confirm_next_time.text = "PERFECT!"

        # mini preview (fixme)
        level_confirm_thumb.bg = pygame.transform.scale(LEVELS[level_id]["map"], (25,25))
        level_confirm_thumb

        Menu.hide_all_and_show(level_confirm_menu)

    def play_level():
        level_id = level_select_menu.selected_button

        # Update level engine
        level_engine.base_map = LEVELS[level_id]["map"].copy()
        level_engine.collision_map = LEVELS[level_id]["collision_map"].copy()
        level_engine.checkpoints = LEVELS[level_id]["checkpoints"]
        level_engine.laps = LEVELS[level_id]["laps"]
        level_engine.lap_handler = LEVELS[level_id]["lap_handler"]
        level_engine.checkpoint_handler = LEVELS[level_id]["checkpoint_handler"]
        level_engine.free_rotate = True
        level_engine.rotation = LEVELS[level_id]["start_rot"] + 3.14

        level_engine.entities = []
        for entity in LEVELS[level_id]["entities"]:
            SpriteEntity(   level_engine, 
                            entity["position"], 
                            entity["entity"]["sprite_size"], 
                            entity["entity"]["spritesheet"])
        level_engine.entities.append(player) # that player is above all entities

        # Update player
        player.rotation = LEVELS[level_id]["start_rot"]
        player.position = LEVELS[level_id]["start_pos"]
        player.velocity = Vec2()
        player.checkpoint = 0
        player.lap = 1
        player.paused = True

        # Startup animation
        startup_scale = 10
        startup_duration = 300
        key_pressed = {"state": True} #ugly!
        def startup(t):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                if not key_pressed["state"]:
                    level_engine.rotation = LEVELS[level_id]["start_rot"] + 3.14
                    startup_trans.cancel()
                    t = 1
            else:
                key_pressed["state"] = False

            level_engine.rotation += 6.28/startup_duration
            if (t < 0.5):
                level_engine.scale(2*t*startup_scale + 1)
            else:
                level_engine.scale(2*(1-t)*startup_scale + 1)
            
            if t == 1:
                Transition(counter, 300)
        def counter(t):
            if t < 0.2:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    t = 0.2

            if t < 0.2:
                pass # wait a moment here for the viewer to enjoy
            elif t < 0.3:
                level_engine.free_rotate = False
            elif t < 0.4:
                level_engine.rotation = LEVELS[level_id]["start_rot"]
                menu_ingame_counter.text = "3"
            elif t < 0.6:
                menu_ingame_counter.text = "2"
            elif t < 0.8:
                menu_ingame_counter.text = "1"
            elif t < 1:
                menu_ingame_counter.text = "GO!"
                player.paused = False
                player.start_time = time.time()*1000
            elif t == 1:
                menu_ingame_counter.text = ""

        startup_trans = Transition(startup, startup_duration)

        menu_ingame_laps.text = str(player.lap) + "/" + str(level_engine.laps)

        Menu.hide_all_and_show(menu_ingame)

    def finish_level():
        level_id = level_select_menu.selected_button

        player.paused = True
        score = int((time.time()*1000-player.start_time)/1000)

        new_record = (score <= SAVE[level_id]["best"] or SAVE[level_id]["best"] == -1)

        if new_record:
             SAVE[level_id]["best"] = score


        menu_finished.disable_input = True

        # Making pretty much everything invisible

        menu_finished_title.text = LEVELS[level_id]["name"]
        menu_finished_sub.hidden = True
        
        # calc stars
        stars = 0
        for goal in LEVELS[level_id]["goals"]:
            if score < goal: stars += 1

        # unlock next level if not unlocked already
        if (level_id < len(LEVELS)-1) and (stars >= 1):
            SAVE[level_id+1]["is_unlocked"] = True

        menu_finished_stars.bg = img_menu_stars[stars]
        menu_finished_stars.hidden = True
        menu_finished_time.text = secs_to_mins(score)
        menu_finished_time.hidden = True
        
        menu_finished_record.hidden = True

        menu_finished_retry.hidden = True
        menu_finished_back.hidden = True

        menu_finished_curr_rec.hidden = True
        menu_finished_curr_rec.text = "Record: " + secs_to_mins(SAVE[level_id]["best"])

        Menu.hide_all_and_show(menu_finished)

        def menu_finish_pop_in(t):
            global Invert_Screen

            if t < 0.25:
                pass
            elif t < 0.5:
                menu_finished_sub.hidden = False
            elif t < 0.75:
                menu_finished_stars.hidden = False
                menu_finished_time.hidden = False
            elif t < 0.83 and new_record:
                Invert_Screen = True
            elif t < 1:
                if new_record:
                    Invert_Screen = False
                    menu_finished_record.hidden = False
                else:
                    menu_finished_curr_rec.hidden = False
                menu_finished_retry.hidden = False
                menu_finished_back.hidden = False
                menu_finished.disable_input = False


        Transition(menu_finish_pop_in, 180)


    # initialize pygame
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode(SCREEN_RES)
    pygame.display.set_caption("Corny")
    clock: pygame.time.Clock = pygame.time.Clock()

    # Nokia screen surface
    nokia = pygame.Surface(NOKIA_RES)

    # load stuff
    checker = pygame.image.load("src/img/checkerboard.png")
    player_sprite = pygame.image.load("src/img/player.png")

    # menu images
    img_blank = pygame.Surface(NOKIA_RES)
    img_blank.fill(PALETTE[1])

    img_menu_full_border = pygame.image.load("src/img/menu/full_border.png")

    img_menu_start_bg = pygame.image.load("src/img/menu/start_bg.png")
    img_menu_start_btn = pygame.image.load("src/img/menu/start_button.png")
    img_menu_keys_btn = pygame.image.load("src/img/menu/keys_button.png")

    img_menu_level_btn = pygame.image.load("src/img/menu/level_select_button.png")

    img_menu_lvl_preview_bg = pygame.image.load("src/img/menu/level_preview_bg.png")
    img_menu_stars = [
        pygame.image.load("src/img/menu/no_star.png"),
        pygame.image.load("src/img/menu/one_star.png"),
        pygame.image.load("src/img/menu/two_star.png"),
        pygame.image.load("src/img/menu/three_star.png"),
    ]
    img_menu_back_btn = pygame.image.load("src/img/menu/back_button.png")
    img_menu_retry_btn = pygame.image.load("src/img/menu/retry_button.png")
    img_menu_go_btn = pygame.image.load("src/img/menu/go_button.png")
    img_menu_next_btn = pygame.image.load("src/img/menu/next_button.png")

    img_menu_keys_menu = pygame.image.load("src/img/menu/keys_menu_bg.png")
    img_menu_keys_ingame = pygame.image.load("src/img/menu/keys_ingame_bg.png")

    # font
    pygame.font.init()
    font_ark = pygame.font.Font("src/font/Ark.ttf", 8)
    font_tiny = pygame.font.Font("src/font/Tiny.ttf", 6)

    # Start menu
    start_menu = Menu(  screen=nokia, 
                        background=img_menu_start_bg
    )
    start_button = MenuButton(
                        menu=start_menu, 
                        size=MENU_BIG_BTN_SIZE, 
                        position=Vec2(42, 25), 
                        bg_sheet=img_menu_start_btn,
                        handler=show_level_selection
    )
    ctrl_button = MenuButton(
                        menu=start_menu, 
                        size=MENU_BIG_BTN_SIZE,
                        position=Vec2(42, 40),
                        bg_sheet=img_menu_keys_btn,
                        handler=show_keys_screen,
    )

    # Level selection menu
    level_select_menu = Menu( screen=nokia,
                              background=img_blank,
                              disabled=True
    )
    
    # Confirm play menu
    level_confirm_menu = Menu(  screen=nokia,
                                background=img_menu_full_border,
                                next_btn=pygame.K_d,
                                prev_btn=pygame.K_a,
                                disabled=True
    )
    level_confirm_title = MenuButton(
                        menu=level_confirm_menu, 
                        size=MENU_LEVEL_BTN_SIZE,
                        position=Vec2(42, 8),
                        text="Sample",
                        text_color=PALETTE[0],
                        font=font_ark,
                        selectable=False
    )
    level_confirm_thumb_bg = MenuButton(
                        menu=level_confirm_menu, 
                        bg=img_menu_lvl_preview_bg,
                        size=Vec2(29,29),
                        position=Vec2(19, 28),
     
                        selectable=False
    )
    level_confirm_thumb = MenuButton(
                        menu=level_confirm_menu, 
                        size=Vec2(25, 25),
                        position=Vec2(19, 28),
                        selectable=False
    )
    level_confirm_stars = MenuButton(
                        menu=level_confirm_menu, 
                        bg=img_menu_stars[0],
                        size=Vec2(29,8),
                        position=Vec2(50, 17),
                        selectable=False
    )
    level_confirm_current_time = MenuButton(
                        menu=level_confirm_menu, 
                        size=Vec2(17,12),
                        position=Vec2(73, 17),
                        text="2:12",
                        text_color=PALETTE[0],
                        font=font_tiny,
                        selectable=False
    )
    level_confirm_next_time = MenuButton(
                        menu=level_confirm_menu, 
                        size=Vec2(48,10),
                        position=Vec2(57, 25),
                        text="Next: 1:12",
                        text_color=PALETTE[0],
                        font=font_tiny,
                        selectable=False
    )
    level_confirm_back = MenuButton(
                        menu=level_confirm_menu,
                        bg_sheet=img_menu_back_btn,
                        size=Vec2(14,14),
                        position=Vec2(45, 37),
                        handler=show_start_screen
    )
    level_confirm_menu.selected_button = 7
    level_confirm_start = MenuButton(
                        menu=level_confirm_menu,
                        bg_sheet=img_menu_go_btn,
                        size=Vec2(19,14),
                        position=Vec2(65, 37),
                        handler=play_level
    )

    # Menu displayed while playing
    menu_ingame = Menu( screen=nokia,
                        disabled=True,
                        click_btn=pygame.K_ESCAPE
                        
    )
    menu_ingame_playtime = MenuButton(
                        menu=menu_ingame, 
                        size=Vec2(28,8),
                        position=Vec2(70, 4),
                        text="0:00:000",
                        text_color=PALETTE[0],
                        font=font_tiny,
                        selectable=False
    )
    menu_ingame_counter = MenuButton(
                        menu=menu_ingame, 
                        size=Vec2(16,8),
                        position=Vec2(42,24),
                        text="",
                        text_color=PALETTE[1],
                        font=font_ark,
                        selectable=False
    )
    menu_ingame_laps = MenuButton(
                        menu=menu_ingame, 
                        size=Vec2(20,8),
                        position=Vec2(42, 4),
                        text="0/0",
                        text_color=PALETTE[0],
                        font=font_tiny,
                        selectable=False
    )
    menu_ingame.selected_button = 3
    menu_ingame_esc = MenuButton(
                        menu=menu_ingame, 
                        size=Vec2(14,14),
                        position=Vec2(8, 8),
                        handler=show_pause_screen
    )
    # Two lines for tutorial text
    menu_ingame_tut0 = MenuButton(
                        menu=menu_ingame, 
                        size=Vec2(84,8),
                        position=Vec2(42, 20),
                        bg=img_blank,
                        text="tutorial text bla bla bla",
                        text_color=PALETTE[0],
                        font=font_tiny,
                        selectable=False,
                        hidden=True,
    )
    menu_ingame_tut1 = MenuButton(
                        menu=menu_ingame, 
                        size=Vec2(84,8),
                        position=Vec2(42, 28),
                        bg=img_blank,
                        text="Line2 text bla bla bla",
                        text_color=PALETTE[0],
                        font=font_tiny,
                        selectable=False,
                        hidden=True
    )


    # pause menu
    menu_pause = Menu(  screen=nokia,
                        next_btn=pygame.K_d,
                        prev_btn=pygame.K_a,
                        disabled=True,
    )
    menu_pause_title = MenuButton(
                        menu=menu_pause, 
                        size=MENU_LEVEL_BTN_SIZE,
                        position=Vec2(42,5),
                        text="Paused",
                        text_color=PALETTE[0],
                        font=font_ark,
                        selectable=False
    )
    menu_pause_back = MenuButton(
                        menu=menu_pause,
                        bg_sheet=img_menu_back_btn,
                        size=Vec2(14,14),
                        position=Vec2(24, 24),
                        handler=show_start_screen
    )
    menu_pause.selected_button = 2
    menu_pause_go = MenuButton(
                        menu=menu_pause,
                        bg_sheet=img_menu_go_btn,
                        size=Vec2(19,14),
                        position=Vec2(42, 24),
                        handler=close_pause_screen
    )
    menu_pause_retry = MenuButton(
                        menu=menu_pause,
                        bg_sheet=img_menu_retry_btn,
                        size=Vec2(14,14),
                        position=Vec2(60, 24),
                        handler=play_level
    )

    # Menu displayed when game was finished
    menu_finished = Menu(   screen=nokia,
                            next_btn=pygame.K_d,
                            prev_btn=pygame.K_a,
                            disabled=True,
                            background=img_menu_full_border
    )
    menu_finished_title = MenuButton(
                        menu=menu_finished, 
                        size=MENU_LEVEL_BTN_SIZE,
                        position=Vec2(42, 8),
                        text="Sample",
                        text_color=PALETTE[0],
                        font=font_ark,
                        selectable=False
    )
    menu_finished_sub = MenuButton(
                        menu=menu_finished, 
                        size=MENU_LEVEL_BTN_SIZE,
                        position=Vec2(42, 14),
                        text="finished!",
                        text_color=PALETTE[0],
                        font=font_tiny,
                        selectable=False
    )
    menu_finished_stars = MenuButton(
                        menu=menu_finished, 
                        bg=img_menu_stars[0],
                        size=Vec2(29,8),
                        position=Vec2(42, 24),
                        selectable=False
    )
    menu_finished_time = MenuButton(
                        menu=menu_finished, 
                        size=Vec2(17,12),
                        position=Vec2(42, 34),
                        text="2:12",
                        text_color=PALETTE[0],
                        font=font_tiny,
                        selectable=False
    )
    menu_finished_record = MenuButton(
                        menu=menu_finished, 
                        size=Vec2(48,6),
                        position=Vec2(42, 42),
                        text="New Record!",
                        text_color=PALETTE[0],
                        font=font_tiny,
                        selectable=False
    )
    def new_record_blink():
        if menu_finished_record.text == "":
            menu_finished_record.text = "New Record!"
        else:
            menu_finished_record.text = ""
    Timer(new_record_blink, 60)

    menu_finished_curr_rec = MenuButton(
                        menu=menu_finished, 
                        size=Vec2(48,6),
                        position=Vec2(42, 42),
                        text="Record: 0:34",
                        text_color=PALETTE[0],
                        font=font_tiny,
                        selectable=False,
    )
    menu_finished_back = MenuButton(
                        menu=menu_finished,
                        bg_sheet=img_menu_back_btn,
                        size=Vec2(14,14),
                        position=Vec2(12, 24),
                        handler=show_start_screen
    )
    menu_finished.selected_button = 6
    menu_finished_retry = MenuButton(
                        menu=menu_finished,
                        bg_sheet=img_menu_retry_btn,
                        size=Vec2(14,14),
                        position=Vec2(72, 24),
                        handler=play_level
    )

    # keys menus
    menu_keys_menu = Menu(   screen=nokia,
                        next_btn=pygame.K_d,
                        prev_btn=pygame.K_a,
                        disabled=True,
                        background=img_menu_keys_menu
    )
    menu_keys_menu_back = MenuButton(
                        menu=menu_keys_menu,
                        bg_sheet=img_menu_back_btn,
                        size=Vec2(14,14),
                        position=Vec2(8, 40),
                        handler=show_start_screen
    )
    menu_keys_menu_next = MenuButton(
                        menu=menu_keys_menu,
                        bg_sheet=img_menu_next_btn,
                        size=Vec2(14,14),
                        position=Vec2(76, 40),
                        handler=show_keys_ingame_screen
    )
    menu_keys_ingame = Menu(   screen=nokia,
                        next_btn=pygame.K_d,
                        prev_btn=pygame.K_a,
                        disabled=True,
                        background=img_menu_keys_ingame
    )
    menu_keys_ingame_back = MenuButton(
                        menu=menu_keys_ingame,
                        bg_sheet=img_menu_back_btn,
                        size=Vec2(14,14),
                        position=Vec2(8, 40),
                        handler=show_keys_screen
    )

    # dev logo splash screen
    menu_dev_logo = Menu(screen=nokia,disable_input=True)
    def dev_logo_anim(t):
        global Invert_Screen

        logo = dev_logo
        if (t < 0.1):
            logo = img_blank
        elif (t < 0.2):
            Invert_Screen = True
        elif (t < 0.8):
            Invert_Screen = False
        elif (t < 0.9):
            Invert_Screen = True
        elif (t <= 1):
            Invert_Screen = False
            logo = img_blank
        
        menu_dev_logo.background = logo

        if (t == 1): 
            Transition(show_keys_after_dev, 100)

    def show_keys_after_dev(t):
        Menu.hide_all_and_show(menu_keys_menu)
        menu_keys_menu.buttons[0].hidden = True
        menu_keys_menu.buttons[1].hidden = True
        menu_keys_menu.disable_input = True

        if t == 1:
            menu_keys_menu.buttons[0].hidden = False
            menu_keys_menu.buttons[1].hidden = False
            menu_keys_menu.disable_input = False
            Menu.hide_all_and_show(start_menu)

    dev_logo = pygame.image.load("src/img/dev_logo.png")
    Transition(dev_logo_anim, 120)


    # init
    Menu.hide_all_and_show(menu_dev_logo)

    # init player and engine
    level_engine = Level(checker, checker, pygame.Surface(BOTTOM_SCREEN_RES))
    # level.free_rotate = True
    # level.free_move = True

    player = Player(level_engine, Vec2(64,64), Vec2(16,16), player_sprite)
    player.paused = True

    #finish_level()

    while Game_Running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
        pygame.event.pump()
        nokia.fill(PALETTE[1])
        clock.tick(60)

        # Update timer instances
        for timer in Timer.instances:
            timer.update()
        
        # in a race
        if not player.paused:
            menu_ingame_laps.text = str(player.lap) + "/" + str(level_engine.laps)
            menu_ingame_playtime.text = milisecs_to_mins(time.time()*1000-player.start_time)
            if player.lap > level_engine.laps: finish_level()
        else:
            # incase of pause menu
            player.start_time += (1/60)*1000

        player.update()
        level_engine.project()
        nokia.blit(level_engine.output, BOTTOM_SCREEN_OFFSET)
        # do stuff with nokia
        # ...


        # update all menus, updated lastly to be on top
        for menu in Menu.instances:
            menu.update()

        # invert screen
        if Invert_Screen:
            invert(nokia)

        screen.blit(pygame.transform.scale(nokia, SCREEN_RES), (0,0))
        pygame.display.update()

if __name__ == "__main__":
    asyncio.run(main())