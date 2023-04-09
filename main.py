import pygame
from pygame.locals import *
from xfps import ShapeParticles  # my own library for particles

import time
import random as rnd
import math
import sys


def main() -> None:
    pygame.init()

    ZOOM = 1
    WS = 800, 600
    DS = WS[0] / ZOOM, WS[1] / ZOOM
    window = pygame.display.set_mode(WS)
    display = pygame.Surface(DS)
    clock = pygame.time.Clock()

    done = False
    while not done:

        # logic of the game objects and entities

        # drawing on the screen
        display.fill((0, 0, 0))

        pygame.draw.rect(display, (255, 0, 0), (0, 0, 32, 32))

        pygame.display.update()

        # event loop
        for event in pygame.event.get():
            if event.type == QUIT:
                done = True

        pygame.display.set_caption(f"feed the bunny FPS: {round(clock.get_fps(), 2)}")

        surf = pygame.transform.scale(display, WS)
        window.blit(surf, (0, 0))
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
    sys.exit()
