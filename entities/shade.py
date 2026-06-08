import pygame
import math
from sprite_loader import WeepingAngelSprite
from systems.particles import ParticleSystem


class Shade:
    STUN_DURATION = 150

    def __init__(self, x, y, speed=2.0):
        self.pos = pygame.Vector2(x, y)
        self.size = 48
        self.speed = speed
        self.active  = False
        self.stun_timer = 0
        self.sprite = WeepingAngelSprite(
            "assets/sprites/shade.png", scale=1)

        self.particles = ParticleSystem()
        self.trail_timer = 0
        self.TRAIL_INTERVAL = 6

    def stun(self, hit_x=None, hit_y=None):
        self.stun_timer = self.STUN_DURATION
        self.active = False

    def update(self, player_pos, player_size, angle,
               cone_angle, flashlight_radius, valid_rooms=None):

        if self.stun_timer > 0:
            self.stun_timer -= 1
            self.active = False
            self.particles.update()
            return

        ecx = self.pos.x + self.size // 2
        ecy = self.pos.y + self.size // 2
        pcx = player_pos.x + player_size // 2
        pcy = player_pos.y + player_size // 2

        dist = pygame.Vector2(ecx, ecy).distance_to(
                  pygame.Vector2(pcx, pcy))
        ang_to = math.atan2(ecy - pcy, ecx - pcx)
        diff = abs(math.atan2(math.sin(ang_to - angle),
                                 math.cos(ang_to - angle)))
        in_light = (diff < cone_angle / 2 and dist < flashlight_radius)

        if in_light:
            self.active = True
            direction = pygame.Vector2(pcx - ecx, pcy - ecy)
            if direction.length() > 0:
                direction = direction.normalize()
            new_pos = self.pos + direction * self.speed
            if self._in_valid_area(new_pos, valid_rooms):
                self.pos = new_pos

            self.trail_timer += 1
            if self.trail_timer >= self.TRAIL_INTERVAL:
                self.trail_timer = 0
                self.particles.emit(
                    ecx, ecy,
                    colour=(40, 40, 40),
                    count=4,
                    speed=0.8,
                    size=3,
                    lifetime=45
                )
                self.particles.emit(
                    ecx, ecy,
                    colour=(200, 200, 200),
                    count=2,
                    speed=0.5,
                    size=2,
                    lifetime=30
                )
        else:
            self.active = False
            self.trail_timer = 0

        self.particles.update()

    def draw(self, screen):
        self.particles.draw(screen)

        self.sprite.draw(screen, int(self.pos.x), int(self.pos.y),
                         frozen=not self.active)

        if self.stun_timer > 0:
            try:
                font = pygame.font.SysFont("courier", 12)
                lbl = font.render("*", True, (180, 180, 255))
                screen.blit(lbl, (self.pos.x + 18, self.pos.y - 16))
            except Exception:
                pass

    def get_rect(self):
        return pygame.Rect(self.pos.x, self.pos.y,
                           self.size, self.size)

    def _in_valid_area(self, pos, valid_rooms):
        if valid_rooms is None:
            return True
        r = pygame.Rect(pos.x, pos.y, self.size, self.size)
        return any(room.colliderect(r) for room in valid_rooms)