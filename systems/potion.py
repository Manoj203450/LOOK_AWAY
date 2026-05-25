import pygame

MAX_POTIONS  = 3
HEAL_AMOUNT  = 30   # heals 40% of max HP

class PotionInventory:
    def __init__(self):
        self.count = 0

    def add(self):
        if self.count < MAX_POTIONS:
            self.count += 1
            return True
        return False  # inventory full

    def use(self, health, max_health):
        if self.count > 0 and health < max_health:
            self.count -= 1
            health = min(max_health, health + (max_health * HEAL_AMOUNT / 100))
            return health
        return health

    def draw(self, screen, font_small):
        W, H = screen.get_size()
        for i in range(MAX_POTIONS):
            x = W - 40 - (i * 35)
            y = H - 50
            if i < self.count:
                # Full potion - eye drop bottle shape
                # Bottle body
                pygame.draw.ellipse(screen, (80, 180, 220),
                                    (x, y + 8, 20, 26))
                # Bottleneck
                pygame.draw.rect(screen, (80, 180, 220),
                                 (x + 6, y, 8, 12))
                # Tip
                pygame.draw.ellipse(screen, (150, 220, 255),
                                    (x + 7, y - 4, 6, 8))
                # Shine
                pygame.draw.ellipse(screen, (200, 240, 255),
                                    (x + 4, y + 10, 6, 8))
                # Outline
                pygame.draw.ellipse(screen, (120, 210, 240),
                                    (x, y + 8, 20, 26), 2)
            else:
                # Empty slot
                pygame.draw.ellipse(screen, (30, 40, 50),
                                    (x, y + 8, 20, 26))
                pygame.draw.ellipse(screen, (60, 70, 80),
                                    (x, y + 8, 20, 26), 2)

        label = font_small.render("Q", True, (150, 150, 150))
        screen.blit(label, (W - MAX_POTIONS * 35 - 20, H - 55))