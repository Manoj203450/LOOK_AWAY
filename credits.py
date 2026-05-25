import pygame
import sys


def run_credits(screen, clock):
    WIDTH, HEIGHT = screen.get_size()

    try:
        font_title = pygame.font.Font("assets/fonts/menu_font.ttf", 48)
        font       = pygame.font.Font("assets/fonts/menu_font.ttf", 24)
        font_small = pygame.font.Font("assets/fonts/menu_font.ttf", 16)
    except:
        font_title = pygame.font.SysFont("courier", 48, bold=True)
        font       = pygame.font.SysFont("courier", 24)
        font_small = pygame.font.SysFont("courier", 16)

    try:
        bg = pygame.image.load("assets/images/menu_bg.png").convert()
        bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    except:
        bg = None

    # Credits content
    credits_lines = [
        ("LOOK AWAY", (220, 220, 220), "title"),
        ("", (0,   0,   0),  "gap"),
        ("DEVELOPED BY", (100, 100, 100), "header"),
        ("Manoj TP086203", (200, 200, 200), "name"),
        ("Ruben", (200, 200, 200), "name"),
        ("Leonardo", (200, 200, 200), "name"),
        ("Pieter", (200, 200, 200), "name"),
        ("", (0,   0,   0),  "gap"),
        ("TOOLS USED", (100, 100, 100), "header"),
        ("Python + Pygame", (180, 180, 180), "normal"),
        ("Canva — Level Design", (180, 180, 180), "normal"),
        ("", (0,   0,   0),  "gap"),
        ("ASSETS", (100, 100, 100), "header"),
        ("Background — AI Generated", (180, 180, 180), "normal"),
        ("", (0,   0,   0),  "gap"),
        ("SPECIAL THANKS", (100, 100, 100), "header"),
        ("APU University!!!!!!!!", (180, 180, 180), "normal"),
        ("", (0,   0,   0),  "gap"),
        ("DON'T LOOK TOO LONG.", (180, 30,  30),  "tagline"),
    ]

    # Scrolling
    scroll_y = HEIGHT
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

        # Draw background
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill((5, 5, 15))

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Calculate total credits height first
        total_height = 0
        for text, color, style in credits_lines:
            if style == "gap":
                total_height += 20
            elif style == "title":
                total_height += font_title.get_height() + 12
            else:
                total_height += font.get_height() + 12

        # Draw scrolling credits
        y = int(scroll_y)
        for text, color, style in credits_lines:
            if style == "gap":
                y += 20
                continue

            if style == "title":
                surf = font_title.render(text, True, color)
            elif style in ("header", "tagline", "name"):
                surf = font.render(text, True, color)
            else:
                surf = font_small.render(text, True, color)

            # Only draw if on screen
            if -surf.get_height() < y < HEIGHT:
                screen.blit(surf,
                            (WIDTH // 2 - surf.get_width() // 2, y))
            y += surf.get_height() + 12

        # Scroll up
        scroll_y -= scroll_speed

        # Reset only after everything has scrolled off the top
        if scroll_y + total_height < 0:
            scroll_y = HEIGHT

        # ESC hint at bottom
        hint = font_small.render(
            "ESC / SPACE / ENTER to return", True, (50, 50, 50))
        screen.blit(hint,
                    (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(60)