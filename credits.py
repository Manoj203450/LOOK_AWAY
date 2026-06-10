import pygame
import sys


def run_credits(screen, clock):
    WIDTH, HEIGHT = screen.get_size()

    try:
        font_title = pygame.font.Font("assets/fonts/mybleedingscars_ot.otf", 48)
    except:
        font_title = pygame.font.SysFont("courier", 48, bold=True)

    try:
        font = pygame.font.Font("assets/fonts/menu_font.ttf", 24)
        font_small = pygame.font.Font("assets/fonts/menu_font.ttf", 16)
    except:
        font = pygame.font.SysFont("courier", 24)
        font_small = pygame.font.SysFont("courier", 16)

    WHITE = (220, 220, 220)
    DIM = (120, 120, 120)
    RED = (180, 30,  30)
    HEADER = (100, 100, 100)
    DIVIDER = (50,  50,  50)

    credits_data = [
        ("title", "LOOK AWAY", WHITE),
        ("gap",),
        ("section", "DEVELOPED BY"),
        ("person", "Manoj    TP086203", [
            "Special Effects, Game Systems",
            "Watchers, Worshippers, Moon Entity",
            "Levels 1, 2, 3",
        ]),
        ("person", "Leonardo TP081483", [
            "Level 4, Assets, Shade Enemy",
        ]),
        ("person", "Ruben    TP079847", [
            "Level 6, Ending Cinematic",
        ]),
        ("person", "Pieter   TP079048", [
            "Level 5, Levels BGM, Game SFX",
            "Menu Settings with Mouse Support",
        ]),
        ("gap",),
        ("section", "TOOLS USED"),
        ("single", "Python + Pygame", (180, 180, 180)),
        ("gap",),
        ("section", "ASSETS"),
        ("single", "Background — AI Generated", (180, 180, 180)),
        ("gap",),
        ("section", "SPECIAL THANKS"),
        ("single", "APU University!!!!!!!!", (180, 180, 180)),
        ("gap",),
        ("single",  "DON'T LOOK TOO LONG.", RED),
    ]

    LEFT_COL  = WIDTH // 2 - 320
    RIGHT_COL = WIDTH // 2 + 40
    DIVIDER_X = WIDTH // 2 + 20

    def entry_height(entry):
        if entry[0] == "gap":
            return 30
        if entry[0] == "title":
            return font_title.get_height() + 16
        if entry[0] == "section":
            return font.get_height() + 24
        if entry[0] == "person":
            rows = max(1, len(entry[2]))
            return rows * (font_small.get_height() + 6) + 16
        if entry[0] == "single":
            return font.get_height() + 16
        return 0

    total_height = sum(entry_height(e) for e in credits_data)

    scroll_y     = float(HEIGHT)
    scroll_speed = 1.2

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN,
                                 pygame.K_SPACE):
                    return

        screen.fill((0, 0, 0))

        y = int(scroll_y)

        for entry in credits_data:
            kind = entry[0]

            if kind == "title":
                if -font_title.get_height() < y < HEIGHT:
                    surf = font_title.render(entry[1], True, entry[2])
                    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))
                y += font_title.get_height() + 16
                continue

            if kind == "gap":
                y += 30
                continue

            if kind == "section":
                if -font.get_height() < y < HEIGHT:
                    surf = font.render(entry[1], True, HEADER)
                    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))
                    pygame.draw.line(screen, DIVIDER,
                                     (LEFT_COL, y + font.get_height() + 4),
                                     (RIGHT_COL + 260, y + font.get_height() + 4), 1)
                y += font.get_height() + 24
                continue

            if kind == "single":
                if -font.get_height() < y < HEIGHT:
                    surf = font.render(entry[1], True, entry[2])
                    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))
                y += font.get_height() + 16
                continue

            if kind == "person":
                name  = entry[1]
                roles = entry[2]
                rows  = max(1, len(roles))
                h = rows * (font_small.get_height() + 6)

                if -h < y < HEIGHT:
                    name_surf = font.render(name, True, WHITE)
                    screen.blit(name_surf, (LEFT_COL, y))

                    pygame.draw.line(screen, DIVIDER,
                                     (DIVIDER_X, y),
                                     (DIVIDER_X, y + h), 1)

                    for j, role in enumerate(roles):
                        role_surf = font_small.render(role, True, DIM)
                        screen.blit(role_surf,
                                    (RIGHT_COL,
                                     y + j * (font_small.get_height() + 6)))

                y += h + 16
                continue

        scroll_y -= scroll_speed
        if scroll_y + total_height < 0:
            scroll_y = float(HEIGHT)

        hint = font_small.render(
            "ESC / SPACE / ENTER to return", True, (50, 50, 50))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(60)