import pygame
from xfps import ShapeParticles

import random as rnd


class Feeder:
    def __init__(self, ds: tuple):
        self.ds = ds

        self.position = pygame.Vector2(ds[0] / 2, 60)
        self.radius = 20
        self.direction = 0  # 0 = no direction, 1 = right direction, -1 = left direction
        self.img = pygame.image.load("assets/sprites/feeder.png").convert()
        self.img.set_colorkey((255, 255, 255))

        self.particles = ShapeParticles("circle", 0.2)

    def draw(self, display, dt):
        self.particles.use(display, dt)
        pygame.draw.circle(display, (0, 0, 0), (self.position.x, self.position.y), 5, 2)
        display.blit(self.img, (self.position.x-self.radius, self.position.y-self.radius+25))

    def update(self, dt, mouse_press, mouse_position):
        if mouse_press[0]:
            self.direction = mouse_position[0] - self.position.x
            self.particles.add(
                [self.position[0], self.position[1] + 45],
                rnd.randint(0, 180),
                rnd.randint(1, 3) / 10,
                rnd.randint(1, 2) * 5,
                (rnd.randint(100, 170), rnd.randint(100, 170), rnd.randint(100, 170)),
                0.01
            )
        else:
            self.direction += self.direction * -1 / 50

        self.position.x += self.direction / 20 * dt

        if self.position.x < 20:
            self.position.x = 21
            self.direction *= -1

        if self.position.x > self.ds[0] - 20:
            self.position.x = self.ds[0] - 21
            self.direction *= -1


class Bunny:
    def __init__(self, ds):
        self.ds = ds

        self.radius = 32
        self.position = pygame.Vector2(ds[0] / 2, ds[1] - ds[1] / 6 - self.radius)

        self.max_radius = 100

        self.mouth_collider = pygame.Rect(self.position.x - self.radius, self.position.y - self.radius, self.radius * 2, 10)
        self.particles = ShapeParticles("circle", 0.2)

        self.head_sprite = pygame.image.load("assets/sprites/basic bunny.png").convert()
        self.head_sprite.set_colorkey((255, 255, 255))

        self.alive = True

    def draw(self, display, dt):
        if self.alive:
            pygame.draw.circle(display, (208, 208, 208), self.position, self.radius)
            pygame.draw.circle(display, (0, 0, 0), self.position, self.radius, 1)
            pygame.draw.ellipse(display, (254, 240, 240), (self.position.x, self.position.y-8, self.radius/2+self.radius/3, self.radius/2+10+self.radius/4))
            pygame.draw.ellipse(display, (0, 0, 0), (self.position.x, self.position.y-8, self.radius/2+self.radius/3, self.radius/2+10+self.radius/4), 1)
            display.blit(self.head_sprite, (self.position.x+self.radius/4, self.position.y-self.radius*1.2))
        self.particles.use(display, dt)

    def update(self, dt, foods):

        self.mouth_collider = pygame.Rect(self.position.x - self.radius, self.position.y - self.radius, self.radius * 2, 10)  # update collider

        # make movement

        # collision logic
        for food in foods:
            if self.mouth_collider.collidepoint(food["loc"]) and self.radius < self.max_radius:
                self.radius += 0.5*dt
                self.position.y -= 0.5

        if self.radius >= self.max_radius and self.alive:
            for i in range(100):
                self.particles.add(
                    [self.position.x, self.position.y],
                    rnd.randint(0, 360),
                    rnd.randint(100, 2000)/100,
                    rnd.randint(40, 60),
                    (255, 255, 255),
                    0.5
                )

            for i in range(100):
                self.particles.add(
                    [self.position.x, self.position.y],
                    rnd.randint(0, 360),
                    rnd.randint(100, 1500)/100,
                    rnd.randint(20, 40),
                    (rnd.randint(200, 220), rnd.randint(200, 220), rnd.randint(200, 220)),
                    0.1
                )
            self.alive = False
