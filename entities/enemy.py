import pygame
import math

class Enemy:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.size = 28
        self.speed = 1.8 # Change this if enemy is too fast
        self.color = (180, 50, 50)

        # The AI state
        self. state = "patrol"
        self.stun_timer = 0
        self.detect_range = 180
        self.patrol_points = [
            pygame.Vector2(x, y),
            pygame.Vector2(x + 200, y),
        ]
        self.patrol_index = 0

    def update(self, player_pos, player_size, valid_rooms=None, hole_rect=None):
        ecx = self.pos.x + self.size // 2
        ecy = self.pos.y + self.size // 2
        pcx = player_pos.x + player_size // 2
        pcy = player_pos.y + player_size // 2

        dist_to_player = pygame.Vector2(ecx, ecy).distance_to(
            pygame.Vector2(pcx, pcy))

        if self.state == "stunned":
            self.color = (80, 80, 80)
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.state = "patrol"
            return

        if dist_to_player < self.detect_range:
            self.state = "chase"
        else:
            if self.state == "chase":
                self.state = "patrol"

        if self.state == "chase":
            self.color = (220, 30, 30)
            direction = pygame.Vector2(pcx - ecx, pcy - ecy)
            if direction.length() > 0:
                direction = direction.normalize()
            new_pos = self.pos + direction * (self.speed * 1.6)
            if self._in_valid_area(new_pos, valid_rooms) and \
                    not self._in_hole(new_pos, hole_rect):
                self.pos = new_pos

        elif self.state == "patrol":
            self.color = (180, 50, 50)
            target = self.patrol_points[self.patrol_index]
            direction = target - self.pos
            if direction.length() < 5:
                self.patrol_index = (
                                            self.patrol_index + 1) % len(self.patrol_points)
            else:
                if direction.length() > 0:
                    direction = direction.normalize()
                new_pos = self.pos + direction * self.speed
                if self._in_valid_area(new_pos, valid_rooms) and \
                        not self._in_hole(new_pos, hole_rect):
                    self.pos = new_pos

    def _in_valid_area(self, pos, valid_rooms):
        if valid_rooms is None:
            return True
        entity_rect = pygame.Rect(pos.x, pos.y, self.size, self.size)
        return any(room.contains(entity_rect) for room in valid_rooms)

    def _in_hole(self, pos, hole_rect):
        if hole_rect is None:
            return False
        entity_rect = pygame.Rect(pos.x, pos.y, self.size, self.size)
        return hole_rect.colliderect(entity_rect)

    def stun(self, duration=180):
        self.state = "stunned"
        self.stun_timer = duration
        self.color = (80, 80, 80)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color,
                         (self.pos.x, self.pos.y, self.size, self.size))

        # Indicator that shows state of enemy
        try:
            font = pygame.font.SysFont("courier", 12)
        except:
            font = pygame.font.SysFont(None, 12)

        if self.state == "chase":
            label = font.render("!", True, (255, 80, 80))
            screen.blit(label, (self.pos.x + 8, self.pos.y - 18))
        elif self.state == "stunned":
            label = font.render("zz", True, (150, 150, 255))
            screen.blit(label, (self.pos.x + 4, self.pos.y - 18))

    def get_rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)


    def _in_valid_area(self, pos, valid_rooms):
        if valid_rooms is None:
            return True  # no restriction
        entity_rect = pygame.Rect(
            pos.x, pos.y, self.size, self.size)
        return any(room.contains(entity_rect)
                   for room in valid_rooms)