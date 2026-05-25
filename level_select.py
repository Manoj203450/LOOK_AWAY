import pygame
import sys


def run_level_select(screen, clock):
    WIDTH, HEIGHT = screen.get_size()

    try:
        font_title = pygame.font.Font("assets/fonts/menu_font.ttf", 48)
        font       = pygame.font.Font("assets/fonts/menu_font.ttf", 28)
        font_small = pygame.font.Font("assets/fonts/menu_font.ttf", 16)
    except:
        font_title = pygame.font.SysFont("courier", 48, bold=True)
        font       = pygame.font.SysFont("courier", 28)
        font_small = pygame.font.SysFont("courier", 16)

    # LEVELS
    levels = [
        {
            "name":        "LEVEL 1 — AWAKENING",
            "desc":        "Waking up in a crashed ship. No weapons.",
            "unlocked":    True,
            "gives_wrench": False,
        },
        {
            "name":        "LEVEL 2 — DESCENT",
            "desc":        "The moon grows closer. Find the wrench.",
            "unlocked":    True,
            "gives_wrench": False,
        },
        {
            "name": "LEVEL 3 — THE VOICE",
            "desc": "Something follows. Something speaks.",
            "unlocked": True,
            "gives_wrench": True,
        },
    ]

    selected = 0

    # Colors
    WHITE     = (220, 220, 220)
    DIM       = (100, 100, 100)
    RED       = (200, 40,  40)
    GOLD      = (220, 180, 40)
    DARK      = (10,  12,  20)
    PANEL     = (20,  24,  35)
    BORDER    = (50,  60,  80)

    # Load background
    try:
        bg = pygame.image.load("assets/images/menu_bg.png").convert()
        bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    except:
        bg = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None   # back to menu
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(levels)
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(levels)
                if event.key == pygame.K_RETURN:
                    if levels[selected]["unlocked"]:
                        return {
                            "level":       selected + 1,
                            "gives_wrench": levels[selected]["gives_wrench"],
                        }

        # DRAW
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill(DARK)

        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        # Title
        title = font_title.render("SELECT LEVEL", True, WHITE)
        screen.blit(title, (80, 60))

        hint = font_small.render(
            "W/S to navigate   ENTER to select   ESC to go back",
            True, DIM)
        screen.blit(hint, (80, 120))

        # Level cards
        card_x = 80
        card_y = 180
        card_w = WIDTH - 160
        card_h = 100
        gap    = 20

        for i, lvl in enumerate(levels):
            cy = card_y + i * (card_h + gap)

            # Card background
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            if i == selected:
                card_surf.fill((30, 40, 60, 220))
            else:
                card_surf.fill((15, 18, 28, 200))
            screen.blit(card_surf, (card_x, cy))

            # Card border
            border_color = RED if i == selected else BORDER
            pygame.draw.rect(screen, border_color,
                             (card_x, cy, card_w, card_h), 2)

            if lvl["unlocked"]:
                # Arrow selector
                if i == selected:
                    arrow = font.render(">", True, RED)
                    screen.blit(arrow, (card_x + 15, cy + card_h//2 - 14))

                # Level name
                name_color = RED if i == selected else WHITE
                name = font.render(lvl["name"], True, name_color)
                screen.blit(name, (card_x + 45, cy + 18))

                # Description
                desc = font_small.render(lvl["desc"], True, DIM)
                screen.blit(desc, (card_x + 45, cy + 58))

                # Wrench indicator
                if lvl["gives_wrench"]:
                    wrench = font_small.render(
                        "[ WRENCH PROVIDED ]", True, (180, 140, 80))
                else:
                    wrench = font_small.render(
                        "[ NO WRENCH ]", True, (100, 100, 100))
                screen.blit(wrench, (card_x + card_w - 220, cy + 38))

            else:
                # Locked level
                locked = font.render(
                    lvl["name"] + "  [ LOCKED ]", True, (60, 60, 60))
                screen.blit(locked, (card_x + 45, cy + 35))

        pygame.display.flip()
        clock.tick(60)