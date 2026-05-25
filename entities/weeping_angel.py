import pygame
import math

class WeepingAngel:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.size = 28
        self.color = (150, 150, 200)
        self.frozen = False
        self.state = "stack"
        self.speed = 2.5

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
            self.color  = (180, 180, 220)
            return

        self.frozen = False
        self.state  = "stalk"
        self.color  = (100, 100, 180)

        direction = pygame.Vector2(pcx - ecx, pcy - ecy)
        if direction.length() > 0:
            direction = direction.normalize()

        new_pos = self.pos + direction * self.speed

        # Only move if inside valid area
        if self._in_valid_area(new_pos, valid_rooms):
            self.pos = new_pos

    def draw(self, screen):
        cx = self.pos.x + self.size // 2
        cy = self.pos.y + self.size // 2
        s = self.size // 2

        # diamond shape
        diamond = [
            (cx, cy - s),
            (cx + s, cy),
            (cx, cy + s),
            (cx - s, cy),
        ]
        pygame.draw.polygon(screen, self.color, diamond)
        pygame.draw.polygon(screen, (200, 200, 200), diamond, 2)

        try:
            font = pygame.font.SysFont("courier", 12)
        except:
            font = pygame.font.SysFont(None, 12)

        if self.frozen:
            label = font.render("...", True, (200, 200, 255))
            screen.blit(label, (self.pos.x, self.pos.y - 18))

    def get_rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)

    def _in_valid_area(self, pos, valid_rooms):
        if valid_rooms is None:
            return True
        entity_rect = pygame.Rect(
            pos.x, pos.y, self.size, self.size)
        return any(room.contains(entity_rect)
                   for room in valid_rooms)