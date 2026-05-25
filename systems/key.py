import pygame

class Key:
    def __init__(self, x, y, key_id):
        self.pos      = pygame.Vector2(x, y)
        self.key_id   = key_id
        self.picked_up = False
        self.size     = 20

    def is_near(self, pcx, pcy, radius=30):
        return pygame.Vector2(pcx, pcy).distance_to(self.pos) < radius

    def draw(self, screen):
        if self.picked_up:
            return
        # Draw key shape
        cx = int(self.pos.x)
        cy = int(self.pos.y)
        # Key head (circle)
        pygame.draw.circle(screen, (220, 180, 40), (cx, cy), 10)
        pygame.draw.circle(screen, (255, 220, 80), (cx, cy), 10, 2)
        # Key shaft
        pygame.draw.line(screen, (220, 180, 40),
                         (cx + 10, cy), (cx + 25, cy), 4)
        # Key teeth
        pygame.draw.line(screen, (220, 180, 40),
                         (cx + 18, cy), (cx + 18, cy + 6), 3)
        pygame.draw.line(screen, (220, 180, 40),
                         (cx + 23, cy), (cx + 23, cy + 6), 3)