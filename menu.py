import pygame
import sys


def run_menu(screen, clock):
    bg = pygame.image.load("assets/images/menu_bg.png").convert()
    bg = pygame.transform.scale(bg, screen.get_size())

    try:
        font_title   = pygame.font.Font("assets/fonts/menu_font.ttf", 90)
        font_menu    = pygame.font.Font("assets/fonts/menu_font.ttf", 32)
        font_tagline = pygame.font.Font("assets/fonts/menu_font.ttf", 18)
    except:
        font_title   = pygame.font.SysFont("courier", 90, bold=True)
        font_menu    = pygame.font.SysFont("courier", 32)
        font_tagline = pygame.font.SysFont("courier", 18)

    options  = ["START NEW GAME", "LOAD GAME", "CREDITS", "EXIT"]
    selected = 0

    WHITE   = (220, 220, 220)
    RED     = (200, 40,  40)
    DIM     = (130, 130, 130)
    TAGLINE = (120, 40,  40)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(options)
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    return options[selected]

        screen.blit(bg, (0, 0))

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 40))
        screen.blit(overlay, (0, 0))

        title1 = font_title.render("LOOK", True, WHITE)
        title2 = font_title.render("AWAY", True, WHITE)
        screen.blit(title1, (80, 120))
        screen.blit(title2, (80, 210))

        menu_start_y = 420
        for i, option in enumerate(options):
            if i == selected:
                arrow = font_menu.render(">", True, RED)
                screen.blit(arrow, (80, menu_start_y + i * 55))
                text = font_menu.render(option, True, RED)
                screen.blit(text, (115, menu_start_y + i * 55))
            else:
                text = font_menu.render(option, True, DIM)
                screen.blit(text, (115, menu_start_y + i * 55))

        tagline = font_tagline.render(
            "DON'T LOOK TOO LONG.", True, TAGLINE)
        screen.blit(tagline, (80, screen.get_height() - 50))

        pygame.display.flip()
        clock.tick(60)