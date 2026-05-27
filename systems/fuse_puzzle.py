import pygame
import sys
import random
import math


class FuseBox:
    def __init__(self, x, y):

        self.rect  = pygame.Rect(x, y, 48, 48)
        self.fixed = False

        self.broken_image = pygame.image.load(
            "assets/sprites/fusebox_broken.png"
        ).convert_alpha()

        self.fixed_image = pygame.image.load(
            "assets/sprites/fusebox_fixed.png"
        ).convert_alpha()

        self.broken_image = pygame.transform.scale(
            self.broken_image,
            (self.rect.width, self.rect.height)
        )

        self.fixed_image = pygame.transform.scale(
            self.fixed_image,
            (self.rect.width, self.rect.height)
        )

    def is_near(self, pcx, pcy, radius=60):

        center = pygame.Vector2(
            self.rect.centerx,
            self.rect.centery
        )

        return pygame.Vector2(
            pcx, pcy
        ).distance_to(center) < radius

    def draw(self, screen, font_small):

        if self.fixed:
            screen.blit(
                self.fixed_image,
                self.rect.topleft
            )
        else:
            screen.blit(
                self.broken_image,
                self.rect.topleft
            )

def run_fuse_puzzle(screen, clock):
    WIDTH, HEIGHT = screen.get_size()

    try:
        font       = pygame.font.Font("assets/fonts/menu_font.ttf", 22)
        font_small = pygame.font.Font("assets/fonts/menu_font.ttf", 16)
    except:
        font       = pygame.font.SysFont("courier", 22)
        font_small = pygame.font.SysFont("courier", 16)

    COLORS = {
        "A": (220, 50,  50),   # red
        "B": (50,  200, 50),   # green
        "C": (50,  50,  220),  # blue
        "D": (220, 220, 50),   # yellow
    }

    # Left side pins (fixed order)
    left_order  = list(COLORS.keys())

    # Right side pins (shuffled)
    right_order = list(COLORS.keys())
    random.shuffle(right_order)

    # Panel dimensions
    PW, PH   = 500, 400
    px       = WIDTH  // 2 - PW // 2
    py       = HEIGHT // 2 - PH // 2

    PIN_R    = 12   # pin circle radius
    SPACING  = 70   # vertical spacing between pins

    def left_pin_pos(i):
        return (px + 60, py + 80 + i * SPACING)

    def right_pin_pos(i):
        return (px + PW - 60, py + 80 + i * SPACING)

    # Connections: maps left key → right key (None = unconnected)
    connections  = {k: None for k in left_order}
    # Dragging state
    dragging_from = None   # left key being dragged from
    drag_pos      = None   # current mouse pos while dragging

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "cancelled"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if clicked a left pin
                for i, key in enumerate(left_order):
                    lx, ly = left_pin_pos(i)
                    if math.hypot(mx - lx, my - ly) < PIN_R + 5:
                        dragging_from = key
                        drag_pos      = (mx, my)
                        connections[key] = None  # reset existing connection

            if event.type == pygame.MOUSEMOTION:
                if dragging_from:
                    drag_pos = (mx, my)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging_from:
                    # Check if released on a right pin
                    for i, key in enumerate(right_order):
                        rx, ry = right_pin_pos(i)
                        if math.hypot(mx - rx, my - ry) < PIN_R + 5:
                            # Remove any existing connection to this right pin
                            for k in connections:
                                if connections[k] == key:
                                    connections[k] = None
                            connections[dragging_from] = key
                            break
                    dragging_from = None
                    drag_pos      = None

        # Check if solved
        solved = all(connections[k] == k for k in left_order)
        if solved:
            # Flash green and return
            for _ in range(3):
                screen.fill((0, 60, 0))
                msg = font.render("POWER RESTORED", True, (100, 255, 100))
                screen.blit(msg, (WIDTH//2 - msg.get_width()//2,
                                  HEIGHT//2 - 20))
                pygame.display.flip()
                pygame.time.wait(200)
                screen.fill((0, 0, 0))
                pygame.display.flip()
                pygame.time.wait(100)
            return "solved"

        # DRAW
        # Dim background
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Panel
        pygame.draw.rect(screen, (30, 35, 45), (px, py, PW, PH))
        pygame.draw.rect(screen, (80, 90, 110), (px, py, PW, PH), 3)

        # Title
        title = font.render("RESTORE POWER", True, (200, 200, 100))
        screen.blit(title, (px + PW//2 - title.get_width()//2, py + 18))

        hint = font_small.render("match the wires  |  ESC to cancel",
                                 True, (100, 100, 100))
        screen.blit(hint, (px + PW//2 - hint.get_width()//2, py + PH - 30))

        # Draw existing connections
        for i, key in enumerate(left_order):
            if connections[key] is not None:
                lx, ly = left_pin_pos(i)
                ri      = right_order.index(connections[key])
                rx, ry  = right_pin_pos(ri)
                pygame.draw.line(screen, COLORS[key], (lx, ly), (rx, ry), 3)

        # Draw dragging wire
        if dragging_from and drag_pos:
            i   = left_order.index(dragging_from)
            lx, ly = left_pin_pos(i)
            pygame.draw.line(screen, COLORS[dragging_from],
                             (lx, ly), drag_pos, 3)

        # Draw left pins
        for i, key in enumerate(left_order):
            lx, ly = left_pin_pos(i)
            pygame.draw.circle(screen, COLORS[key], (lx, ly), PIN_R)
            pygame.draw.circle(screen, (255, 255, 255), (lx, ly), PIN_R, 2)
            label = font_small.render(key, True, (255, 255, 255))
            screen.blit(label, (lx - 20, ly - 8))

        # Draw right pins
        for i, key in enumerate(right_order):
            rx, ry = right_pin_pos(i)
            pygame.draw.circle(screen, COLORS[key], (rx, ry), PIN_R)
            pygame.draw.circle(screen, (255, 255, 255), (rx, ry), PIN_R, 2)
            label = font_small.render(key, True, (255, 255, 255))
            screen.blit(label, (rx + 18, ry - 8))

        pygame.display.flip()
        clock.tick(60)