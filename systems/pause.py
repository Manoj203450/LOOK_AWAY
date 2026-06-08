import pygame
import sys


def run_pause(screen, clock, game_surf):

    WIDTH, HEIGHT = screen.get_size()

    try:
        font_title = pygame.font.Font("assets/fonts/menu_font.ttf", 48)
        font       = pygame.font.Font("assets/fonts/menu_font.ttf", 30)
        font_small = pygame.font.Font("assets/fonts/menu_font.ttf", 16)
    except:
        font_title = pygame.font.SysFont("courier", 48, bold=True)
        font       = pygame.font.SysFont("courier", 30)
        font_small = pygame.font.SysFont("courier", 16)

    options  = ["CONTINUE", "RESTART", "SETTINGS", "MAIN MENU"]
    selected = 0

    WHITE = (220, 220, 220)
    RED   = (200, 40,  40)
    DIM   = (100, 100, 100)

    while True:
        screen = pygame.display.get_surface()
        WIDTH, HEIGHT = screen.get_size()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "continue"
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    if options[selected] == "CONTINUE":
                        return "continue"
                    elif options[selected] == "RESTART":
                        return "restart"
                    elif options[selected] == "SETTINGS":
                        from settings_screen import run_settings
                        run_settings(screen, clock)
                    elif options[selected] == "MAIN MENU":
                        return "menu"

        # Draw frozen game frame behind pause menu
        screen.blit(game_surf, (0, 0))

        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        # Pause panel
        PANEL_W = 400
        PANEL_H = 370
        PANEL_X = WIDTH  // 2 - PANEL_W // 2
        PANEL_Y = HEIGHT // 2 - PANEL_H // 2

        panel = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
        panel.fill((10, 12, 20, 220))
        screen.blit(panel, (PANEL_X, PANEL_Y))
        pygame.draw.rect(screen, (60, 70, 90),
                         (PANEL_X, PANEL_Y, PANEL_W, PANEL_H), 2)

        # Title
        title = font_title.render("PAUSED", True, WHITE)
        screen.blit(title,
                    (WIDTH//2 - title.get_width()//2,
                     PANEL_Y + 30))

        # Options
        for i, option in enumerate(options):
            y = PANEL_Y + 120 + i * 55
            if i == selected:
                arrow = font.render(">", True, RED)
                screen.blit(arrow, (PANEL_X + 40, y))
                text = font.render(option, True, RED)
            else:
                text = font.render(option, True, DIM)
            screen.blit(text, (PANEL_X + 70, y))

        # Hint
        hint = font_small.render(
            "ESC to continue", True, (40, 40, 40))
        screen.blit(hint,
                    (WIDTH//2 - hint.get_width()//2,
                     PANEL_Y + PANEL_H - 25))

        pygame.display.flip()
        clock.tick(60)