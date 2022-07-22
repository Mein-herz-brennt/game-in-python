import math
import random

import pygame
import pygame_menu
from pygame_menu.examples import create_example_window
from pygame import mixer
from random import randrange
from typing import Tuple, Any, Optional, List

# import sched

# game constants
WIDTH = 800
HEIGHT = 600


def start_the_game():
    # global variables
    running = True
    pause_state = 0
    score = 0
    highest_score = 0
    life = 3
    kills = 0
    difficulty = 1
    level = 1
    max_kills_to_difficulty_up = 5
    max_difficulty_to_level_up = 5
    initial_player_velocity = 3.0
    initial_enemy_velocity = 1.0
    weapon_shot_velocity = 5.0
    single_frame_rendering_time = 0
    total_time = 0
    frame_count = 0
    fps = 0

    # game objects
    player = type('Player', (), {})()
    bullet = type('Bullet', (), {})()
    enemies = []
    lasers = []

    # initialize pygame
    pygame.init()

    # Input key states (keyboard)
    LEFT_ARROW_KEY_PRESSED = 0
    RIGHT_ARROW_KEY_PRESSED = 0
    UP_ARROW_KEY_PRESSED = 0
    SPACE_BAR_PRESSED = 0
    ENTER_KEY_PRESSED = 0
    ESC_KEY_PRESSED = 0

    # create display window
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Counter-Doge")

    window_icon = pygame.image.load("C:/diploma/dogegame/snack.png")
    pygame.display.set_icon(window_icon)

    # game sounds
    pause_sound = None
    level_up_sound = None
    weapon_annihilation_sound = None
    game_over_sound = None

    # create background
    background_img = pygame.image.load("C:/diploma/dogegame/bvar3.png")  # 800 x 600 px image
    background_music_paths = ["C:/diploma/dogegame/backmusic.wav"]

    def init_background_music():
        if difficulty == 1:
            mixer.quit()
            mixer.init()
        if difficulty <= 6:
            mixer.music.load(background_music_paths[difficulty - 1])
        else:
            mixer.music.load(background_music_paths[5])
        mixer.music.play(-1)

    # create player class
    class Player:
        def __init__(self, img_path, width, height, x, y, dx, dy, kill_sound_path):
            self.img_path = img_path
            self.img = pygame.image.load(self.img_path)
            self.width = width
            self.height = height
            self.x = x
            self.y = y
            self.dx = dx
            self.dy = dy
            self.kill_sound_path = kill_sound_path
            self.kill_sound = mixer.Sound(self.kill_sound_path)

        def draw(self):
            window.blit(self.img, (self.x, self.y))

    # create enemy class
    class Enemy:
        def __init__(self, img_path, width, height, x, y, dx, dy, kill_sound_path):
            self.img_path = img_path
            self.img = pygame.image.load(self.img_path)
            self.width = width
            self.height = height
            self.x = x
            self.y = y
            self.dx = dx
            self.dy = dy
            self.kill_sound_path = kill_sound_path
            self.kill_sound = mixer.Sound(self.kill_sound_path)

        def draw(self):
            window.blit(self.img, (self.x, self.y))

    # create bullet class
    class Bullet:
        def __init__(self, img_path, width, height, x, y, dx, dy, fire_sound_path):
            self.img_path = img_path
            self.img = pygame.image.load(self.img_path)
            self.width = width
            self.height = height
            self.x = x
            self.y = y
            self.dx = dx
            self.dy = dy
            self.fired = False
            self.fire_sound_path = fire_sound_path
            self.fire_sound = mixer.Sound(self.fire_sound_path)

        def draw(self):
            if self.fired:
                window.blit(self.img, (self.x, self.y))

    # create laser class
    class Laser:
        def __init__(self, img_path, width, height, x, y, dx, dy, shoot_probability, relaxation_time, beam_sound_path):
            self.img_path = img_path
            self.img = pygame.image.load(self.img_path)
            self.width = width
            self.height = height
            self.x = x
            self.y = y
            self.dx = dx
            self.dy = dy
            self.beamed = False
            self.shoot_probability = shoot_probability
            self.shoot_timer = 0
            self.relaxation_time = relaxation_time
            self.beam_sound_path = beam_sound_path
            self.beam_sound = mixer.Sound(self.beam_sound_path)

        def draw(self):
            if self.beamed:
                window.blit(self.img, (self.x, self.y))

    def scoreboard():
        x_offset = 10
        y_offset = 10
        # set font type and size
        font = pygame.font.SysFont("calibre", 16)

        # render font and text sprites
        score_sprint = font.render("SCORE : " + str(score), True, (255, 255, 255))
        highest_score_sprint = font.render("HI-SCORE : " + str(highest_score), True, (255, 255, 255))
        level_sprint = font.render("LEVEL : " + str(level), True, (255, 255, 255))
        difficulty_sprint = font.render("DIFFICULTY : " + str(difficulty), True, (255, 255, 255))
        life_sprint = font.render("LIFE LEFT : " + str(life) + " | " + ("@ " * life), True, (255, 255, 255))

        # performance info
        fps_sprint = font.render("FPS : " + str(fps), True, (255, 255, 255))
        frame_time_in_ms = round(single_frame_rendering_time * 1000, 2)
        frame_time_sprint = font.render("FT : " + str(frame_time_in_ms) + " ms", True, (255, 255, 255))

        # place the font sprites on the screen
        window.blit(score_sprint, (x_offset, y_offset))
        window.blit(highest_score_sprint, (x_offset, y_offset + 20))
        window.blit(level_sprint, (x_offset, y_offset + 40))
        window.blit(difficulty_sprint, (x_offset, y_offset + 60))
        window.blit(life_sprint, (x_offset, y_offset + 80))
        window.blit(fps_sprint, (WIDTH - 80, y_offset))
        window.blit(frame_time_sprint, (WIDTH - 80, y_offset + 20))

    def collision_check(object1, object2):
        x1_cm = object1.x + object1.width / 2
        y1_cm = object1.y + object1.width / 2
        x2_cm = object2.x + object2.width / 2
        y2_cm = object2.y + object2.width / 2
        distance = math.sqrt(math.pow((x2_cm - x1_cm), 2) + math.pow((y2_cm - y1_cm), 2))
        return distance < ((object1.width + object2.width) / 2)

    # def collision_check(object1_x, object1_y, object1_diameter, object2_x, object2_y, object2_diameter):
    #     x1_cm = object1_x + object1_diameter / 2
    #     y1_cm = object1_y + object1_diameter / 2
    #     x2_cm = object2_x + object2_diameter / 2
    #     y2_cm = object2_y + object2_diameter / 2
    #     distance = math.sqrt(math.pow((x2_cm - x1_cm), 2) + math.pow((y2_cm - y1_cm), 2))
    #     return distance < ((object1_diameter + object2_diameter) / 2)

    def level_up():
        global life
        global level
        global difficulty
        global max_difficulty_to_level_up
        level_up_sound.play()
        level += 1
        life += 1  # grant a life
        difficulty = 1  # reset difficulty
        # TODO: change player and bullet speeds, enemy laser speed and firing probability wrt level
        #  come up with interesting gameplay ideas.
        #  variables in hand:
        #  1. speed of weapons
        #  2. enemy (up to 6) & player velocity
        #  3. laser firing probability
        #  future ideas:
        #  1. add new type of enemies
        #  2. add new player spaceship and bullets!
        #  future features:
        #  1. create player profile ad store highest score to DB
        #  2. multiplayer
        if level % 3 == 0:
            player.dx += 1
            bullet.dy += 1
            max_difficulty_to_level_up += 1
            for each_laser in lasers:
                each_laser.shoot_probability += 0.1
                if each_laser.shoot_probability > 1.0:
                    each_laser.shoot_probability = 1.0
        if max_difficulty_to_level_up > 7:
            max_difficulty_to_level_up = 7

        font = pygame.font.SysFont("freesansbold", 64)
        gameover_sprint = font.render("LEVEL UP", True, (255, 255, 255))
        window.blit(gameover_sprint, (WIDTH / 2 - 120, HEIGHT / 2 - 32))
        pygame.display.update()
        init_game()
        time.sleep(1.0)

    def respawn(enemy_obj):
        enemy_obj.x = random.randint(0, (WIDTH - enemy_obj.width))
        enemy_obj.y = random.randint(((HEIGHT / 10) * 1 - (enemy_obj.height / 2)),
                                     ((HEIGHT / 10) * 4 - (enemy_obj.height / 2)))

    def kill_enemy(player_obj, bullet_obj, enemy_obj):
        global score
        global kills
        global difficulty
        bullet_obj.fired = False
        enemy_obj.kill_sound.play()
        bullet_obj.x = player_obj.x + player_obj.width / 2 - bullet_obj.width / 2
        bullet_obj.y = player_obj.y + bullet_obj.height / 2
        score = score + 10 * difficulty * level
        kills += 1
        if kills % max_kills_to_difficulty_up == 0:
            difficulty += 1
            if (difficulty == max_difficulty_to_level_up) and (life != 0):
                level_up()
            init_background_music()
        print("Score:", score)
        print("level:", level)
        print("difficulty:", difficulty)
        respawn(enemy_obj)

    def rebirth(player_obj):
        player_obj.x = (WIDTH / 2) - (player_obj.width / 2)
        player_obj.y = (HEIGHT / 10) * 9 - (player_obj.height / 2)

    def gameover_screen():
        scoreboard()
        font = pygame.font.SysFont("freesansbold", 64)
        gameover_sprint = font.render("GAME OVER", True, (0, 0, 0))
        window.blit(gameover_sprint, (WIDTH / 2 - 140, HEIGHT / 2 - 32))
        pygame.display.update()

        mixer.music.stop()
        game_over_sound.play()
        time.sleep(13.0)
        mixer.quit()

    def gameover():
        global running
        global score
        global highest_score

        if score > highest_score:
            highest_score = score

        # console display
        print("----------------")
        print("GAME OVER !!")
        print("----------------")
        print("you died at")
        print("Level:", level)
        print("difficulty:", difficulty)
        print("Your Score:", score)
        print("----------------")
        print("Try Again !!")
        print("----------------")
        running = False
        gameover_screen()

    def kill_player(player_obj, enemy_obj, laser_obj):
        global life
        laser_obj.beamed = False
        player_obj.kill_sound.play()
        laser_obj.x = enemy_obj.x + enemy_obj.width / 2 - laser_obj.width / 2
        laser_obj.y = enemy_obj.y + laser_obj.height / 2
        life -= 1
        print("Life Left:", life)
        if life > 0:
            rebirth(player_obj)
        else:
            gameover()

    def destroy_weapons(player_obj, bullet_obj, enemy_obj, laser_obj):
        bullet_obj.fired = False
        laser_obj.beamed = False
        weapon_annihilation_sound.play()
        bullet_obj.x = player_obj.x + player_obj.width / 2 - bullet_obj.width / 2
        bullet_obj.y = player_obj.y + bullet_obj.height / 2
        laser_obj.x = enemy_obj.x + enemy_obj.width / 2 - laser_obj.width / 2
        laser_obj.y = enemy_obj.y + laser_obj.height / 2

    # timer = sched.scheduler(time.time, time.sleep)
    #
    #
    # def calculate_fps(sc):
    #     global frame_count
    #     fps = frame_count
    #     print("FPS =", fps)
    #     frame_count = 0
    #     timer.enter(60, 1, calculate_fps, (sc,))
    #
    #
    # timer.enter(60, 1, calculate_fps, (timer, ))
    # timer.run()

    def pause_game():
        pause_sound.play()
        scoreboard()
        font = pygame.font.SysFont("freesansbold", 64)
        gameover_sprint = font.render("PAUSED", True, (0, 0, 0))
        window.blit(gameover_sprint, (WIDTH / 2 - 80, HEIGHT / 2 - 32))
        pygame.display.update()
        mixer.music.pause()

    def init_game():
        global pause_sound
        global level_up_sound
        global game_over_sound
        global weapon_annihilation_sound

        pause_sound = mixer.Sound("C:/diploma/dogegame/pause.wav")
        level_up_sound = mixer.Sound("C:/diploma/dogegame/1up.wav")
        game_over_sound = mixer.Sound("C:/diploma/dogegame/gameover.wav")
        weapon_annihilation_sound = mixer.Sound("C:/diploma/dogegame/annihilation.wav")

        # player
        player_img_path = "C:/diploma/dogegame/doge.png"  # 64 x 64 px image
        player_width = 64
        player_height = 64
        player_x = (WIDTH / 2) - (player_width / 2)
        player_y = (HEIGHT / 10) * 9 - (player_height / 2)
        player_dx = initial_player_velocity
        player_dy = 0
        player_kill_sound_path = "C:/diploma/dogegame/bark.wav"

        global player
        player = Player(player_img_path, player_width, player_height, player_x, player_y, player_dx, player_dy,
                        player_kill_sound_path)

        # bullet
        bullet_img_path = "C:/diploma/dogegame/bullet2.png"  # 32 x 32 px image
        bullet_width = 32
        bullet_height = 32
        bullet_x = player_x + player_width / 2 - bullet_width / 2
        bullet_y = player_y + bullet_height / 2
        bullet_dx = 0
        bullet_dy = weapon_shot_velocity
        bullet_fire_sound_path = "C:/diploma/dogegame/ak.wav"

        global bullet
        bullet = Bullet(bullet_img_path, bullet_width, bullet_height, bullet_x, bullet_y, bullet_dx, bullet_dy,
                        bullet_fire_sound_path)

        # enemy (number of enemy = level number)
        enemy_img_path = "C:/diploma/dogegame/kit3.png"  # 64 x 64 px image
        enemy_width = 64
        enemy_height = 64
        enemy_dx = initial_enemy_velocity
        enemy_dy = (HEIGHT / 10) / 2
        enemy_kill_sound_path = "C:/diploma/dogegame/kill.wav"

        # laser beam (equals number of enemies and retains corresponding enemy position)
        laser_img_path = "C:/diploma/dogegame/beam.png"  # 24 x 24 px image
        laser_width = 24
        laser_height = 24
        laser_dx = 0
        laser_dy = weapon_shot_velocity
        shoot_probability = 0.3
        relaxation_time = 100
        laser_beam_sound_path = "C:/diploma/dogegame/meow.wav"

        global enemies
        global lasers

        enemies.clear()
        lasers.clear()

        for lev in range(level):
            enemy_x = random.randint(0, (WIDTH - enemy_width))
            enemy_y = random.randint(((HEIGHT / 10) * 1 - (enemy_height / 2)), ((HEIGHT / 10) * 4 - (enemy_height / 2)))
            laser_x = enemy_x + enemy_width / 2 - laser_width / 2
            laser_y = enemy_y + laser_height / 2

            enemy_obj = Enemy(enemy_img_path, enemy_width, enemy_height, enemy_x, enemy_y, enemy_dx, enemy_dy,
                              enemy_kill_sound_path)
            enemies.append(enemy_obj)

            laser_obj = Laser(laser_img_path, laser_width, laser_height, laser_x, laser_y, laser_dx, laser_dy,
                              shoot_probability, relaxation_time, laser_beam_sound_path)
            lasers.append(laser_obj)

    # init game
    init_game()
    init_background_music()
    runned_once = False

    # main game loop begins
    while running:
        # start of frame timing
        start_time = time.time()

        # background
        window.fill((0, 0, 0))
        window.blit(background_img, (0, 0))

        # register events
        for event in pygame.event.get():
            # Quit Event
            if event.type == pygame.QUIT:
                running = False

            # Keypress Down Event
            if event.type == pygame.KEYDOWN:
                # Left Arrow Key down
                if event.key == pygame.K_LEFT:
                    print("LOG: Left Arrow Key Pressed Down")
                    LEFT_ARROW_KEY_PRESSED = 1
                # Right Arrow Key down
                if event.key == pygame.K_RIGHT:
                    print("LOG: Right Arrow Key Pressed Down")
                    RIGHT_ARROW_KEY_PRESSED = 1
                # Up Arrow Key down
                if event.key == pygame.K_UP:
                    print("LOG: Up Arrow Key Pressed Down")
                    UP_ARROW_KEY_PRESSED = 1
                # Space Bar down
                if event.key == pygame.K_SPACE:
                    print("LOG: Space Bar Pressed Down")
                    SPACE_BAR_PRESSED = 1
                # Enter Key down ("Carriage RETURN key" from old typewriter lingo)
                if event.key == pygame.K_RETURN:
                    print("LOG: Enter Key Pressed Down")
                    ENTER_KEY_PRESSED = 1
                    pause_state += 1
                # Esc Key down
                if event.key == pygame.K_ESCAPE:
                    print("LOG: Escape Key Pressed Down")
                    ESC_KEY_PRESSED = 1
                    pause_state += 1

            # Keypress Up Event
            if event.type == pygame.KEYUP:
                # Right Arrow Key up
                if event.key == pygame.K_RIGHT:
                    print("LOG: Right Arrow Key Released")
                    RIGHT_ARROW_KEY_PRESSED = 0
                # Left Arrow Key up
                if event.key == pygame.K_LEFT:
                    print("LOG: Left Arrow Key Released")
                    LEFT_ARROW_KEY_PRESSED = 0
                # Up Arrow Key up
                if event.key == pygame.K_UP:
                    print("LOG: Up Arrow Key Released")
                    UP_ARROW_KEY_PRESSED = 0
                # Space Bar up
                if event.key == pygame.K_SPACE:
                    print("LOG: Space Bar Released")
                    SPACE_BAR_PRESSED = 0
                # Enter Key up ("Carriage RETURN key" from old typewriter lingo)
                if event.key == pygame.K_RETURN:
                    print("LOG: Enter Key Released")
                    ENTER_KEY_PRESSED = 0
                # Esc Key up
                if event.key == pygame.K_ESCAPE:
                    print("LOG: Escape Key Released")
                    ESC_KEY_PRESSED = 0

        # check for pause game event
        if pause_state == 2:
            pause_state = 0
            runned_once = False
            mixer.music.unpause()
        if pause_state == 1:
            if not runned_once:
                runned_once = True
                pause_game()
            continue
        # manipulate game objects based on events and player actions
        # player spaceship movement
        if RIGHT_ARROW_KEY_PRESSED:
            player.x += player.dx
        if LEFT_ARROW_KEY_PRESSED:
            player.x -= player.dx
        # bullet firing
        if (SPACE_BAR_PRESSED or UP_ARROW_KEY_PRESSED) and not bullet.fired:
            bullet.fired = True
            bullet.fire_sound.play()
            bullet.x = player.x + player.width / 2 - bullet.width / 2
            bullet.y = player.y + bullet.height / 2
        # bullet movement
        if bullet.fired:
            bullet.y -= bullet.dy

        # iter through every enemies and lasers
        for i in range(len(enemies)):
            # laser beaming
            if not lasers[i].beamed:
                lasers[i].shoot_timer += 1
                if lasers[i].shoot_timer == lasers[i].relaxation_time:
                    lasers[i].shoot_timer = 0
                    random_chance = random.randint(0, 100)
                    if random_chance <= (lasers[i].shoot_probability * 100):
                        lasers[i].beamed = True
                        lasers[i].beam_sound.play()
                        lasers[i].x = enemies[i].x + enemies[i].width / 2 - lasers[i].width / 2
                        lasers[i].y = enemies[i].y + lasers[i].height / 2
            # enemy movement
            enemies[i].x += enemies[i].dx * float(2 ** (difficulty - 1))
            # laser movement
            if lasers[i].beamed:
                lasers[i].y += lasers[i].dy

        # collision check
        for i in range(len(enemies)):
            bullet_enemy_collision = collision_check(bullet, enemies[i])
            if bullet_enemy_collision:
                kill_enemy(player, bullet, enemies[i])

        for i in range(len(lasers)):
            laser_player_collision = collision_check(lasers[i], player)
            if laser_player_collision:
                kill_player(player, enemies[i], lasers[i])

        for i in range(len(enemies)):
            enemy_player_collision = collision_check(enemies[i], player)
            if enemy_player_collision:
                kill_enemy(player, bullet, enemies[i])
                kill_player(player, enemies[i], lasers[i])

        for i in range(len(lasers)):
            bullet_laser_collision = collision_check(bullet, lasers[i])
            if bullet_laser_collision:
                destroy_weapons(player, bullet, enemies[i], lasers[i])

        # boundary check: 0 <= x <= WIDTH, 0 <= y <= HEIGHT
        # player spaceship
        if player.x < 0:
            player.x = 0
        if player.x > WIDTH - player.width:
            player.x = WIDTH - player.width
        # enemy
        for enemy in enemies:
            if enemy.x <= 0:
                enemy.dx = abs(enemy.dx) * 1
                enemy.y += enemy.dy
            if enemy.x >= WIDTH - enemy.width:
                enemy.dx = abs(enemy.dx) * -1
                enemy.y += enemy.dy
        # bullet
        if bullet.y < 0:
            bullet.fired = False
            bullet.x = player.x + player.width / 2 - bullet.width / 2
            bullet.y = player.y + bullet.height / 2
        # laser
        for i in range(len(lasers)):
            if lasers[i].y > HEIGHT:
                lasers[i].beamed = False
                lasers[i].x = enemies[i].x + enemies[i].width / 2 - lasers[i].width / 2
                lasers[i].y = enemies[i].y + lasers[i].height / 2

        # create frame by placing objects on the surface
        scoreboard()
        for laser in lasers:
            laser.draw()
        for enemy in enemies:
            enemy.draw()
        bullet.draw()
        player.draw()

        # render the display
        pygame.display.update()

        # end of rendering, end on a frame
        frame_count += 1
        end_time = time.time()
        single_frame_rendering_time = end_time - start_time
        # fps = 1 / render_time

        total_time = total_time + single_frame_rendering_time
        if total_time >= 1.0:
            fps = frame_count
            frame_count = 0
            total_time = 0


pass
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------MENU
ABOUT = ['Counter-Doge'.format(pygame_menu.__version__),
         'Розробник: Helgh'.format(pygame_menu.__author__),
         'Email: helghacc@gmail.com'.format(pygame_menu.__email__)]
DIFFICULTY = ['EASY']
FPS = 60
WINDOW_SIZE = (640, 480)

clock: Optional['pygame.time.Clock'] = None
main_menu: Optional['pygame_menu.Menu'] = None
surface: Optional['pygame.Surface'] = None


# -----------------------------------------------------------------------------
# Methods
# -----------------------------------------------------------------------------
def change_difficulty(value: Tuple[Any, int], difficulty: str) -> None:
    """
    Change difficulty of the game.
    :param value: Tuple containing the data of the selected object
    :param difficulty: Optional parameter passed as argument to add_selector
    """
    selected, index = value
    print('Selected difficulty: "{0}" ({1}) at index {2}'
          ''.format(selected, difficulty, index))
    DIFFICULTY[0] = difficulty


def random_color() -> Tuple[int, int, int]:
    """
    Return a random color.
    :return: Color tuple
    """
    return randrange(0, 255), randrange(0, 255), randrange(0, 255)


def play_function(difficulty: List, font: 'pygame.font.Font', test: bool = False) -> None:
    """
    Main game function.
    :param difficulty: Difficulty of the game
    :param font: Pygame font
    :param test: Test method, if ``True`` only one loop is allowed
    :return: None
    """
    assert isinstance(difficulty, list)
    difficulty = difficulty[0]
    assert isinstance(difficulty, str)

    # Define globals
    global main_menu
    global clock

    if difficulty == 'EASY':
        f = font.render('Playing as a baby (easy)', True, (255, 255, 255))
    elif difficulty == 'MEDIUM':
        f = font.render('Playing as a kid (medium)', True, (255, 255, 255))
    elif difficulty == 'HARD':
        f = font.render('Playing as a champion (hard)', True, (255, 255, 255))
    else:
        raise Exception('unknown difficulty {0}'.format(difficulty))
    WIDTH = 800


HEIGHT = 600

# global variables
running = True
pause_state = 0
score = 0
highest_score = 0
life = 3
kills = 0
difficulty = 1
level = 8
max_kills_to_difficulty_up = 50
max_difficulty_to_level_up = 5
initial_player_velocity = 3.0
initial_enemy_velocity = 1.0
weapon_shot_velocity = 5.0
single_frame_rendering_time = 0
total_time = 0
frame_count = 0
fps = 0

# game objects
player = type('Player', (), {})()
bullet = type('Bullet', (), {})()
enemies = []
lasers = []

# initialize pygame
pygame.init()

# Input key states (keyboard)
LEFT_ARROW_KEY_PRESSED = 0
RIGHT_ARROW_KEY_PRESSED = 0
UP_ARROW_KEY_PRESSED = 0
SPACE_BAR_PRESSED = 0
ENTER_KEY_PRESSED = 0
ESC_KEY_PRESSED = 0

# create display window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Counter-Doge")
window_icon = pygame.image.load("C:/diploma/dogegame/snack.png")
pygame.display.set_icon(window_icon)

# game sounds
pause_sound = None
level_up_sound = None
weapon_annihilation_sound = None
game_over_sound = None

# create background
background_img = pygame.image.load("C:/diploma/dogegame/bvar3.png")  # 800 x 600 px image
background_music_paths = ["C:/diploma/dogegame/backmusic.wav"]


def init_background_music():
    if difficulty == 1:
        mixer.quit()
        mixer.init()
    if difficulty <= 6:
        mixer.music.load(background_music_paths[difficulty - 1])
    else:
        mixer.music.load(background_music_paths[5])
    mixer.music.play(-1)


# create player class
class Player:
    def __init__(self, img_path, width, height, x, y, dx, dy, kill_sound_path):
        self.img_path = img_path
        self.img = pygame.image.load(self.img_path)
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.kill_sound_path = kill_sound_path
        self.kill_sound = mixer.Sound(self.kill_sound_path)

    def draw(self):
        window.blit(self.img, (self.x, self.y))


# create enemy class
class Enemy:
    def __init__(self, img_path, width, height, x, y, dx, dy, kill_sound_path):
        self.img_path = img_path
        self.img = pygame.image.load(self.img_path)
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.kill_sound_path = kill_sound_path
        self.kill_sound = mixer.Sound(self.kill_sound_path)

    def draw(self):
        window.blit(self.img, (self.x, self.y))


# create bullet class
class Bullet:
    def __init__(self, img_path, width, height, x, y, dx, dy, fire_sound_path):
        self.img_path = img_path
        self.img = pygame.image.load(self.img_path)
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.fired = False
        self.fire_sound_path = fire_sound_path
        self.fire_sound = mixer.Sound(self.fire_sound_path)

    def draw(self):
        if self.fired:
            window.blit(self.img, (self.x, self.y))


# create laser class
class Laser:
    def __init__(self, img_path, width, height, x, y, dx, dy, shoot_probability, relaxation_time, beam_sound_path):
        self.img_path = img_path
        self.img = pygame.image.load(self.img_path)
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.beamed = False
        self.shoot_probability = shoot_probability
        self.shoot_timer = 0
        self.relaxation_time = relaxation_time
        self.beam_sound_path = beam_sound_path
        self.beam_sound = mixer.Sound(self.beam_sound_path)

    def draw(self):
        if self.beamed:
            window.blit(self.img, (self.x, self.y))


def scoreboard():
    x_offset = 10
    y_offset = 10
    # set font type and size
    font = pygame.font.SysFont("calibre", 16)

    # render font and text sprites
    score_sprint = font.render("SCORE : " + str(score), True, (255, 255, 255))
    highest_score_sprint = font.render("HI-SCORE : " + str(highest_score), True, (255, 255, 255))
    level_sprint = font.render("LEVEL : " + str(level), True, (255, 255, 255))
    difficulty_sprint = font.render("DIFFICULTY : " + str(difficulty), True, (255, 255, 255))
    life_sprint = font.render("LIFE LEFT : " + str(life) + " | " + ("@ " * life), True, (255, 255, 255))

    # performance info
    fps_sprint = font.render("FPS : " + str(fps), True, (255, 255, 255))
    frame_time_in_ms = round(single_frame_rendering_time * 1000, 2)
    frame_time_sprint = font.render("FT : " + str(frame_time_in_ms) + " ms", True, (255, 255, 255))

    # place the font sprites on the screen
    window.blit(score_sprint, (x_offset, y_offset))
    window.blit(highest_score_sprint, (x_offset, y_offset + 20))
    window.blit(level_sprint, (x_offset, y_offset + 40))
    window.blit(difficulty_sprint, (x_offset, y_offset + 60))
    window.blit(life_sprint, (x_offset, y_offset + 80))
    window.blit(fps_sprint, (WIDTH - 80, y_offset))
    window.blit(frame_time_sprint, (WIDTH - 80, y_offset + 20))


def collision_check(object1, object2):
    x1_cm = object1.x + object1.width / 2
    y1_cm = object1.y + object1.width / 2
    x2_cm = object2.x + object2.width / 2
    y2_cm = object2.y + object2.width / 2
    distance = math.sqrt(math.pow((x2_cm - x1_cm), 2) + math.pow((y2_cm - y1_cm), 2))
    return distance < ((object1.width + object2.width) / 2)


# def collision_check(object1_x, object1_y, object1_diameter, object2_x, object2_y, object2_diameter):
#     x1_cm = object1_x + object1_diameter / 2
#     y1_cm = object1_y + object1_diameter / 2
#     x2_cm = object2_x + object2_diameter / 2
#     y2_cm = object2_y + object2_diameter / 2
#     distance = math.sqrt(math.pow((x2_cm - x1_cm), 2) + math.pow((y2_cm - y1_cm), 2))
#     return distance < ((object1_diameter + object2_diameter) / 2)


def level_up():
    global life
    global level
    global difficulty
    global max_difficulty_to_level_up
    level_up_sound.play()
    level += 1
    life += 1  # grant a life
    difficulty = 1  # reset difficulty
    # TODO: change player and bullet speeds, enemy laser speed and firing probability wrt level
    #  come up with interesting gameplay ideas.
    #  variables in hand:
    #  1. speed of weapons
    #  2. enemy (up to 6) & player velocity
    #  3. laser firing probability
    #  future ideas:
    #  1. add new type of enemies
    #  2. add new player spaceship and bullets!
    #  future features:
    #  1. create player profile ad store highest score to DB
    #  2. multiplayer
    if level % 3 == 0:
        player.dx += 1
        bullet.dy += 1
        max_difficulty_to_level_up += 1
        for each_laser in lasers:
            each_laser.shoot_probability += 0.1
            if each_laser.shoot_probability > 1.0:
                each_laser.shoot_probability = 1.0
    if max_difficulty_to_level_up > 7:
        max_difficulty_to_level_up = 7

    font = pygame.font.SysFont("freesansbold", 64)
    gameover_sprint = font.render("LEVEL UP", True, (255, 255, 255))
    window.blit(gameover_sprint, (WIDTH / 2 - 120, HEIGHT / 2 - 32))
    pygame.display.update()
    init_game()
    time.sleep(1.0)


def respawn(enemy_obj):
    enemy_obj.x = random.randint(0, (WIDTH - enemy_obj.width))
    enemy_obj.y = random.randint(((HEIGHT / 10) * 1 - (enemy_obj.height / 2)),
                                 ((HEIGHT / 10) * 4 - (enemy_obj.height / 2)))


def kill_enemy(player_obj, bullet_obj, enemy_obj):
    global score
    global kills
    global difficulty
    bullet_obj.fired = False
    enemy_obj.kill_sound.play()
    bullet_obj.x = player_obj.x + player_obj.width / 2 - bullet_obj.width / 2
    bullet_obj.y = player_obj.y + bullet_obj.height / 2
    score = score + 10 * difficulty * level
    kills += 1
    if kills % max_kills_to_difficulty_up == 0:
        difficulty += 1
        if (difficulty == max_difficulty_to_level_up) and (life != 0):
            level_up()
        init_background_music()
    print("Score:", score)
    print("level:", level)
    print("difficulty:", difficulty)
    respawn(enemy_obj)


def rebirth(player_obj):
    player_obj.x = (WIDTH / 2) - (player_obj.width / 2)
    player_obj.y = (HEIGHT / 10) * 9 - (player_obj.height / 2)


def gameover_screen():
    scoreboard()
    font = pygame.font.SysFont("freesansbold", 64)
    gameover_sprint = font.render("GAME OVER", True, (0, 0, 0))
    window.blit(gameover_sprint, (WIDTH / 2 - 140, HEIGHT / 2 - 32))
    pygame.display.update()

    mixer.music.stop()
    game_over_sound.play()
    time.sleep(13.0)
    mixer.quit()


def gameover():
    global running
    global score
    global highest_score

    if score > highest_score:
        highest_score = score

    # console display
    print("----------------")
    print("GAME OVER !!")
    print("----------------")
    print("you died at")
    print("Level:", level)
    print("difficulty:", difficulty)
    print("Your Score:", score)
    print("----------------")
    print("Try Again !!")
    print("----------------")
    running = False
    gameover_screen()


def kill_player(player_obj, enemy_obj, laser_obj):
    global life
    laser_obj.beamed = False
    player_obj.kill_sound.play()
    laser_obj.x = enemy_obj.x + enemy_obj.width / 2 - laser_obj.width / 2
    laser_obj.y = enemy_obj.y + laser_obj.height / 2
    life -= 1
    print("Life Left:", life)
    if life > 0:
        rebirth(player_obj)
    else:
        gameover()


def destroy_weapons(player_obj, bullet_obj, enemy_obj, laser_obj):
    bullet_obj.fired = False
    laser_obj.beamed = False
    weapon_annihilation_sound.play()
    bullet_obj.x = player_obj.x + player_obj.width / 2 - bullet_obj.width / 2
    bullet_obj.y = player_obj.y + bullet_obj.height / 2
    laser_obj.x = enemy_obj.x + enemy_obj.width / 2 - laser_obj.width / 2
    laser_obj.y = enemy_obj.y + laser_obj.height / 2


# timer = sched.scheduler(time.time, time.sleep)
#
#
# def calculate_fps(sc):
#     global frame_count
#     fps = frame_count
#     print("FPS =", fps)
#     frame_count = 0
#     timer.enter(60, 1, calculate_fps, (sc,))
#
#
# timer.enter(60, 1, calculate_fps, (timer, ))
# timer.run()


def pause_game():
    pause_sound.play()
    scoreboard()
    font = pygame.font.SysFont("freesansbold", 64)
    gameover_sprint = font.render("PAUSED", True, (0, 0, 0))
    window.blit(gameover_sprint, (WIDTH / 2 - 80, HEIGHT / 2 - 32))
    pygame.display.update()
    mixer.music.pause()


def init_game():
    global pause_sound
    global level_up_sound
    global game_over_sound
    global weapon_annihilation_sound

    pause_sound = mixer.Sound("C:/diploma/dogegame/pause.wav")
    level_up_sound = mixer.Sound("C:/diploma/dogegame/1up.wav")
    game_over_sound = mixer.Sound("C:/diploma/dogegame/gameover.wav")
    weapon_annihilation_sound = mixer.Sound("C:/diploma/dogegame/annihilation.wav")

    # player
    player_img_path = "C:/diploma/dogegame/doge.png"  # 64 x 64 px image
    player_width = 64
    player_height = 64
    player_x = (WIDTH / 2) - (player_width / 2)
    player_y = (HEIGHT / 10) * 9 - (player_height / 2)
    player_dx = initial_player_velocity
    player_dy = 0
    player_kill_sound_path = "C:/diploma/dogegame/bark.wav"

    global player
    player = Player(player_img_path, player_width, player_height, player_x, player_y, player_dx, player_dy,
                    player_kill_sound_path)

    # bullet
    bullet_img_path = "C:/diploma/dogegame/bullet2.png"  # 32 x 32 px image
    bullet_width = 32
    bullet_height = 32
    bullet_x = player_x + player_width / 2 - bullet_width / 2
    bullet_y = player_y + bullet_height / 2
    bullet_dx = 0
    bullet_dy = weapon_shot_velocity
    bullet_fire_sound_path = "C:/diploma/dogegame/ak.wav"

    global bullet
    bullet = Bullet(bullet_img_path, bullet_width, bullet_height, bullet_x, bullet_y, bullet_dx, bullet_dy,
                    bullet_fire_sound_path)

    # enemy (number of enemy = level number)
    enemy_img_path = "C:/diploma/dogegame/kit3.png"  # 64 x 64 px image
    enemy_width = 64
    enemy_height = 64
    enemy_dx = initial_enemy_velocity
    enemy_dy = (HEIGHT / 10) / 2
    enemy_kill_sound_path = "C:/diploma/dogegame/kill.wav"

    # laser beam (equals number of enemies and retains corresponding enemy position)
    laser_img_path = "C:/diploma/dogegame/beam.png"  # 24 x 24 px image
    laser_width = 24
    laser_height = 24
    laser_dx = 0
    laser_dy = weapon_shot_velocity
    shoot_probability = 0.3
    relaxation_time = 100
    laser_beam_sound_path = "C:/diploma/dogegame/meow.wav"

    global enemies
    global lasers

    enemies.clear()
    lasers.clear()

    for lev in range(level):
        enemy_x = random.randint(0, (WIDTH - enemy_width))
        enemy_y = random.randint(((HEIGHT / 10) * 1 - (enemy_height / 2)), ((HEIGHT / 10) * 4 - (enemy_height / 2)))
        laser_x = enemy_x + enemy_width / 2 - laser_width / 2
        laser_y = enemy_y + laser_height / 2

        enemy_obj = Enemy(enemy_img_path, enemy_width, enemy_height, enemy_x, enemy_y, enemy_dx, enemy_dy,
                          enemy_kill_sound_path)
        enemies.append(enemy_obj)

        laser_obj = Laser(laser_img_path, laser_width, laser_height, laser_x, laser_y, laser_dx, laser_dy,
                          shoot_probability, relaxation_time, laser_beam_sound_path)
        lasers.append(laser_obj)


# init game
init_game()
init_background_music()
runned_once = False

# main game loop begins
while running:
    # start of frame timing
    start_time = time.time()

    # background
    window.fill((0, 0, 0))
    window.blit(background_img, (0, 0))

    # register events
    for event in pygame.event.get():
        # Quit Event
        if event.type == pygame.QUIT:
            running = False

        # Keypress Down Event
        if event.type == pygame.KEYDOWN:
            # Left Arrow Key down
            if event.key == pygame.K_LEFT:
                print("LOG: Left Arrow Key Pressed Down")
                LEFT_ARROW_KEY_PRESSED = 1
            # Right Arrow Key down
            if event.key == pygame.K_RIGHT:
                print("LOG: Right Arrow Key Pressed Down")
                RIGHT_ARROW_KEY_PRESSED = 1
            # Up Arrow Key down
            if event.key == pygame.K_UP:
                print("LOG: Up Arrow Key Pressed Down")
                UP_ARROW_KEY_PRESSED = 1
            # Space Bar down
            if event.key == pygame.K_SPACE:
                print("LOG: Space Bar Pressed Down")
                SPACE_BAR_PRESSED = 1
            # Enter Key down ("Carriage RETURN key" from old typewriter lingo)
            if event.key == pygame.K_RETURN:
                print("LOG: Enter Key Pressed Down")
                ENTER_KEY_PRESSED = 1
                pause_state += 1
            # Esc Key down
            if event.key == pygame.K_ESCAPE:
                print("LOG: Escape Key Pressed Down")
                ESC_KEY_PRESSED = 1
                pause_state += 1

        # Keypress Up Event
        if event.type == pygame.KEYUP:
            # Right Arrow Key up
            if event.key == pygame.K_RIGHT:
                print("LOG: Right Arrow Key Released")
                RIGHT_ARROW_KEY_PRESSED = 0
            # Left Arrow Key up
            if event.key == pygame.K_LEFT:
                print("LOG: Left Arrow Key Released")
                LEFT_ARROW_KEY_PRESSED = 0
            # Up Arrow Key up
            if event.key == pygame.K_UP:
                print("LOG: Up Arrow Key Released")
                UP_ARROW_KEY_PRESSED = 0
            # Space Bar up
            if event.key == pygame.K_SPACE:
                print("LOG: Space Bar Released")
                SPACE_BAR_PRESSED = 0
            # Enter Key up ("Carriage RETURN key" from old typewriter lingo)
            if event.key == pygame.K_RETURN:
                print("LOG: Enter Key Released")
                ENTER_KEY_PRESSED = 0
            # Esc Key up
            if event.key == pygame.K_ESCAPE:
                print("LOG: Escape Key Released")
                ESC_KEY_PRESSED = 0

    # check for pause game event
    if pause_state == 2:
        pause_state = 0
        runned_once = False
        mixer.music.unpause()
    if pause_state == 1:
        if not runned_once:
            runned_once = True
            pause_game()
        continue
    # manipulate game objects based on events and player actions
    # player spaceship movement
    if RIGHT_ARROW_KEY_PRESSED:
        player.x += player.dx
    if LEFT_ARROW_KEY_PRESSED:
        player.x -= player.dx
    # bullet firing
    if (SPACE_BAR_PRESSED or UP_ARROW_KEY_PRESSED) and not bullet.fired:
        bullet.fired = True
        bullet.fire_sound.play()
        bullet.x = player.x + player.width / 2 - bullet.width / 2
        bullet.y = player.y + bullet.height / 2
    # bullet movement
    if bullet.fired:
        bullet.y -= bullet.dy

    # iter through every enemies and lasers
    for i in range(len(enemies)):
        # laser beaming
        if not lasers[i].beamed:
            lasers[i].shoot_timer += 1
            if lasers[i].shoot_timer == lasers[i].relaxation_time:
                lasers[i].shoot_timer = 0
                random_chance = random.randint(0, 100)
                if random_chance <= (lasers[i].shoot_probability * 100):
                    lasers[i].beamed = True
                    lasers[i].beam_sound.play()
                    lasers[i].x = enemies[i].x + enemies[i].width / 2 - lasers[i].width / 2
                    lasers[i].y = enemies[i].y + lasers[i].height / 2
        # enemy movement
        enemies[i].x += enemies[i].dx * float(2 ** (difficulty - 1))
        # laser movement
        if lasers[i].beamed:
            lasers[i].y += lasers[i].dy

    # collision check
    for i in range(len(enemies)):
        bullet_enemy_collision = collision_check(bullet, enemies[i])
        if bullet_enemy_collision:
            kill_enemy(player, bullet, enemies[i])

    for i in range(len(lasers)):
        laser_player_collision = collision_check(lasers[i], player)
        if laser_player_collision:
            kill_player(player, enemies[i], lasers[i])

    for i in range(len(enemies)):
        enemy_player_collision = collision_check(enemies[i], player)
        if enemy_player_collision:
            kill_enemy(player, bullet, enemies[i])
            kill_player(player, enemies[i], lasers[i])

    for i in range(len(lasers)):
        bullet_laser_collision = collision_check(bullet, lasers[i])
        if bullet_laser_collision:
            destroy_weapons(player, bullet, enemies[i], lasers[i])

    # boundary check: 0 <= x <= WIDTH, 0 <= y <= HEIGHT
    # player spaceship
    if player.x < 0:
        player.x = 0
    if player.x > WIDTH - player.width:
        player.x = WIDTH - player.width
    # enemy
    for enemy in enemies:
        if enemy.x <= 0:
            enemy.dx = abs(enemy.dx) * 1
            enemy.y += enemy.dy
        if enemy.x >= WIDTH - enemy.width:
            enemy.dx = abs(enemy.dx) * -1
            enemy.y += enemy.dy
    # bullet
    if bullet.y < 0:
        bullet.fired = False
        bullet.x = player.x + player.width / 2 - bullet.width / 2
        bullet.y = player.y + bullet.height / 2
    # laser
    for i in range(len(lasers)):
        if lasers[i].y > HEIGHT:
            lasers[i].beamed = False
            lasers[i].x = enemies[i].x + enemies[i].width / 2 - lasers[i].width / 2
            lasers[i].y = enemies[i].y + lasers[i].height / 2

    # create frame by placing objects on the surface
    scoreboard()
    for laser in lasers:
        laser.draw()
    for enemy in enemies:
        enemy.draw()
    bullet.draw()
    player.draw()

    # render the display
    pygame.display.update()

    # end of rendering, end on a frame
    frame_count += 1
    end_time = time.time()
    single_frame_rendering_time = end_time - start_time
    # fps = 1 / render_time

    total_time = total_time + single_frame_rendering_time
    if total_time >= 1.0:
        fps = frame_count
        frame_count = 0
        total_time = 0
    # print("rendering time:", single_frame_rendering_time)
    # print("FPS:", fps)
    # Draw random color and text
    bg_color = random_color()
    f_width = f.get_size()[0]

    # Reset main menu and disable
    # You also can set another menu, like a 'pause menu', or just use the same
    # main_menu as the menu that will check all your input.
    main_menu.disable()
    main_menu.full_reset()
    while True:

        # noinspection PyUnresolvedReferences
        clock.tick(60)

        # Application events
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    main_menu.enable()

                    # Quit this function, then skip to loop of main-menu on line 250
                    # return

        # Pass events to main_menu
        if main_menu.is_enabled():
            main_menu.update(events)

        # Continue playing
        surface.fill(bg_color)
        surface.blit(f, ((WINDOW_SIZE[0] - f_width) / 2, WINDOW_SIZE[1] / 2))
        pygame.display.flip()

        # If test returns
        if test:
            break


def main_background() -> None:
    """
    Function used by menus, draw on background while menu is active.
    :return: None
    """
    global surface
    surface.fill((128, 0, 128))


def main(test: bool = False) -> None:
    """
    Main program.
    :param test: Indicate function is being tested
    :return: None
    """

    # -------------------------------------------------------------------------
    # Globals
    # -------------------------------------------------------------------------
    global clock
    global main_menu
    global surface

    # -------------------------------------------------------------------------
    # Create window
    # -------------------------------------------------------------------------
    surface = create_example_window('Example - Game Selector', WINDOW_SIZE)
    clock = pygame.time.Clock()

    # -------------------------------------------------------------------------
    # Create menus: Play Menu
    # -------------------------------------------------------------------------
    start_the_game = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.7,
        title='Меню',
        width=WINDOW_SIZE[0] * 0.75
    )

    submenu_theme = pygame_menu.themes.THEME_DEFAULT.copy()
    submenu_theme.widget_font_size = 15
    play_submenu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.5,
        theme=submenu_theme,
        title='Submenu',
        width=WINDOW_SIZE[0] * 0.7
    )
    for i in range(30):
        play_submenu.add.button('Back {0}'.format(i), pygame_menu.events.BACK)
    play_submenu.add.button('Return to main menu', pygame_menu.events.RESET)

    start_the_game.add.button('Розпочати',  # When pressing return -> play(DIFFICULTY[0], font)
                              play_function,
                              DIFFICULTY,
                              pygame.font.Font(pygame_menu.font.FONT_FRANCHISE, 30))
    start_the_game.add.selector('Складність: ',
                                [('1 - Легко', 'EASY'),
                                 ('2 - Нормально', 'MEDIUM'),
                                 ('3 - Важко', 'HARD')],
                                onchange=change_difficulty,
                                selector_id='select_difficulty')
    start_the_game.add.button('Повернутися', pygame_menu.events.BACK)

    # -------------------------------------------------------------------------
    # Create menus:About
    # -------------------------------------------------------------------------
    about_theme = pygame_menu.themes.THEME_DEFAULT.copy()
    about_theme.widget_margin = (0, 0)

    about_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.6,
        theme=about_theme,
        title='Інфо',
        width=WINDOW_SIZE[0] * 0.6
    )

    for m in ABOUT:
        about_menu.add.label(m, align=pygame_menu.locals.ALIGN_LEFT, font_size=20)
    about_menu.add.vertical_margin(30)
    about_menu.add.button('Повернутися', pygame_menu.events.BACK)

    # -------------------------------------------------------------------------
    # Create menus: Main
    # -------------------------------------------------------------------------
    main_theme = pygame_menu.themes.THEME_DEFAULT.copy()

    main_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.6,
        theme=main_theme,
        title='Меню',
        width=WINDOW_SIZE[0] * 0.6
    )

    main_menu.add.button('Грати', start_the_game)
    main_menu.add.button('Інфо', about_menu)
    main_menu.add.button('Вихід', pygame_menu.events.EXIT)

    # -------------------------------------------------------------------------
    # Main loop
    # -------------------------------------------------------------------------
    while True:

        # Tick
        clock.tick(FPS)

        # Paint background
        main_background()

        # Application events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()

        # Main menu
        if main_menu.is_enabled():
            main_menu.mainloop(surface, main_background, disable_loop=test, fps_limit=FPS)

        # Flip surface
        pygame.display.flip()

        # At first loop returns
        if test:
            break


if __name__ == '__main__':
    main()
