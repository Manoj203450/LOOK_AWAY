import pygame

class StationaryBox:
    def __init__(self, x, y, width, height):
        self.rect  = pygame.Rect(x, y, width, height)
        self.color = (80, 85, 100)

    def blocks_player(self, new_x, new_y, player_size, player_pos):
        player_rect = pygame.Rect(new_x, new_y, player_size, player_size)
        if player_rect.colliderect(self.rect):
            return player_pos.x, player_pos.y
        return new_x, new_y

    def blocks_light(self, player_rect):
        if self.rect.left < player_rect.centerx < self.rect.right:
            if self.rect.bottom < player_rect.top:
                return True
        return False

    def draw(self, screen, font_small):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (120, 125, 140), self.rect, 2)
        label = font_small.render("S", True, (180, 180, 200))
        screen.blit(label, (self.rect.centerx - 6, self.rect.centery - 8))


class MovableBox:
    def __init__(self, x, y, width, height):
        self.rect  = pygame.Rect(x, y, width, height)
        self.color = (100, 90, 70)

    def push(self, dx, dy, player_rect, room_bounds):
        ROOM_LEFT, ROOM_TOP, ROOM_RIGHT, ROOM_BOTTOM = room_bounds

        # Only do anything if player is touching the box
        if not player_rect.colliderect(self.rect):
            return

        # Only push if player is moving
        if dx == 0 and dy == 0:
            return

        # Move box by same amount as player
        new_bx = self.rect.x + dx
        new_by = self.rect.y + dy

        # Clamp to room (so it does not go into space)
        new_bx = max(ROOM_LEFT, min(ROOM_RIGHT  - self.rect.width,  new_bx))
        new_by = max(ROOM_TOP,  min(ROOM_BOTTOM - self.rect.height, new_by))

        self.rect.x = new_bx
        self.rect.y = new_by

    def blocks_light(self, player_rect):
        if self.rect.left < player_rect.centerx < self.rect.right:
            if self.rect.bottom < player_rect.top:
                return True
        return False

    def draw(self, screen, font_small):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (160, 140, 100), self.rect, 2)
        label = font_small.render("M", True, (220, 200, 150))
        screen.blit(label, (self.rect.centerx - 8, self.rect.centery - 8))