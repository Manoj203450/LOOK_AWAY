import pygame
import random
import math

class Moon:
    def __init__(self):
        self.state         = "hidden"   # hidden, emerging, full, flooding
        self.emerge_alpha  = 0          # 0 = invisible, 255 = fully visible
        self.flood_alpha   = 0          # moonlight flood opacity
        self.shake_timer   = 0
        self.shake_intense = 0
        self.flood_active  = False

    def trigger(self):
        if self.state == "hidden":
            self.state       = "emerging"
            self.shake_timer = 120   # 2 seconds of shake

    def update(self):
        if self.state == "emerging":
            if self.shake_timer > 0:
                self.shake_timer -= 1
                self.shake_intense = min(15, (120 - self.shake_timer) // 4)

            if self.emerge_alpha < 255.0:
                self.emerge_alpha += 0.8
                if self.emerge_alpha > 255.0:
                    self.emerge_alpha = 255.0
            else:
                self.state = "flooding"

        if self.state == "flooding":
            self.flood_active = True
            if self.flood_alpha < 255.0:
                self.flood_alpha += 0.5
                if self.flood_alpha > 255.0:
                    self.flood_alpha = 255.0

    def get_shake_offset(self):
        if self.shake_timer > 0:
            return (
                random.randint(-self.shake_intense, self.shake_intense),
                random.randint(-self.shake_intense, self.shake_intense)
            )
        return (0, 0)

    def is_flooding(self):
        return self.flood_active

    def get_flood_damage(self):
        if self.flood_active:
            return (self.flood_alpha / 255) * 0.8
        return 0

    def draw_moon(self, screen, room_rect):
        if self.state == "hidden":
            return

        cx = room_rect.centerx
        cy = room_rect.centery

        # Space background
        space = pygame.Surface(
            (room_rect.width, room_rect.height), pygame.SRCALPHA)
        space.fill((0, 0, 5, 255))
        screen.blit(space, (room_rect.x, room_rect.y))

        # Draw stars
        random.seed(42)
        for _ in range(60):
            sx = room_rect.x + random.randint(0, room_rect.width)
            sy = room_rect.y + random.randint(0, room_rect.height)
            pygame.draw.circle(screen, (255, 255, 255), (sx, sy), 1)

        # Moon circle
        moon_surf = pygame.Surface(
            (room_rect.width, room_rect.height), pygame.SRCALPHA)
        alpha = int(self.emerge_alpha)

        # Outer glow
        for r in range(100, 70, -5):
            glow_alpha = max(0, int(alpha * (1 - (r - 70) / 30) * 0.3))
            pygame.draw.circle(moon_surf, (200, 220, 255, glow_alpha),
                               (room_rect.width//2, room_rect.height//2), r)

        # Moon body
        pygame.draw.circle(moon_surf, (200, 210, 220, alpha),
                           (room_rect.width//2, room_rect.height//2), 70)

        # Craters
        craters = [(-20, -15, 12), (15, 20, 8), (-5, 25, 6),
                   (25, -10, 10), (-30, 10, 7)]
        for cx2, cy2, cr in craters:
            pygame.draw.circle(
                moon_surf,
                (170, 180, 190, alpha),
                (room_rect.width//2 + cx2, room_rect.height//2 + cy2), cr)

        screen.blit(moon_surf, (room_rect.x, room_rect.y))

    def draw_flood(self, screen):
        if not self.flood_active:
            return
        flood = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        flood.fill((200, 220, 255, int(self.flood_alpha * 0.4)))
        screen.blit(flood, (0, 0))