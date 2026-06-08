import pygame
import math
from sprite_loader import WeepingAngelSprite
from systems.particles import ParticleSystem


class WeepingAngel:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.size = 48
        self.frozen = False
        self.state = "stack"
        self.speed = 2.5
        self.sprite = WeepingAngelSprite(
            "assets/sprites/weeping_angel.png",
            scale=1
        )

        # PARTICLE SETUP
        self.particles = ParticleSystem()
        self.dust_timer = 0
        self.DUST_INTERVAL = 12

    def update(self, player_pos, player_size, angle,
               cone_angle, flashlight_radius, valid_rooms=None):
        ecx = self.pos.x + self.size // 2
        ecy = self.pos.y + self.size // 2
        pcx = player_pos.x + player_size // 2
        pcy = player_pos.y + player_size // 2

        dist_to_player = pygame.Vector2(ecx, ecy).distance_to(
                         pygame.Vector2(pcx, pcy))

        angle_to_angel = math.atan2(ecy - pcy, ecx - pcx)
        angle_diff = abs(math.atan2(
            math.sin(angle_to_angel - angle),
            math.cos(angle_to_angel - angle)
        ))
        in_flashlight = (angle_diff < cone_angle / 2 and
                         dist_to_player < flashlight_radius)

        if in_flashlight:
            self.frozen = True
            self.state  = "frozen"
            self.particles.update()
            return

        self.frozen = False
        self.state = "stalk"

        direction = pygame.Vector2(pcx - ecx, pcy - ecy)
        if direction.length() > 0:
            direction = direction.normalize()

        new_pos = self.pos + direction * self.speed

        if self._in_valid_area(new_pos, valid_rooms):
            self.pos = new_pos

        self.dust_timer += 1
        if self.dust_timer >= self.DUST_INTERVAL:
            self.dust_timer = 0
            self.particles.emit(
                ecx, ecy,
                colour=(180, 220, 255),
                count=3,
                speed=0.6,
                size=2,
                lifetime=90
            )

        self.particles.update()

    def draw(self, screen):
        self.particles.draw(screen)

        self.sprite.draw(
            screen,
            int(self.pos.x),
            int(self.pos.y),
            frozen=self.frozen
        )

        try:
            font = pygame.font.SysFont("courier", 12)
        except:
            font = pygame.font.SysFont(None, 12)

        if self.frozen:
            label = font.render("...", True, (200, 200, 255))
            screen.blit(label, (self.pos.x, self.pos.y - 18))

    def get_rect(self):
        return pygame.Rect(self.pos.x, self.pos.y,
                           self.size, self.size)

    def _in_valid_area(self, pos, valid_rooms):
        if valid_rooms is None:
            return True
        entity_rect = pygame.Rect(
            pos.x, pos.y, self.size, self.size)
        return any(room.contains(entity_rect)
                   for room in valid_rooms)