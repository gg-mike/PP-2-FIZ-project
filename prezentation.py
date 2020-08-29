from math import hypot, ceil
from random import randrange
from numpy import array, dot, linalg
import time
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # Hides information about pygame
import pygame as PG

# Constants
TITLE = "Collisions"
DEFAULT_WINDOW_SIZE = (1000, 600)
WIDTH, HEIGHT = DEFAULT_WINDOW_SIZE
FPS = 60
PLAYBACK_SPEED = 1.0
ParticleRadius = 16
ParticleCount = 20
TimeDelta = 4
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
# initialize pygame and create window
PG.init()
screen = PG.display.set_mode(DEFAULT_WINDOW_SIZE, flags=PG.RESIZABLE)
PG.display.set_caption(TITLE)
PG.display.set_icon(PG.image.load("graphics/icon.png"))
# Assets
CellImage = PG.image.load("graphics/blue_particle.png").convert()
RingImage = PG.image.load("graphics/red_particle.png").convert()


# Classes
class Particle(PG.sprite.Sprite):
    def __init__(self, x, y, radius, v):
        PG.sprite.Sprite.__init__(self)
        self.radius = radius
        self.image = PG.transform.scale(CellImage, (radius * 2, radius * 2))
        self.rect = self.image.get_rect()
        self.image.convert_alpha()
        self.rect.centerx = x
        self.rect.centery = y
        self.v = v
        self.move = array([0, 0])
        self.mass = 1

    def update(self):
        self.move = self.move + self.v * elapsed_time * PLAYBACK_SPEED
        self.rect.centerx += int(self.move[0])
        self.rect.centery += int(self.move[1])
        self.move[0] -= int(self.move[0])
        self.move[1] -= int(self.move[1])

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.v[0] = -self.v[0]
            self.collision(0)
        if self.rect.left < 0:
            self.rect.left = 0
            self.v[0] = -self.v[0]
            self.collision(0)
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.v[1] = -self.v[1]
            self.collision(0)
        if self.rect.top < 0:
            self.rect.top = 0
            self.v[1] = -self.v[1]
            self.collision(0)
        self.specials()

    def specials(self):
        pass

    def collision(self, _):
        pass


class RedParticle(Particle):
    def __init__(self, x, y, radius, v):
        Particle.__init__(self, x, y, radius, v)
        self.image = PG.transform.scale(RingImage, (radius * 2, radius * 2))
        self.rect = self.image.get_rect()
        #self.image.set_colorkey(WHITE)
        self.timer = time.time()
        self.collisions = self.distance = 0
        self.last_position = array([x, y])

    def specials(self):
        if time.time() - self.timer > TimeDelta:
            saveData.append(f"{self.collisions} : {int(self.distance)}\n")
            self.timer = time.time()
            self.collisions = self.distance = 0

    def collision(self, count):
        self.collisions += count
        position = array([self.rect.centerx, self.rect.centery])
        self.distance += linalg.norm(position - self.last_position)
        self.last_position = position


# Functions
def events():
    global clicked_particle, FPS, PLAYBACK_SPEED, running, paused
    for event in PG.event.get():
        if event.type == PG.QUIT:  # Quit program
            running = False
        elif event.type == PG.VIDEORESIZE:  # full screen clicked
            global WIDTH, HEIGHT, screen
            WIDTH, HEIGHT = event.size
            screen = PG.display.set_mode(event.size, flags=PG.RESIZABLE)
        elif event.type == PG.KEYDOWN:  # key pressed
            if event.key == PG.K_ESCAPE:  # esc quit program
                running = False
            elif event.key == PG.K_s:
                for par in all_particles:
                    par.v = array([0, 0])
            elif event.key == PG.K_SPACE:
                paused = not paused
            elif event.key == PG.K_MINUS:
                if FPS > 10:
                    FPS -= 10
            elif event.key == PG.K_EQUALS:
                FPS += 10
            elif event.key == PG.K_UP:
                if 0.5 <= PLAYBACK_SPEED < 2.0:
                    PLAYBACK_SPEED += 0.5
                elif 0.1 <= PLAYBACK_SPEED < 0.5:
                    PLAYBACK_SPEED += 0.1
            elif event.key == PG.K_DOWN:
                if 0.5 < PLAYBACK_SPEED <= 2.0:
                    PLAYBACK_SPEED -= 0.5
                elif 0.1 < PLAYBACK_SPEED <= 0.5:
                    PLAYBACK_SPEED -= 0.1
        elif event.type == PG.MOUSEBUTTONDOWN:  # mouse pressed
            if event.button == 1:  # left mouse clicked
                pos = PG.mouse.get_pos()
                clicked_sprites = [s for s in all_sprites if s.rect.collidepoint(pos)]
                if clicked_sprites:
                    clicked_particle = [clicked_sprites[0], pos]
                else:
                    particle = Particle(*pos, ParticleRadius, array([0, 0]))
                    all_sprites.add(particle)
                    all_particles.append(particle)
            elif event.button == 3:  # right mouse clicked
                if clicked_particle:
                    clicked_particle = False
                else:
                    pos = PG.mouse.get_pos()
                    clicked_sprites = [s for s in all_sprites if s.rect.collidepoint(pos)]
                    if clicked_sprites:
                        all_particles.remove(clicked_sprites[0])
                        clicked_sprites[0].kill()
        elif event.type == PG.MOUSEBUTTONUP and clicked_particle:  # mouse unclicked
            mx, my = PG.mouse.get_pos()
            clicked_particle[0].v = array([(clicked_particle[1][0] - mx), (clicked_particle[1][1] - my)]) * 5
            clicked_particle = False

    if clicked_particle:
        mx, my = PG.mouse.get_pos()
        clicked_particle[0].rect.centerx = mx
        clicked_particle[0].rect.centery = my
        clicked_particle[0].v = array([0, 0])
        PG.draw.line(screen, RED, (clicked_particle[1]), (mx, my))


def check_collisions():
    for s in range(len(all_particles)):
        for t in range(s + 1, len(all_particles)):
            source = all_particles[s]
            target = all_particles[t]
            min_distance = (source.radius + target.radius) ** 2
            distance = (source.rect.centerx - target.rect.centerx) ** 2 + (
                    source.rect.centery - target.rect.centery) ** 2
            if distance <= min_distance:  # if collision
                # source.move = target.move = array([0, 0])
                overlapping(source, target, distance ** 0.5)
                collision(source, target)
                target.collision(1)
                source.collision(1)


def overlapping(source, target, distance):
    overlap = (source.radius + target.radius - distance) / 2.0
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


# Create sprite groups and other
clock = PG.time.Clock()
all_sprites = PG.sprite.Group()
all_particles = []
clicked_particle = False
# Add random Particles
for i in range(ParticleCount):
    m = Particle(randrange(WIDTH), randrange(HEIGHT), ParticleRadius,
                 array([randrange(-100, 100), randrange(-100, 100)]))
    all_sprites.add(m)
    all_particles.append(m)

red_par_init_speed = randrange(0, 100)
m = RedParticle(randrange(WIDTH), randrange(HEIGHT), ParticleRadius, array([red_par_init_speed, red_par_init_speed]))
all_sprites.add(m)
all_particles.append(m)
start_time = time.time()
elapsed_time = 0.0
paused_time = 0.0
running = True
paused = False
print(f"\rFPS: \t{FPS} | PLAYBACK SPEED: x{PLAYBACK_SPEED}", sep=' ', end='')
saveData = [f"TimeDelta: {TimeDelta}\nParticles: {ParticleCount}\ncollisions : distance\n"]
# Game loop
while running:
    prev_fps = FPS
    prev_playback_speed = PLAYBACK_SPEED
    screen.fill(GREY)
    events()  # Process input (events)
    if paused:
        paused_time = time.time() if paused_time == 0.0 else paused_time
    else:
        check_collisions()  # physics
        if paused_time == 0.0:
            elapsed_time = time.time() - start_time
        else:
            elapsed_time = paused_time - start_time
            paused_time = 0.0
        start_time = time.time()
        all_sprites.update()  # physics
    all_sprites.draw(screen)
    clock.tick(FPS)
    PG.display.flip()
    PLAYBACK_SPEED = round(PLAYBACK_SPEED, 1)
    if prev_fps != FPS or prev_playback_speed != PLAYBACK_SPEED:
        print(f"\rFPS: \t{FPS} | PLAYBACK SPEED: x{PLAYBACK_SPEED}", sep=' ', end='')

PG.quit()