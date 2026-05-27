import pygame


def point_in_polygon(point, polygon):
    x, y = point
    n = len(polygon)
    inside = False
    px, py = polygon[0]
    for i in range(1, n + 1):
        qx, qy = polygon[i % n]
        if ((py > y) != (qy > y)) and (
                x < (qx - px) * (y - py) / (qy - py) + px):
            inside = not inside
        px, py = qx, qy
    return inside


class StationaryBox:
    def __init__(self, x, y, width, height):
        self.rect  = pygame.Rect(x, y, width, height)
        self.color = (80, 85, 100)
        # Load sprite
        try:
            img = pygame.image.load(
                "assets/sprites/box_stationary.png").convert_alpha()
            self.img = pygame.transform.scale(img, (width, height))
        except:
            self.img = None

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

    def blocks_beam(self, player_rect, beam_polygon):
        box_corners = [
            (self.rect.left,  self.rect.top),
            (self.rect.right, self.rect.top),
            (self.rect.left,  self.rect.bottom),
            (self.rect.right, self.rect.bottom),
        ]
        box_in_beam = any(
            point_in_polygon(corner, beam_polygon)
            for corner in box_corners
        )
        if not box_in_beam:
            return False
        if self.rect.centery < player_rect.centery:
            if (self.rect.left < player_rect.right and
                    self.rect.right > player_rect.left):
                return True
        return False

    def draw(self, screen, font_small):
        if self.img:
            screen.blit(self.img, (self.rect.x, self.rect.y))
        else:
            # Fallback rectangle
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, (120, 125, 140), self.rect, 2)
            try:
                label = font_small.render("S", True, (180, 180, 200))
                screen.blit(label,
                            (self.rect.centerx - 6,
                             self.rect.centery - 8))
            except:
                pass


class MovableBox:
    def __init__(self, x, y, width, height):
        self.rect  = pygame.Rect(x, y, width, height)
        self.color = (100, 90, 70)
        # Load sprite
        try:
            img = pygame.image.load(
                "assets/sprites/box_movable.png").convert_alpha()
            self.img = pygame.transform.scale(img, (width, height))
        except:
            self.img = None

    def push(self, dx, dy, player_rect, room_bounds,
             valid_rooms=None):
        if not player_rect.colliderect(self.rect):
            return
        if dx == 0 and dy == 0:
            return

        new_bx = self.rect.x + dx
        new_by = self.rect.y + dy

        if valid_rooms:
            test_rect = pygame.Rect(new_bx, new_by,
                                    self.rect.width,
                                    self.rect.height)
            corners = [
                (test_rect.left,  test_rect.top),
                (test_rect.right, test_rect.top),
                (test_rect.left,  test_rect.bottom),
                (test_rect.right, test_rect.bottom),
            ]
            in_bounds = all(
                any(room.collidepoint(cx, cy)
                    for room in valid_rooms)
                for cx, cy in corners
            )
            if not in_bounds:
                return
        else:
            ROOM_LEFT, ROOM_TOP, ROOM_RIGHT, ROOM_BOTTOM = room_bounds
            new_bx = max(ROOM_LEFT, min(
                ROOM_RIGHT  - self.rect.width,  new_bx))
            new_by = max(ROOM_TOP,  min(
                ROOM_BOTTOM - self.rect.height, new_by))

        self.rect.x = new_bx
        self.rect.y = new_by

    def blocks_player(self, new_x, new_y, player_size, player_pos):
        return new_x, new_y

    def blocks_light(self, player_rect):
        if self.rect.left < player_rect.centerx < self.rect.right:
            if self.rect.bottom < player_rect.top:
                return True
        return False

    def blocks_beam(self, player_rect, beam_polygon):
        box_corners = [
            (self.rect.left,  self.rect.top),
            (self.rect.right, self.rect.top),
            (self.rect.left,  self.rect.bottom),
            (self.rect.right, self.rect.bottom),
        ]
        box_in_beam = any(
            point_in_polygon(corner, beam_polygon)
            for corner in box_corners
        )
        if not box_in_beam:
            return False
        if self.rect.centery < player_rect.centery:
            if (self.rect.left < player_rect.right and
                    self.rect.right > player_rect.left):
                return True
        return False

    def draw(self, screen, font_small):
        if self.img:
            screen.blit(self.img, (self.rect.x, self.rect.y))
        else:
            # Fallback rectangle
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, (160, 140, 100), self.rect, 2)
            try:
                label = font_small.render("M", True, (220, 200, 150))
                screen.blit(label,
                            (self.rect.centerx - 8,
                             self.rect.centery - 8))
            except:
                pass