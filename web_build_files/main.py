import pygame
from pygame.locals import *

import time
import random as rnd
import math
import asyncio


def surf_circle(r: float, color: tuple | pygame.Color) -> pygame.Surface:
    surf = pygame.Surface((r * 2, r * 2)) if r > 0 else pygame.Surface((0, 0))
    pygame.draw.circle(surf, color, (r, r), r)
    surf.set_colorkey((0, 0, 0))

    return surf


class ShapeParticles:
    def __init__(self, shape_type: str, gravity: float = 0.0):
        self.shape_type = shape_type
        self.gravity = gravity
        self.objects = []

    def add(self, loc: list | pygame.Vector2, angle: float, speed: float, size: float, color: tuple | pygame.Color,
            dis_amount: float):
        vel = [math.cos(math.radians(angle)) * speed, math.sin(math.radians(angle)) * speed]
        self.objects.append(
            {
                "loc": loc,
                "vel": vel,
                "size": size,
                "color": color,
                "dis_amount": dis_amount,
            }
        )

    def use(self, surf: pygame.Surface, dt: float = 1.0, operation=lambda x, dt: x):
        if self.shape_type == "circle":
            for i, p in sorted(enumerate(self.objects), reverse=True):
                p["loc"][0] += p["vel"][0] * dt
                p["loc"][1] += p["vel"][1] * dt
                p["size"] -= p["dis_amount"] * dt
                p["vel"][1] += self.gravity * dt
                operation(p, dt)
                pygame.draw.circle(surf, p["color"], p["loc"], p["size"])
                if p["size"] <= 0:
                    self.objects.pop(i)

        elif self.shape_type == "rectangle":
            for i, p in sorted(enumerate(self.objects), reverse=True):
                p["loc"][0] += p["vel"][0] * dt
                p["loc"][1] += p["vel"][1] * dt
                p["size"] -= p["dis_amount"] * dt
                p["vel"][1] += self.gravity * dt
                operation(p, dt)
                pygame.draw.rect(surf, p["color"], (p["loc"][0]-p["size"]/2, p["loc"][1]-p["size"]/2, p["size"], p["size"]))
                if p["size"] <= 0:
                    self.objects.pop(i)
        else:
            raise TypeError(f"{self.shape_type} is an invalid shape type you can use circle or rectangle")

    def use_with_light(self, surf: pygame.Surface, dt: float, operation=lambda x, dt: x):
        if self.shape_type == "circle":
            for i, p in sorted(enumerate(self.objects), reverse=True):
                p["loc"][0] += p["vel"][0] * dt
                p["loc"][1] += p["vel"][1] * dt
                p["size"] -= p["dis_amount"] * dt
                p["vel"][1] += self.gravity * dt
                operation(p, dt)
                light_surf = surf_circle(p["size"] * 2, (p["color"][0] / 3, p["color"][1] / 3, p["color"][2] / 3))
                surf.blit(light_surf,
                          (p["loc"][0] - int(light_surf.get_width() / 2), p["loc"][1] - int(light_surf.get_height() / 2)),
                          special_flags=pygame.BLEND_RGB_ADD)
                pygame.draw.circle(surf, p["color"], p["loc"], p["size"])
                if p["size"] <= 0:
                    self.objects.pop(i)

        elif self.shape_type == "rectangle":
            for i, p in sorted(enumerate(self.objects), reverse=True):
                p["loc"][0] += p["vel"][0] * dt
                p["loc"][1] += p["vel"][1] * dt
                p["size"] -= p["dis_amount"] * dt
                p["vel"][1] += self.gravity * dt
                operation(p, dt)
                light_surf = surf_rect(p["size"] * 2, p["size"] * 2, (p["color"][0] / 3, p["color"][1] / 3, p["color"][2] / 3))
                surf.blit(light_surf,
                          (p["loc"][0] - int(light_surf.get_width() / 4)-p["size"]/2, p["loc"][1] - int(light_surf.get_height() / 4)-p["size"]/2),
                          special_flags=pygame.BLEND_RGB_ADD)
                pygame.draw.rect(surf, p["color"], (p["loc"][0]-p["size"]/2, p["loc"][1]-p["size"]/2, p["size"], p["size"]))
                if p["size"] <= 0:
                    self.objects.pop(i)
        else:
            raise TypeError(f"{self.shape_type} is an invalid shape type you can use circle or rectangle")


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
        pygame.draw.rect(display, (0, 0, 0), (self.position.x-7.5+3, self.position.y+self.radius*2+3, 15, 20))
        pygame.draw.rect(display, (150, 150, 150), (self.position.x-7.5, self.position.y+self.radius*2, 15, 20))
        pygame.draw.ellipse(display, (0, 0, 0), (self.position.x-self.radius+3, self.position.y-self.radius+self.radius+self.radius+10+3, self.radius*2, 20))
        pygame.draw.ellipse(display, (255, 0, 0), (self.position.x-self.radius, self.position.y-self.radius+self.radius+self.radius+10, self.radius*2, 20))

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
            self.inner_particles.add([self.position.x, self.position.y], rnd.randint(0, 360), rnd.randint(1, 2)/5, rnd.randint(int(self.radius/4), int(self.radius/3)), self.inner_particles_color, 0.0)

        # this collider holds them in position, so they don't go outside the blob
        self.inner_particles_collider = pygame.Rect(self.position.x - self.radius, self.position.y - self.radius + self.radius / 2, self.radius * 2, self.radius * 2)

        self.outer_particles = ShapeParticles("circle", 0.0)
        for i in range(20):
            self.outer_particles.add([self.position.x, self.position.y], rnd.randint(0, 360), rnd.randint(1, 5)/5, rnd.randint(int(self.radius/2-5), int(self.radius/2)), tuple(self.body_color), 0.0)

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
        self.plop_sound = pygame.mixer.Sound("the plop_sound.ogg")
        self.plop_sound.set_volume(5)

        self.explosion_sound = pygame.mixer.Sound("explosion.ogg")
        self.explosion_sound.set_volume(1)

        # text and font
        self.font = pygame.font.Font("main-font.ttf", 25)
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

    def update(self, dt, foods, game_over):

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
                self.dest_color = self.const_dest_color.copy()
                self.body_color = self.const_body_color.copy()
                self.not_feed_timer = time.perf_counter()
                for p in self.inner_particles.objects:
                    p["size"] += self.growth_speed/2*dt
                for p in self.outer_particles.objects:
                    p["size"] += self.growth_speed/2*dt

        if self.radius >= self.max_radius and self.alive:
            self.inner_particles.objects = []
            self.outer_particles.objects = []
            self.not_feed_timer = 0
            if not game_over:
                self.explosion_sound.play()
            self.not_feed = False
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
                    (rnd.randint(self.const_body_color[0]-40, self.const_body_color[0]), rnd.randint(self.const_body_color[0]-40, self.const_body_color[0]), rnd.randint(self.const_body_color[0]-40, self.const_body_color[0])),
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


class SpeedBlob(Blob):
    def __init__(self, ds):
        super().__init__(ds)

        self.speed = rnd.randint(3, 6)
        self.max_radius = 50
        self.radius = rnd.randint(20, 25)
        self.body_color = [100, 0, 255]
        self.const_body_color = [100, 0, 255]
        self.const_dest_color = [255, 0, 0]
        self.dest_color = [255, 0, 0]
        self.not_feed_time = 6
        self.points = 15

        self.dest = ds[1] - ds[1] / 6 - self.radius

        self.points_text = self.font.render(f"+{self.points}", True, (255, 0, 0))


class HeavyBlob(Blob):
    def __init__(self, ds):
        super().__init__(ds)

        self.speed = rnd.randint(1, 2)/2
        self.max_radius = 200
        self.radius = rnd.randint(100, 120)
        self.position = pygame.Vector2(ds[0] / 2, ds[1] + self.radius/2)
        self.body_color = [150, 50, 0]
        self.const_body_color = [150, 50, 0]
        self.const_dest_color = [255, 0, 0]
        self.dest_color = [255, 0, 0]
        self.not_feed_time = 5
        self.points = 20
        self.growth_speed = 0.01

        self.dest = ds[1] - ds[1] / 6 - self.radius

        self.points_text = self.font.render(f"+{self.points}", True, (255, 0, 0))


class RandomBlob(Blob):
    def __init__(self, ds):
        super().__init__(ds)

        self.speed = rnd.randint(1, 2)
        self.max_radius = 75
        self.radius = rnd.randint(20, 35)
        self.growth_speed = 0.05
        self.body_color = [150, 150, 250]
        self.const_body_color = [150, 150, 250]
        self.const_dest_color = [255, 0, 0]
        self.dest_color = [255, 0, 0]
        self.not_feed_time = 6
        self.points = 25

        self.dest = ds[1] - ds[1] / 6 - self.radius

        self.points_text = self.font.render(f"+{self.points}", True, (255, 0, 0))

        self.change_dir_timer = time.perf_counter()
        self.change_dir_time = rnd.randint(1, 6)

    def update(self, dt, foods, game_over):
        if time.perf_counter() - self.change_dir_timer > self.change_dir_time:
            self.direction = rnd.choice([1, -1])
            self.change_dir_timer = time.perf_counter()
            self.change_dir_time = rnd.randint(1, 6)

        super().update(dt, foods, game_over)


async def main() -> None:
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
    ground_sprite = pygame.image.load("ground.png").convert()
    ground_sprite.set_colorkey((255, 255, 255))

    icon_sprite = pygame.image.load("icon.png").convert()

    button_press_sound = pygame.mixer.Sound("button_press.ogg")

    pygame.mixer.music.load("music-for-game.ogg")
    pygame.mixer.music.set_volume(0.1)

    pygame.mixer.music.play(-1)

    main_font = pygame.font.Font("main-font.ttf", 40)
    secondary_font = pygame.font.Font("main-font.ttf", 25)
    title_font = pygame.font.Font("title-font.ttf", 70)

    # logic variables
    points = 0
    background_points = [[i] for i in range(-200, DS[1] + 100, 100)]
    background_particles = ShapeParticles("circle", 0.0)
    display_offset = [0, 0]
    game_over = False
    game_over_sound = pygame.mixer.Sound("game-over-sound.ogg")

    game_over_gui_position = pygame.Vector2(DS[0]/2, DS[1]/2-600)
    game_over_gui_dest_position = pygame.Vector2(DS[0]/2, DS[1]/2)

    game_started = False

    game_started_gui_position = pygame.Vector2(DS[0]/2, DS[1]/2)
    game_started_gui_dest_position = game_started_gui_position
    play_button_pressed = False,

    # entities
    feeder = Feeder(DS)
    blobs = []

    # timers
    last_time = time.perf_counter()
    spawn_timer = time.perf_counter()
    spawn_time = 2

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
        if time.perf_counter() - spawn_timer > spawn_time*dt and not game_over and game_started:
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

            game_started_gui_position.x += (game_started_gui_dest_position.x - game_started_gui_position.x) / 20
            game_started_gui_position.y += (game_started_gui_dest_position.y - game_started_gui_position.y) / 20

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

        # drawing and updating the Game Over GUI
        if game_over:
            game_over_gui_position.x += (game_over_gui_dest_position.x - game_over_gui_position.x) / 20
            game_over_gui_position.y += (game_over_gui_dest_position.y - game_over_gui_position.y) / 20

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

        await asyncio.sleep(0)

    pygame.quit()
    return


if __name__ == '__main__':
    asyncio.run(main())
