import pygame
import random
import math


class Particle:
    def __init__(self, x, y, colour, speed=2.0, size=4, lifetime=30):
        self.x        = float(x)
        self.y        = float(y)
        self.colour   = colour
        self.size     = size
        self.lifetime = lifetime
        self.max_life = lifetime
        angle         = random.uniform(0, math.pi * 2)
        self.vx       = math.cos(angle) * speed * random.uniform(0.5, 1.5)
        self.vy       = math.sin(angle) * speed * random.uniform(0.5, 1.5)

    def update(self):
        # move particle
        self.x += self.vx
        self.y += self.vy
        # slow down
        self.vx *= 0.92
        self.vy *= 0.92
        # tick lifetime
        self.lifetime -= 1

    def draw(self, screen):
        # fade based on remaining life
        alpha   = int(255 * (self.lifetime / self.max_life))
        current = max(1, int(self.size * (self.lifetime / self.max_life)))
        surf    = pygame.Surface((current * 2, current * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.colour, alpha), (current, current), current)
        screen.blit(surf, (int(self.x) - current, int(self.y) - current))

    def is_dead(self):
        # check expired
        return self.lifetime <= 0


class ParticleSystem:
    def __init__(self):
        # particle list
        self.particles = []

    def emit(self, x, y, colour, count=8,
             speed=2.0, size=4, lifetime=30):
        # spawn particles
        for _ in range(count):
            self.particles.append(
                Particle(x, y, colour, speed, size, lifetime))

    def update(self):
        # update all
        for p in self.particles:
            p.update()
        # remove dead
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self, screen):
        # draw all
        for p in self.particles:
            p.draw(screen)

    def clear(self):
        # wipe all
        self.particles = []