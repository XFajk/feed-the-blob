import pygame
from xfps import ShapeParticles, surf_circle

import random as rnd
import time


class Feeder:
    def __init__(self, ds: tuple):
        self.ds = ds

        self.position = pygame.Vector2(ds[0] / 2, 60)
        self.radius = 25
        self.direction = 0  # 0 = no direction, 1 = right direction, -1 = left direction
        self.globe = surf_circle(self.radius, (0, 100, 200))

        self.particles = ShapeParticles("circle", 0.2)  # the food

        self.inner_particles = ShapeParticles("circle", 0.0)  # the particle inside the globe

        for i in range(20):
            self.inner_particles.add(
                [self.position.x-5, self.position.y+self.radius],
                rnd.randint(0, 360),
                rnd.randint(1, 2)/2,
                rnd.randint(5, 12),
                (rnd.randint(100, 170), rnd.randint(100, 170), rnd.randint(100, 170)),
                0.0
            )

        self.inner_particles_collider = pygame.Rect(0, 0, 0, 0)  # initializing the collision box of the inner particles

    def draw(self, display, dt):

        """
        this function makes sure the inner particles stay in their
        collision box
        """
        def inner_particles_movement(particle, d):
            if not self.inner_particles_collider.collidepoint(particle['loc']):
                particle["loc"][0] -= particle["vel"][0] * d
                particle["loc"][1] -= particle["vel"][1] * d
                particle["vel"][0] *= -1
                particle["vel"][1] *= -1

            if not self.inner_particles_collider.collidepoint(particle['loc']):
                particle["loc"] = [self.position.x - 5, self.position.y + self.radius]

        self.particles.use(display, dt, lambda x, d: pygame.draw.circle(display, (0, 0, 0), (x["loc"][0] + 3, x["loc"][1] + 3), x["size"]))  # draws the food particles
        for p in self.particles.objects:
            if p["loc"][1] > self.ds[1]-self.ds[1]/6:
                p["size"] = 0
        pygame.draw.circle(display, (0, 0, 0), (self.position.x, self.position.y), 5, 2)  # draws the handle on the zip line
        self.inner_particles.use(display, dt, inner_particles_movement)  # draws the inner particles
        # this function draws the transparent globe
        display.blit(self.globe, (self.position.x-self.radius, self.position.y-self.radius+self.radius+5), special_flags=pygame.BLEND_RGB_ADD)
        # this function draws the lower part of the feeder
        pygame.draw.ellipse(display, (255, 0, 0), (self.position.x-self.radius, self.position.y-self.radius+self.radius+self.radius+10, self.radius*2, 20))
        pygame.draw.rect(display, (150, 150, 150), (self.position.x-7.5, self.position.y+self.radius*2, 15, 20))

    def update(self, dt, mouse_press, mouse_position):

        """
        this if statement calculates the speed and direction of the feeder
        and adds one particle of food
        """
        if mouse_press[0]:
            self.direction = mouse_position[0] - self.position.x
            self.particles.add(
                [self.position[0], self.position[1] + self.radius*2+25],
                rnd.randint(0, 180),
                rnd.randint(1, 3) / 10,
                rnd.randint(1, 2) * 5,
                (rnd.randint(100, 170), rnd.randint(100, 170), rnd.randint(100, 170)),
                0.01
            )
        else:
            self.direction += self.direction * -1 / 50

        # moves the feeder and the inner particles with it
        self.position.x += self.direction / 20 * dt
        for p in self.inner_particles.objects:
            p["loc"][0] += self.direction / 20 * dt

        # this makes it bounce when the feeder is outside the screen
        if self.position.x < 20:
            self.position.x = 21
            self.direction *= -1

        if self.position.x > self.ds[0] - 20:
            self.position.x = self.ds[0] - 21
            self.direction *= -1

        # update the colliders
        self.inner_particles_collider = pygame.Rect(
            self.position.x-10,
            self.position.y+self.radius+5-10,
            20, 20
        )


class Blob:
    def __init__(self, ds):
        self.ds = ds

        self.radius = 32
        self.position = pygame.Vector2(ds[0] / 2, ds[1]+30)
        self.dest = ds[1] - ds[1] / 6 - self.radius
        self.points = 10

        self.max_radius = 100
        self.mouth_collider = pygame.Rect(self.position.x - self.radius, self.position.y - self.radius, self.radius * 2, 10)
        self.particles = ShapeParticles("circle", 0.2)

        # colors
        self.const_body_color = [208, 208, 208]
        self.const_dest_color = [255, 0, 0]
        self.body_color = [208, 208, 208]
        self.dest_color = [255, 0, 0]
        self.inner_particles_color = (220, 220, 220)

        # these particles are the white particles inside the blob
        self.inner_particles = ShapeParticles("circle", 0.0)
        for i in range(10):
            self.inner_particles.add([self.position.x, self.position.y], rnd.randint(0, 360), rnd.randint(1, 2)/5, rnd.randint(4, 10), self.inner_particles_color, 0.0)

        # this collider holds them in position, so they don't go outside the blob
        self.inner_particles_collider = pygame.Rect(self.position.x - self.radius, self.position.y - self.radius + self.radius / 2, self.radius * 2, self.radius * 2)

        self.outer_particles = ShapeParticles("circle", 0.0)
        for i in range(20):
            self.outer_particles.add([self.position.x, self.position.y], rnd.randint(0, 360), rnd.randint(1, 5)/5, rnd.randint(10, 15), tuple(self.body_color), 0.0)

        # this collider holds them in position, so they don't go outside the blob
        self.outer_particles_collider = pygame.Rect(self.position.x - self.radius, self.position.y - self.radius + self.radius / 2, self.radius * 2, self.radius * 2)

        self.growth_speed = 0.1

        self.velocity = pygame.Vector2(0, 0)
        self.direction = rnd.choice([-1, 1])
        self.speed = rnd.randint(1, 3)

        # timer
        self.not_feed_timer = time.perf_counter()
        self.not_feed_time = 7
        self.not_feed = False

        self.alive = True

        # sound effects
        self.plop_counter = 49
        self.plop_sound = pygame.mixer.Sound("assets/sound_effects/the plop_sound.mp3")

        self.explosion_sound = pygame.mixer.Sound("assets/sound_effects/explosion.mp3")
        self.explosion_sound.set_volume(0.2)

        # text and font
        self.font = pygame.font.Font("assets/font/main-font.ttf", 25)
        self.points_text = self.font.render(f"+{self.points}", True, (255, 0, 0))
        self.points_text_position = pygame.Vector2(self.position)
        self.points_text_timer = None

    def draw(self, display, dt):
        def inner_particles_move(particle, d):
            if not self.inner_particles_collider.collidepoint(particle['loc']):
                particle["loc"][0] -= particle["vel"][0] * d
                particle["loc"][1] -= particle["vel"][1] * d
                particle["vel"][0] *= -1
                particle["vel"][1] *= -1

            if not self.inner_particles_collider.collidepoint(particle['loc']):
                particle["loc"] = [self.position.x, self.position.y]

        def outer_particle_move(particle, d):
            particle["color"] = self.body_color
            if not self.outer_particles_collider.collidepoint(particle['loc']):
                particle["loc"][0] -= particle["vel"][0] * d
                particle["loc"][1] -= particle["vel"][1] * d
                particle["vel"][0] *= -1
                particle["vel"][1] *= -1

            if not self.outer_particles_collider.collidepoint(particle['loc']):
                particle["loc"] = [self.position.x, self.position.y]

        if self.alive:
            # drawing the outlines
            for p in self.outer_particles.objects:
                pygame.draw.circle(display, (0, 0, 0), (p["loc"][0]+3, p["loc"][1]+3), p["size"])
            pygame.draw.ellipse(display, (0, 0, 0), (self.position.x - self.radius+3, self.position.y - self.radius + self.radius / 2+3, self.radius*2, self.radius * 2))

            # drawing the blob
            self.outer_particles.use(display, dt, outer_particle_move)
            pygame.draw.ellipse(display, self.body_color, (self.position.x - self.radius, self.position.y - self.radius + self.radius / 2, self.radius*2, self.radius * 2))
            self.inner_particles.use(display, dt, inner_particles_move)
            self.points_text_position = pygame.Vector2(self.position)
        self.particles.use(display, dt, lambda x, d: pygame.draw.circle(display, (0, 0, 0), (x["loc"][0] + 3, x["loc"][1] + 3), x["size"]))

        def inner_particles_move(particle, d):
            if not self.inner_particles_collider.collidepoint(particle['loc']):
                particle["loc"][0] -= particle["vel"][0]*d
                particle["loc"][1] -= particle["vel"][1]*d
                particle["vel"][0] *= -1
                particle["vel"][1] *= -1
        self.inner_particles.use(display, dt, inner_particles_move)

        if not self.alive and self.radius >= self.max_radius:
            if self.points_text_timer is None:
                self.points_text_timer = time.perf_counter()
            if time.perf_counter() - self.points_text_timer < 1:
                display.blit(self.points_text, (self.points_text_position.x-self.points_text.get_width()/2, self.points_text_position.y))
                self.points_text_position.y -= 0.5 * dt

    def update(self, dt, foods):

        # updates the colliders
        self.mouth_collider = pygame.Rect(self.position.x - self.radius, self.position.y - self.radius, self.radius * 2, self.radius*2)  # update collider
        self.inner_particles_collider = pygame.Rect(
            self.position.x - self.radius+self.radius/2,
            self.position.y - self.radius + self.radius / 2+self.radius/2,
            self.radius * 2-self.radius/2*2,
            self.radius * 2-self.radius/2*2
        )
        self.outer_particles_collider = pygame.Rect(
            self.position.x - self.radius+self.radius/4,
            self.position.y - self.radius + self.radius/2+self.radius/4,
            self.radius * 2-self.radius/4*2,
            self.radius * 2-self.radius/4*2
        )

        # make movement
        self.velocity = pygame.Vector2(0, 0)

        if self.position.x - self.radius < 0:
            self.position.x += self.speed
            self.direction *= -1

        if self.position.x + self.radius > self.ds[0]:
            self.position.x -= self.speed
            self.direction *= -1

        self.velocity.x = self.direction*self.speed

        if self.position.y > self.dest:
            self.velocity.y = -2

        self.position += self.velocity * dt
        for p in self.inner_particles.objects:
            p["loc"][0] += self.velocity.x
            p["loc"][1] += self.velocity.y

        for p in self.outer_particles.objects:
            p["loc"][0] += self.velocity.x
            p["loc"][1] += self.velocity.y

        # collision logic
        # feeding the blob
        for food in foods:
            if self.mouth_collider.collidepoint(food["loc"]) and self.radius < self.max_radius:
                self.plop_counter += 1
                self.radius += self.growth_speed*dt
                self.position.y -= self.growth_speed
                self.not_feed_timer = 0
                self.dest_color = [255, 0, 0]
                self.body_color = [208, 208, 208]
                self.not_feed_timer = time.perf_counter()
                for p in self.inner_particles.objects:
                    p["size"] += self.growth_speed/2*dt
                for p in self.outer_particles.objects:
                    p["size"] += self.growth_speed/2*dt

        if self.radius >= self.max_radius and self.alive:
            self.inner_particles.objects = []
            self.outer_particles.objects = []
            self.not_feed_timer = 0
            self.not_feed = False
            self.explosion_sound.play()
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

        # not feed logic
        if time.perf_counter() - self.not_feed_timer > self.not_feed_time/2 and self.alive:
            color = self.body_color.copy()
            self.body_color[0] += (self.dest_color[0] - self.body_color[0]) / 10
            self.body_color[0] = int(self.body_color[0])
            self.body_color[1] += (self.dest_color[1] - self.body_color[1]) / 10
            self.body_color[1] = int(self.body_color[1])
            self.body_color[2] += (self.dest_color[2] - self.body_color[2]) / 10
            self.body_color[2] = int(self.body_color[2])

            if color == self.body_color:
                if self.dest_color == self.const_dest_color:
                    self.dest_color = self.const_body_color
                elif self.dest_color == self.const_body_color:
                    self.dest_color = self.const_dest_color

        if time.perf_counter() - self.not_feed_timer > self.not_feed_time and self.alive:
            self.not_feed = True
            self.not_feed_timer = time.perf_counter()

        # sound logic
        if self.plop_counter > 50:
            self.plop_sound.play()
            self.plop_counter = 0
