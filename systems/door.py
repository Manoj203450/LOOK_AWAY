import pygame

class KeyDoor:
    def __init__(self, x, y, width, height, door_id):
        self.rect    = pygame.Rect(x, y, width, height)
        self.door_id = door_id
        self.open    = False

    def try_open(self, player_keys):
        if self.door_id in player_keys:
            self.open = True
            player_keys.remove(self.door_id)
            return True
        return False

    def blocks_player(self, new_x, new_y, player_size, player_pos):
        if self.open:
            return new_x, new_y
        player_rect = pygame.Rect(new_x, new_y, player_size, player_size)
        if player_rect.colliderect(self.rect):
            return player_pos.x, player_pos.y
        return new_x, new_y

    def draw(self, screen, font_small):
        color = (40, 40, 40) if self.open else (60, 40, 10)
        pygame.draw.rect(screen, color, self.rect)
        if not self.open:
            pygame.draw.rect(screen, (180, 130, 40), self.rect, 3)
            label = font_small.render("K", True, (220, 180, 60))
            screen.blit(label, (self.rect.centerx - 5,
                                self.rect.centery - 8))
        else:
            pygame.draw.rect(screen, (40, 40, 40), self.rect, 2)


class FuseDoor:
    def __init__(self, x, y, width, height):
        self.rect  = pygame.Rect(x, y, width, height)
        self.open  = False

    def update(self, fuse_fixed):
        self.open = fuse_fixed

    def blocks_player(self, new_x, new_y, player_size, player_pos):
        if self.open:
            return new_x, new_y
        player_rect = pygame.Rect(new_x, new_y, player_size, player_size)
        if player_rect.colliderect(self.rect):
            return player_pos.x, player_pos.y
        return new_x, new_y

    def draw(self, screen, font_small):
        color = (40, 40, 40) if self.open else (20, 60, 80)
        pygame.draw.rect(screen, color, self.rect)
        if not self.open:
            pygame.draw.rect(screen, (60, 160, 200), self.rect, 3)
            label = font_small.render("F", True, (100, 200, 220))
            screen.blit(label, (self.rect.centerx - 5,
                                self.rect.centery - 8))
        else:
            pygame.draw.rect(screen, (40, 40, 40), self.rect, 2)


class ClosingDoor:
    def __init__(self, x, y, width, height, close_speed=0.3):
        self.rect        = pygame.Rect(x, y, width, height)
        self.open        = True
        self.closing     = False
        self.close_speed = close_speed
        self.open_height  = height
        self.current_height = 0   # starts fully open (0 = no block)

    def trigger_close(self):
        self.closing = True

    def update(self):
        if self.closing:
            self.current_height = min(
                self.open_height,
                self.current_height + self.close_speed
            )
            if self.current_height >= self.open_height:
                self.open = False

    def is_fully_closed(self):
        return self.current_height >= self.open_height

    def blocks_player(self, new_x, new_y, player_size, player_pos):
        if self.open and not self.is_fully_closed():
            return new_x, new_y
        player_rect = pygame.Rect(new_x, new_y, player_size, player_size)
        closing_rect = pygame.Rect(
            self.rect.x,
            self.rect.y,
            self.rect.width,
            int(self.current_height)
        )
        if player_rect.colliderect(closing_rect):
            return player_pos.x, player_pos.y
        return new_x, new_y

    def draw(self, screen, font_small):
        if self.current_height > 0:
            closing_rect = pygame.Rect(
                self.rect.x,
                self.rect.y,
                self.rect.width,
                int(self.current_height)
            )
            pygame.draw.rect(screen, (80, 20, 20), closing_rect)
            pygame.draw.rect(screen, (180, 40, 40), closing_rect, 2)