import pygame
from pygame.locals import *
from xfps import ShapeParticles  # my own library for particles

import time
import random as rnd
import math
import sys
import os

from entities import *


def main() -> None:
    if sys.platform == "darwin":  # checking if the operating system is macOS
        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))  # sets the current working directory to the directory containing the script

    pygame.init()
    pygame.mixer.init()

    ZOOM = [1, 1]
    WS = 600, 600
    ORIGIN_WS = 600, 600
    current_ws = 600, 600
    DS = WS[0] // ZOOM[0], WS[1] // ZOOM[0]
    window = pygame.display.set_mode(WS, vsync=1, flags=RESIZABLE)
    display = pygame.Surface(DS)
    clock = pygame.time.Clock()

    # assets
    ground_sprite = pygame.image.load("assets/sprites/ground.png").convert()
    ground_sprite.set_colorkey((255, 255, 255))

    icon_sprite = pygame.image.load("assets/sprites/icon.png").convert()

    mouse_pressed_spr = pygame.image.load("assets/sprites/mouse_pressed.png").convert()
    mouse_pressed_spr.set_colorkey((255, 255, 255))

    mouse_not_pressed_spr = pygame.image.load("assets/sprites/mouse_not_pressed.png").convert()
    mouse_not_pressed_spr.set_colorkey((255, 255, 255))

    mouse_sprs = [mouse_pressed_spr, mouse_not_pressed_spr]
    mouse_sprs_index = 1

    button_press_sound = pygame.mixer.Sound("assets/sound_effects/button_press.mp3")

    pygame.mixer.music.load("assets/music/music-for-game.mp3")
    pygame.mixer.music.set_volume(0.1)

    pygame.mixer.music.play(-1)

    main_font = pygame.font.Font("assets/font/main-font.ttf", 40)
    secondary_font = pygame.font.Font("assets/font/main-font.ttf", 25)
    small_font = pygame.font.Font("assets/font/main-font.ttf", 18)
    title_font = pygame.font.Font("assets/font/title-font.ttf", 70)

    # logic variables
    # logic variables
    points = 0
    background_points = [[i] for i in range(-200, DS[1] + 100, 100)]
    background_particles = ShapeParticles("circle", 0.0)
    display_offset = [0, 0]
    game_over = False
    game_over_sound = pygame.mixer.Sound("assets/sound_effects/game-over-sound.mp3")

    game_over_gui_position = pygame.Vector2(DS[0]/2, DS[1]/2-600)
    game_over_gui_dest_position = pygame.Vector2(DS[0]/2, DS[1]/2)

    game_started = False

    game_started_gui_position = pygame.Vector2(DS[0]/2, DS[1]/2)
    game_started_gui_dest_position = game_started_gui_position
    play_button_pressed = False

    tutorial = False

    tutorial_gui_position = pygame.Vector2(DS[0]/2, DS[1]/2)
    tutorial_gui_dest_position = tutorial_gui_position

    tutorial_mouse_position = pygame.Vector2(DS[0]/2+60, DS[1]/2-10)
    tutorial_mouse_position_index = 3
    tutorial_mouse_dest_positions = [pygame.Vector2(DS[0]/2-120, DS[1]/2-10), pygame.Vector2(0, 0), pygame.Vector2(DS[0]/2+60, DS[1]/2-10), pygame.Vector2(0, 0)]
    tutorial_mouse_dest_position = pygame.Vector2(DS[0]/2-120, DS[1]/2)

    tutorial_blob = Blob(DS)
    tutorial_blob.speed = 0
    tutorial_blob.mouth_collider = pygame.Rect(0, 0, 0, 0)

    enter_pressed = False

    feeder = Feeder(DS)
    blobs = []

    # timers
    last_time = time.perf_counter()
    spawn_timer = time.perf_counter()
    spawn_time = 2

    bg_particle_timer = time.perf_counter()

    tutorial_mouse_pressed_timer = time.perf_counter()

    done = False
    while not done:

        # calculating the delta time
        dt = time.perf_counter() - last_time
        dt *= 60
        last_time = time.perf_counter()

        # input methods
        keys = pygame.key.get_pressed()
        mouse_press = pygame.mouse.get_pressed()
        """
        in this line of code we calculate the mouse position
        by multiplying it with ZOOM so it is on the correct position no matter what size the 
        size of a window 
        """
        mouse_position = [
            pygame.mouse.get_pos()[0] * ZOOM[0] - display_offset[0] * ZOOM[0],
            pygame.mouse.get_pos()[1] * ZOOM[1] - display_offset[1] * ZOOM[1]
        ]

        # logic of the game objects and entities
        if time.perf_counter() - spawn_timer > spawn_time*dt and not game_over and game_started and not tutorial:
            the_blob = rnd.choices([Blob(DS), SpeedBlob(DS), HeavyBlob(DS), RandomBlob(DS)], weights=[4, 8, 2, 3])
            blobs.append(the_blob[0])
            spawn_timer = time.perf_counter()

        if time.perf_counter() - bg_particle_timer > 0.1:
            background_particles.add([0, DS[1]], rnd.randint(-90, 0), rnd.randint(1, 3), rnd.randint(60, 100),
                                     (200, 100, 0), 0.5)
            background_particles.add([DS[0], 0], rnd.randint(90, 180), rnd.randint(1, 3), rnd.randint(60, 100),
                                     (200, 100, 0), 0.5)
            bg_particle_timer = time.perf_counter()

        feeder.update(dt, mouse_press, mouse_position)

        # drawing on the screen
        display.fill((230, 229, 0))

        # drawing the background
        background_particles.use(display, dt)
        for bp in background_points:
            bp[0] += 2 * dt
            pygame.draw.line(display, (230, 122, 0), (-10, bp[0]), (DS[0] + 10, bp[0] + 100), 40)
            if bp[0] > DS[1] + 100:
                bp[0] = -200

        # drawing the feeder
        pygame.draw.line(display, (0, 0, 0), (0, 60), (DS[1], 60), 3)  # rail of the feeder
        feeder.draw(display, dt)

        # drawing the blobs
        for b in sorted(blobs, key=lambda i: i.radius, reverse=True):
            b.update(dt, feeder.particles.objects, game_over)
            b.draw(display, dt)
            if b.not_feed:
                for x in blobs:
                    x.radius = x.max_radius
                game_over = True
                game_over_sound.play()
                pygame.mixer.music.stop()
            if not b.alive and b.particles.objects == []:
                blobs.remove(b)

            if not game_over and not b.alive:
                points += b.points
                b.points = 0

        # draw the bunny platform
        display.blit(ground_sprite, (0, DS[1] - DS[1]/6-10))

        # drawing the Game Not Started GUI
        if not game_started:

            game_started_gui_position.x += (game_started_gui_dest_position.x - game_started_gui_position.x) / 20*dt
            game_started_gui_position.y += (game_started_gui_dest_position.y - game_started_gui_position.y) / 20*dt

            game_started_gui = {
                "title_text": title_font.render("feed-the-blob", True, (0, 0, 255)),
                "title_text_shadow": title_font.render("feed-the-blob", True, (0, 0, 0)),

                "play_button_rect": pygame.Rect(game_started_gui_position.x-80/2, game_started_gui_position.y-50/2-30, 80, 50),
                "play_button_text": secondary_font.render("PLAY", True, (255, 255, 255)),
                "play_button_color":  (0, 255, 0),

                "quit_button_rect": pygame.Rect(game_started_gui_position.x-80/2, game_started_gui_position.y-50/2+50, 80, 50),
                "quit_button_text": secondary_font.render("QUIT", True, (255, 255, 255)),
                "quit_button_color": (0, 255, 0),
            }

            # tile
            display.blit(game_started_gui["title_text_shadow"], (game_started_gui_position.x-game_started_gui["title_text_shadow"].get_width()/2+3, game_started_gui_position.y-game_started_gui["title_text_shadow"].get_height()/2-180+3))
            display.blit(game_started_gui["title_text"], (game_started_gui_position.x-game_started_gui["title_text"].get_width()/2, game_started_gui_position.y-game_started_gui["title_text"].get_height()/2-180))

            # button logic

            if game_started_gui["play_button_rect"].collidepoint(mouse_position):
                game_started_gui["play_button_color"] = (0, 200, 0)
                if mouse_press[0] and not play_button_pressed:
                    button_press_sound.play()
                    play_button_pressed = True
                    game_started_gui_dest_position = pygame.Vector2(game_started_gui_position.x, game_started_gui_position.y-600)
                elif not mouse_press[0]:
                    play_button_pressed = False
            else:
                play_button_pressed = False
                game_started_gui["play_button_color"] = (0, 255, 0)

            if game_started_gui["quit_button_rect"].collidepoint(mouse_position):
                game_started_gui["quit_button_color"] = (200, 0, 0)
                if mouse_press[0] and game_started_gui_dest_position == game_started_gui_position:
                    button_press_sound.play()
                    done = True
            else:
                game_started_gui["quit_button_color"] = (255, 0, 0)

            # buttons
            pygame.draw.rect(display, (0, 0, 0), (game_started_gui["play_button_rect"].x+3, game_started_gui["play_button_rect"].y+3, game_started_gui["play_button_rect"].w, game_started_gui["play_button_rect"].h))
            pygame.draw.rect(display, game_started_gui["play_button_color"], game_started_gui["play_button_rect"])

            pygame.draw.rect(display, (0, 0, 0), (game_started_gui["quit_button_rect"].x+3, game_started_gui["quit_button_rect"].y+3, game_started_gui["quit_button_rect"].w, game_started_gui["quit_button_rect"].h))
            pygame.draw.rect(display, game_started_gui["quit_button_color"], game_started_gui["quit_button_rect"])

            # button text
            display.blit(
                game_started_gui["play_button_text"],
                (game_started_gui_position.x - game_started_gui["play_button_text"].get_width() / 2, game_started_gui_position.y-game_started_gui["play_button_text"].get_height()/2-26)
            )

            display.blit(
                game_started_gui["quit_button_text"],
                (game_started_gui_position.x - game_started_gui["quit_button_text"].get_width() / 2, game_started_gui_position.y-game_started_gui["quit_button_text"].get_height()/2+54)
            )

            if game_started_gui_position.y < -100:
                game_started = True
                tutorial = True

        # drawing the Tutorial GUI
        if tutorial:
            tutorial_gui_position.x += (tutorial_gui_dest_position.x - tutorial_gui_position.x) / 20*dt
            tutorial_gui_position.y += (tutorial_gui_dest_position.y - tutorial_gui_position.y) / 20*dt
            tutorial_mouse_position.x += (tutorial_gui_dest_position.x - tutorial_gui_position.x) / 20*dt
            tutorial_mouse_position.y += (tutorial_gui_dest_position.y - tutorial_gui_position.y) / 20*dt

            tutorial_mouse_dest_positions = [pygame.Vector2(tutorial_gui_position.x - 120, tutorial_gui_position.y - 10), pygame.Vector2(0, 0),
                                             pygame.Vector2(tutorial_gui_position.x + 60, tutorial_gui_position.y - 10), pygame.Vector2(0, 0)]
            tutorial_mouse_dest_position = tutorial_mouse_dest_positions[tutorial_mouse_position_index]

            if not mouse_sprs_index:
                tutorial_mouse_position.x += (tutorial_mouse_dest_position.x - tutorial_mouse_position.x) / 20*dt
                tutorial_mouse_position.y += (tutorial_mouse_dest_position.y - tutorial_mouse_position.y) / 20*dt

            tutorial_gui = {
                "outer_window1": pygame.Rect(tutorial_gui_position.x-440/2, tutorial_gui_position.y-220/2, 440, 220),
                "inner_window1": pygame.Rect(tutorial_gui_position.x-400/2, tutorial_gui_position.y-180/2, 400, 180),

                "1line1": small_font.render("control the feeder by holding the left mouse button", True, (255, 255, 0)),
                "1line2": small_font.render("and by dragging the mouse around", True, (255, 255, 0)),
                "1line1s": small_font.render("control the feeder by holding the left mouse button", True, (0, 0, 0)),
                "1line2s": small_font.render("and by dragging the mouse around", True, (0, 0, 0)),
                "1line3": small_font.render("press Enter", True, (255, 255, 0)),
                "1line3s": small_font.render("press Enter", True, (0, 0, 0)),

                "outer_window2": pygame.Rect(tutorial_gui_position.x-440/2+600, tutorial_gui_position.y-220/2, 440, 220),
                "inner_window2": pygame.Rect(tutorial_gui_position.x-400/2+600, tutorial_gui_position.y-180/2, 400, 180),

                "2line1": small_font.render("when the blob blinks red its going to explode", True, (255, 255, 0)),
                "2line2": small_font.render("when it explodes this way its you lose the game", True, (255, 255, 0)),
                "2line1s": small_font.render("when the blob blinks red its going to explode", True, (0, 0, 0)),
                "2line2s": small_font.render("when it explodes this way its you lose the game", True, (0, 0, 0)),
                "2line3": small_font.render("press Enter", True, (255, 255, 0)),
                "2line3s": small_font.render("press Enter", True, (0, 0, 0)),
            }

            # drawing the windows
            pygame.draw.rect(display, (0, 0, 0), (tutorial_gui["outer_window1"].x+3, tutorial_gui["outer_window1"].y+3, tutorial_gui["outer_window1"].w, tutorial_gui["outer_window1"].h))
            pygame.draw.rect(display, (100, 150, 0), tutorial_gui["outer_window1"])
            pygame.draw.rect(display, (0, 0, 0), (tutorial_gui["inner_window1"].x+3, tutorial_gui["inner_window1"].y+3, tutorial_gui["inner_window1"].w, tutorial_gui["inner_window1"].h))
            pygame.draw.rect(display, (100, 100, 100), tutorial_gui["inner_window1"])

            pygame.draw.rect(display, (0, 0, 0), (tutorial_gui["outer_window2"].x+3, tutorial_gui["outer_window2"].y+3, tutorial_gui["outer_window2"].w, tutorial_gui["outer_window2"].h))
            pygame.draw.rect(display, (100, 150, 0), tutorial_gui["outer_window2"])
            pygame.draw.rect(display, (0, 0, 0), (tutorial_gui["inner_window2"].x+3, tutorial_gui["inner_window2"].y+3, tutorial_gui["inner_window2"].w, tutorial_gui["inner_window2"].h))
            pygame.draw.rect(display, (100, 100, 100), tutorial_gui["inner_window2"])

            # drawing text
            display.blit(tutorial_gui["1line1s"], (tutorial_gui_position.x-tutorial_gui["1line1s"].get_width()/2+3, tutorial_gui_position.y-tutorial_gui["1line1s"].get_height()/2-60+3))
            display.blit(tutorial_gui["1line1"], (tutorial_gui_position.x-tutorial_gui["1line1"].get_width()/2, tutorial_gui_position.y-tutorial_gui["1line1"].get_height()/2-60))
            display.blit(tutorial_gui["1line2s"], (tutorial_gui_position.x-tutorial_gui["1line2s"].get_width()/2+3, tutorial_gui_position.y-tutorial_gui["1line2s"].get_height()/2-40+3))
            display.blit(tutorial_gui["1line2"], (tutorial_gui_position.x-tutorial_gui["1line2"].get_width()/2, tutorial_gui_position.y-tutorial_gui["1line2"].get_height()/2-40))
            display.blit(tutorial_gui["1line3s"], (tutorial_gui_position.x-tutorial_gui["1line3s"].get_width()/2+3, tutorial_gui_position.y-tutorial_gui["1line3s"].get_height()/2+75+3))
            display.blit(tutorial_gui["1line3"], (tutorial_gui_position.x-tutorial_gui["1line3"].get_width()/2, tutorial_gui_position.y-tutorial_gui["1line3"].get_height()/2+75))

            display.blit(tutorial_gui["2line1s"], (tutorial_gui_position.x-tutorial_gui["2line1s"].get_width()/2+3+600, tutorial_gui_position.y-tutorial_gui["2line1s"].get_height()/2-60+3))
            display.blit(tutorial_gui["2line1"], (tutorial_gui_position.x-tutorial_gui["2line1"].get_width()/2+600, tutorial_gui_position.y-tutorial_gui["2line1"].get_height()/2-60))
            display.blit(tutorial_gui["2line2s"], (tutorial_gui_position.x-tutorial_gui["2line2s"].get_width()/2+3+600, tutorial_gui_position.y-tutorial_gui["2line2s"].get_height()/2-40+3))
            display.blit(tutorial_gui["2line2"], (tutorial_gui_position.x-tutorial_gui["2line2"].get_width()/2+600, tutorial_gui_position.y-tutorial_gui["2line2"].get_height()/2-40))
            display.blit(tutorial_gui["2line3s"], (tutorial_gui_position.x-tutorial_gui["2line3s"].get_width()/2+3+600, tutorial_gui_position.y-tutorial_gui["2line3s"].get_height()/2+75+3))
            display.blit(tutorial_gui["2line3"], (tutorial_gui_position.x-tutorial_gui["2line3"].get_width()/2+600, tutorial_gui_position.y-tutorial_gui["2line3"].get_height()/2+75))

            tutorial_blob.position = pygame.Vector2((tutorial_gui_position.x+600, tutorial_gui_position.y))
            tutorial_blob.update(dt, [], False)
            tutorial_blob.draw(display, dt)

            display.blit(mouse_sprs[mouse_sprs_index], tutorial_mouse_position)

            if time.perf_counter() - tutorial_mouse_pressed_timer > 3:
                mouse_sprs_index += 1
                tutorial_mouse_position_index += 1
                if mouse_sprs_index > 1:
                    mouse_sprs_index = 0
                if tutorial_mouse_position_index > 3:
                    tutorial_mouse_position_index = 0
                tutorial_mouse_pressed_timer = time.perf_counter()

            if keys[K_RETURN] and not enter_pressed:
                enter_pressed = True
                tutorial_gui_dest_position = pygame.Vector2(float(tutorial_gui_position.x)-600.0, tutorial_gui_position.y)
            elif not keys[K_RETURN] and enter_pressed:
                enter_pressed = False

            if tutorial_gui_position.x < -800:
                tutorial = False

        # drawing and updating the Game Over GUI
        if game_over:
            game_over_gui_position.x += (game_over_gui_dest_position.x - game_over_gui_position.x) / 20*dt
            game_over_gui_position.y += (game_over_gui_dest_position.y - game_over_gui_position.y) / 20*dt

            game_over_gui = {
                "outer_window": pygame.Rect(game_over_gui_position.x - 420 / 2, game_over_gui_position.y - 420 / 2, 420,
                                            420),
                "inner_window": pygame.Rect(game_over_gui_position.x - 360 / 2, game_over_gui_position.y - 360 / 2, 360,
                                            360),
                "Title_text": main_font.render("GAME OVER :(", True, (255, 255, 0)),
                "Title_text_shadow": main_font.render("GAME OVER :(", True, (0, 0, 0)),
                "score_text": secondary_font.render(f"score: {points}", True, (255, 255, 0)),
                "score_text_shadow": secondary_font.render(f"score: {points}", True, (0, 0, 0)),

                "reset_button_rect": pygame.Rect(game_over_gui_position.x-80/2, game_over_gui_position.y-50/2+30, 80, 50),
                "reset_button_text": secondary_font.render("RESET", True, (255, 255, 255)),
                "reset_button_color": (255, 255, 0),
                "quit_button_rect": pygame.Rect(game_over_gui_position.x-80/2, game_over_gui_position.y-50/2+90, 80, 50),
                "quit_button_text": secondary_font.render("QUIT", True, (255, 255, 255)),
                "quit_button_color": (255, 0, 0)
            }

            pygame.draw.rect(display, (0, 0, 0), (game_over_gui.get("outer_window").x+3, game_over_gui.get("outer_window").y+3, game_over_gui.get("outer_window").w, game_over_gui.get("outer_window").h))
            pygame.draw.rect(display, (100, 150, 0), game_over_gui.get("outer_window"))
            pygame.draw.rect(display, (0, 0, 0), (game_over_gui.get("inner_window").x+3, game_over_gui.get("inner_window").y+3, game_over_gui.get("inner_window").w, game_over_gui.get("inner_window").h))
            pygame.draw.rect(display, (100, 100, 100), game_over_gui.get("inner_window"))

            # button logic
            if game_over_gui["reset_button_rect"].collidepoint(mouse_position):
                game_over_gui["reset_button_color"] = (200, 200, 0)
                if mouse_press[0]:
                    button_press_sound.play()
                    feeder = Feeder(DS)
                    blobs = []
                    points = 0
                    game_over = False
                    pygame.mixer.music.play(-1)
                    game_over_gui_position = pygame.Vector2(DS[0]/2, DS[1]/2-600)
            else:
                game_over_gui["reset_button_color"] = (255, 255, 0)

            if game_over_gui["quit_button_rect"].collidepoint(mouse_position):
                game_over_gui["quit_button_color"] = (200, 0, 0)
                if mouse_press[0]:
                    button_press_sound.play()
                    done = True
            else:
                game_over_gui["quit_button_color"] = (255, 0, 0)

            # buttons
            pygame.draw.rect(display, (0, 0, 0), (game_over_gui["reset_button_rect"].x+3, game_over_gui["reset_button_rect"].y+3, game_over_gui["reset_button_rect"].w, game_over_gui["reset_button_rect"].h))
            pygame.draw.rect(display, game_over_gui["reset_button_color"], game_over_gui["reset_button_rect"])

            pygame.draw.rect(display, (0, 0, 0), (game_over_gui["quit_button_rect"].x+3, game_over_gui["quit_button_rect"].y+3, game_over_gui["quit_button_rect"].w, game_over_gui["quit_button_rect"].h))
            pygame.draw.rect(display, game_over_gui["quit_button_color"], game_over_gui["quit_button_rect"])

            # button text
            display.blit(
                game_over_gui["reset_button_text"],
                (game_over_gui_position.x - game_over_gui["reset_button_text"].get_width() / 2, game_over_gui_position.y-game_over_gui["reset_button_text"].get_height()/2+34)
            )

            display.blit(
                game_over_gui["quit_button_text"],
                (game_over_gui_position.x - game_over_gui["quit_button_text"].get_width() / 2, game_over_gui_position.y-game_over_gui["quit_button_text"].get_height()/2+94)
            )

            # text
            display.blit(game_over_gui.get("Title_text_shadow"), (game_over_gui_position.x-game_over_gui.get("Title_text").get_width()/2+3, game_over_gui_position.y-160+3))
            display.blit(game_over_gui.get("Title_text"), (game_over_gui_position.x-game_over_gui.get("Title_text").get_width()/2, game_over_gui_position.y-160))

            game_over_gui["score_text"] = secondary_font.render(f"score: {points}", True, (255, 255, 0))
            game_over_gui["score_text_shadow"] = secondary_font.render(f"score: {points}", True, (0, 0, 0))
            display.blit(game_over_gui.get("score_text_shadow"), (game_over_gui_position.x-game_over_gui.get("score_text").get_width()/2+3, game_over_gui_position.y-100+3))
            display.blit(game_over_gui.get("score_text"), (game_over_gui_position.x-game_over_gui.get("score_text").get_width()/2, game_over_gui_position.y-100))

        pygame.display.update()

        # event loop
        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
            if event.type == VIDEORESIZE:
                # resets the background
                background_points = [[i] for i in range(-200, DS[1] + 100, 100)]
                current_ws = event.w, event.h

                # if  window is smaller than Original window size then scale the ZOOM so the mouse position fits
                if event.w < ORIGIN_WS[0]:
                    WS = event.w, WS[1]
                    ZOOM[0] = ORIGIN_WS[0] / event.w
                else:
                    WS = ORIGIN_WS
                    ZOOM[0] = 1
                if event.h < ORIGIN_WS[1]:
                    WS = WS[0], event.h
                    ZOOM[1] = ORIGIN_WS[1] / event.h
                else:
                    WS = ORIGIN_WS
                    ZOOM[1] = 1

                """
                if the window is bigger then the original window
                size it scales the original resolution in this case
                600X600 to a bigger one like 700x700 and adjust the ZOOM so the mouse 
                position is correctly calculated
                """
                if event.w > ORIGIN_WS[0] and event.h > ORIGIN_WS[1]:
                    if event.w > event.h:
                        WS = event.h, event.h
                        ZOOM = [ORIGIN_WS[0] / WS[0], ORIGIN_WS[1] / WS[1]]
                    elif event.w < event.h:
                        WS = event.w, event.w
                        ZOOM = [ORIGIN_WS[0] / WS[0], ORIGIN_WS[1] / WS[1]]
                    elif event.w == event.h:
                        WS = event.w, event.w
                        ZOOM = [ORIGIN_WS[0] / WS[0], ORIGIN_WS[1] / WS[1]]

                for b in blobs:
                    b.position.y = b.dest

        pygame.display.set_caption(f"feed the bunny FPS: {round(clock.get_fps(), 2)}")
        pygame.display.set_icon(icon_sprite)

        """
            this makes sure that if the window is bigger
            in proportion to the resolution in this case 600x600
            if it is it centers it on the axis that is bigger
        """
        if current_ws[0] > WS[0]:
            display_offset[0] = (current_ws[0] - WS[0]) / 2
        else:
            display_offset[0] = 0
        if current_ws[1] > WS[1]:
            display_offset[1] = (current_ws[1] - WS[1]) / 2
        else:
            display_offset[1] = 0

        surf = pygame.transform.scale(display, WS)
        window.blit(surf, display_offset)
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
    sys.exit()
