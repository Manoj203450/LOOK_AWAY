import pygame

class Chest:
    def __init__(self, x, y, item):
        self.rect     = pygame.Rect(x, y, 40, 35)
        self.item     = item
        self.opened   = False
        self.color    = (139, 100, 40)

    def is_near(self, pcx, pcy, radius=50):
        center = pygame.Vector2(self.rect.centerx, self.rect.centery)
        return pygame.Vector2(pcx, pcy).distance_to(center) < radius

    def open(self):
        if not self.opened:
            self.opened = True
            return self.item
        return None

    def draw(self, screen, font_small):
        if self.opened:
            # Draw as open chest (darker)
            pygame.draw.rect(screen, (80, 55, 20), self.rect)
            pygame.draw.rect(screen, (120, 90, 40), self.rect, 2)
            label = font_small.render("~", True, (100, 100, 100))
        else:
            # Draw as closed chest
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, (200, 160, 60), self.rect, 2)
            # Chest lid line
            pygame.draw.line(screen, (200, 160, 60),
                             (self.rect.left, self.rect.centery),
                             (self.rect.right, self.rect.centery), 2)
            # Lock dot
            pygame.draw.circle(screen, (200, 160, 60),
                               (self.rect.centerx, self.rect.centery), 4)
            label = font_small.render("?", True, (220, 180, 80))
        screen.blit(label, (self.rect.centerx - 5, self.rect.y - 18))