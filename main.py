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

    ZOOM = 1
    WS = 600, 600
    DS = WS[0] // ZOOM, WS[1] // ZOOM
    window = pygame.display.set_mode(WS, vsync=1)
    display = pygame.Surface(DS)
    clock = pygame.time.Clock()

    # assets

    # logic variables
    background_points = [[i] for i in range(-200, DS[1]+100, 100)]
    background_particles = ShapeParticles("circle", 0.0)

    # entities
    feeder = entities.Feeder(DS)

    # timers
    last_time = time.perf_counter()

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
        mouse_position = [pygame.mouse.get_pos()[0]/ZOOM, pygame.mouse.get_pos()[1]/ZOOM]

        # logic of the game objects and entities
        if time.perf_counter() - bg_particle_timer > 0.1:
            background_particles.add([0, DS[1]], rnd.randint(-90, 0), rnd.randint(1, 3), rnd.randint(60, 100), (200, 100, 0), 0.5)
            background_particles.add([DS[0], 0], rnd.randint(90, 180), rnd.randint(1, 3), rnd.randint(60, 100), (200, 100, 0), 0.5)
            bg_particle_timer = time.perf_counter()

        feeder.update(dt, mouse_press, mouse_position)

        # drawing on the screen
        display.fill((230, 229, 0))

        # drawing the background
        background_particles.use(display, dt)
        for bp in background_points:
            bp[0] += 2*dt
            pygame.draw.line(display, (230, 122, 0), (-10, bp[0]), (DS[0]+10, bp[0]+100), 40)
            if bp[0] > DS[1]+100:
                bp[0] = -200

        # drawing the feeder
        pygame.draw.line(display, (0, 0, 0), (0, 60), (DS[1], 60), 3)  # rail of the feeder

        feeder.draw(display, dt)

        pygame.display.update()

        # event loop
        for event in pygame.event.get():
            if event.type == QUIT:
                done = True

        pygame.display.set_caption(f"feed the bunny FPS: {round(clock.get_fps(), 2)}")

        surf = pygame.transform.scale(display, WS)
        window.blit(surf, (0, 0))
        clock.tick(61)

    pygame.quit()


if __name__ == '__main__':
    main()
    sys.exit()
