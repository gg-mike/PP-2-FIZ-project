import sys
from math import ceil
from random import randrange
from numpy import array, dot, linalg, isnan
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # Hides information about pygame
import pygame as PG

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


def run_simulation(ThreadID, tempResultPath, M, WIDTH, HEIGHT, ParticleRadius, ParticleCount, ParticleSpeed, SIMTIME,
                   FPS, windowed):
    dt = SIMTIME / M  # delta t
    lam = []  # avarage roads
    n = []  # collisions frequency
    # initialize Pygame
    PG.init()
    if windowed:
        # create window
        screen = PG.display.set_mode((WIDTH, HEIGHT))
        PG.display.set_caption("Collisions= " + str(ParticleCount))
        PG.display.set_icon(PG.image.load("graphics/icon.png"))
        # Assets
        CellImage = PG.image.load("graphics/blue_particle.png").convert()
        RingImage = PG.image.load("graphics/red_particle.png").convert()
    # create sprite groups
    all_sprites = PG.sprite.Group()
    all_particles = []

    # Classes
    class Particle(PG.sprite.Sprite):
        def __init__(self, x, y, radius, v):
            PG.sprite.Sprite.__init__(self)
            self.radius = radius
            self.image = PG.Surface((radius * 2, radius * 2))
            if windowed:
                self.image = PG.transform.scale(CellImage, (radius * 2, radius * 2))
                self.image.convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.centerx = x
            self.rect.centery = y
            self.v = v
            self.move = array([0, 0])
            self.mass = 1

        def update(self):
            self.rect.centerx += int(self.v[0]) * ParticleSpeed
            self.rect.centery += int(self.v[1]) * ParticleSpeed
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
                self.v[0] = -self.v[0]
                self.collision(False)
            if self.rect.left < 0:
                self.rect.left = 0
                self.v[0] = -self.v[0]
                self.collision(False)
            if self.rect.bottom > HEIGHT:
                self.rect.bottom = HEIGHT
                self.v[1] = -self.v[1]
                self.collision(False)
            if self.rect.top < 0:
                self.rect.top = 0
                self.v[1] = -self.v[1]
                self.collision(False)
            self.action()

        def action(self):
            pass

        def collision(self, _):
            pass

    class RedParticle(Particle):
        def __init__(self, x, y, radius, v):
            Particle.__init__(self, x, y, radius, v)
            if windowed:
                self.image = PG.transform.scale(RingImage, (radius * 2, radius * 2))
                self.rect = self.image.get_rect()
            self.timer = 0
            self.collisions = self.distance = 0
            self.last_position = (x, y)
            self.has_last_position = False

        def action(self):
            self.timer += 1
            if self.timer >= dt:
                if self.collisions > 0:
                    lam.append(self.distance / self.collisions)
                    n.append(self.collisions / dt)
                else:
                    lam.append(0)
                    n.append(0)
                self.timer = self.distance = self.collisions = 0
                self.has_last_position = False

        def collision(self, particle):
            if particle:
                self.collisions += 1
                if self.has_last_position:
                    position = array([self.rect.centerx, self.rect.centery])
                    self.distance += linalg.norm(position - self.last_position)
                    self.last_position = position
                else:
                    self.last_position = (self.rect.centerx, self.rect.centery)
            elif self.collisions > 0:
                position = array([self.rect.centerx, self.rect.centery])
                self.distance += linalg.norm(position - self.last_position)
                self.last_position = position

    # Functions
    def events():
        for event in PG.event.get():
            if event.type == PG.QUIT:
                sys.exit(0)

    def check_collisions():
        for s in range(len(all_particles)):
            for t in range(s + 1, len(all_particles)):
                source = all_particles[s]
                target = all_particles[t]
                min_distance = (source.radius + target.radius)
                distance = ((source.rect.centerx - target.rect.centerx) ** 2 + (
                        source.rect.centery - target.rect.centery) ** 2) ** 0.5
                if distance <= min_distance and distance >= 1:  # if collision
                    # source.move = target.move = array([0, 0])
                    overlapping(source, target, distance)
                    collision(source, target)
                    target.collision(True)
                    source.collision(True)

    def overlapping(source, target, distance):
        overlap = (source.radius + target.radius - distance) / 2
        n = array([target.rect.centerx - source.rect.centerx, target.rect.centery - source.rect.centery]) / distance
        source.rect.centerx -= ceil(overlap * n[0])
        target.rect.centerx += ceil(overlap * n[0])
        source.rect.centery -= ceil(overlap * n[1])
        target.rect.centery += ceil(overlap * n[1])

    def collision(source, target):
        normal = array([target.rect.centerx - source.rect.centerx, target.rect.centery - source.rect.centery])
        tangent = array([-normal[1], normal[0]])
        distance = linalg.norm(normal)
        n = normal / distance
        t = tangent / distance
        dst = dot(source.v, t)
        dtt = dot(target.v, t)
        dsn = dot(source.v, n)
        dtn = dot(target.v, n)
        if source.mass != target.mass:
            source.v = dst * t + (((source.mass - target.mass) * dsn + 2 * target.mass * dtn) /
                                  (source.mass + target.mass)) * n
            target.v = dtt * t + (((target.mass - source.mass) * dtn + 2 * source.mass * dsn) /
                                  (source.mass + target.mass)) * n
        else:
            source.v = dst * t + dtn * n
            target.v = dtt * t + dsn * n

    # Add red Particle
    red_par_init_speed = randrange(5, 10)
    m = RedParticle(0, 0, ParticleRadius,
                    array([red_par_init_speed, red_par_init_speed]))
    all_sprites.add(m)
    all_particles.append(m)
    # Add random Particles
    for i in range(ParticleCount):
        m = Particle(randrange(WIDTH), randrange(HEIGHT), ParticleRadius,
                     array([randrange(-10, 10), randrange(-10, 10)]))
        all_sprites.add(m)
        all_particles.append(m)

    # Game loop
    clock = PG.time.Clock()
    while SIMTIME > 0:
        SIMTIME -= 1
        events()  # Process input (events)
        check_collisions()  # physics
        all_sprites.update()  # physics
        if windowed:
            screen.fill(GREY)
            all_sprites.draw(screen)
            PG.display.flip()
        clock.tick(FPS)

    # quit pygame
    PG.quit()
    # average Data
    lamSum = nSum = 0
    for i in range(M):
        lamSum += lam[i]
        nSum += n[i]
    # save Data
    file = open(tempResultPath, "a")
    file.write(f"{nSum / M};{lamSum / M}\n")
    file.close()

    print(f"Thread {ThreadID} done")