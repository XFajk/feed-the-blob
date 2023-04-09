import pygame
from xfps import ShapeParticles

import random as rnd


class Feeder:
    def __init__(self, ds: tuple):
        self.ds = ds

        self.position = pygame.Vector2(ds[0]/2, 60)
        self.radius = 20
        self.direction = 0  # 0 = no direction, 1 = right direction, -1 = left direction

        self.particles = ShapeParticles("circle", 0.2)

    def draw(self, display, dt):
        self.particles.use(display, dt)
        pygame.draw.circle(display, (0, 0, 255), self.position, self.radius)

    def update(self, dt, mouse_press, mouse_position):
        if mouse_press[0]:
            self.direction = mouse_position[0] - self.position.x
        else:
            self.direction += self.direction * -1 / 50

        self.position.x += self.direction / 20 * dt

        if self.position.x < 20:
            self.position.x = 21
            self.direction *= -1

        if self.position.x > self.ds[0]-20:
            self.position.x = self.ds[0] - 21
            self.direction *= -1

        self.particles.add(
            [self.position[0], self.position[1]+20],
            rnd.randint(0, 180),
            rnd.randint(1, 3) / 10,
            rnd.randint(1, 2)*5,
            (rnd.randint(100, 170), rnd.randint(100, 170), rnd.randint(100, 170)),
            0.01
        )



