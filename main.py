import pygame
from pygame.locals import *
from xfps import ShapeParticles  # my own library for particles

import time
import random as rnd
import math
import sys

import entities


def main() -> None:
    pygame.init()

    ZOOM = [1, 1]
    WS = 600, 600
    ORIGIN_WS = 600, 600
    current_ws = 600, 600
    DS = WS[0] // ZOOM[0], WS[1] // ZOOM[0]
    window = pygame.display.set_mode(WS, vsync=1, flags=RESIZABLE)
    display = pygame.Surface(DS)
    clock = pygame.time.Clock()

    # assets

    # logic variables
    background_points = [[i] for i in range(-200, DS[1] + 100, 100)]
    background_particles = ShapeParticles("circle", 0.0)
    display_offset = [0, 0]

    # entities
    feeder = entities.Feeder(DS)
    blobs = [entities.Blob(DS)]

    # timers
    last_time = time.perf_counter()
    spawn_timer = time.perf_counter()
    spawn_time = 3

    bg_particle_timer = time.perf_counter()

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
        if time.perf_counter() - spawn_timer > spawn_time*dt:
            blobs.append(entities.Blob(DS))
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
            b.update(dt, feeder.particles.objects)
            b.draw(display, dt)
            if b.not_feed:
                for x in blobs:
                    x.radius = x.max_radius
            if not b.alive and b.particles.objects == []:
                blobs.remove(b)

        # draw the bunny platform
        pygame.draw.rect(display, (0, 255, 100), (0, DS[1] - DS[1] / 6, 600, 600))

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

        pygame.display.set_caption(f"feed the bunny FPS: {round(clock.get_fps(), 2)}")

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
