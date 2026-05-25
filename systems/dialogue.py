import pygame
import sys

def run_dialogue(screen, clock, lines, black_bg=False):
    WIDTH, HEIGHT = screen.get_size()

    try:
        font       = pygame.font.Font("assets/fonts/menu_font.ttf", 22)
        font_small = pygame.font.Font("assets/fonts/menu_font.ttf", 14)
    except:
        font       = pygame.font.SysFont("courier", 22)
        font_small = pygame.font.SysFont("courier", 14)

    DIM   = (60, 60, 60)

    BOX_H = 140
    BOX_Y = HEIGHT - BOX_H - 20
    BOX_X = 40
    BOX_W = WIDTH - 80

    def draw_box():
        # If black_bg, wipe entire screen black first
        if black_bg:
            screen.fill((0, 0, 0))

        box = pygame.Surface((BOX_W, BOX_H), pygame.SRCALPHA)
        box.fill((10, 12, 20, 210))
        screen.blit(box, (BOX_X, BOX_Y))
        pygame.draw.rect(screen, (60, 70, 90),
                         (BOX_X, BOX_Y, BOX_W, BOX_H), 2)

    for text, color in lines:
        displayed = ""
        done      = False

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "skipped"
                    if event.key == pygame.K_SPACE:
                        displayed = text
                        done      = True

            if not done:
                if len(displayed) < len(text):
                    displayed += text[len(displayed)]

            draw_box()

            render = font.render(displayed, True, color)
            screen.blit(render, (BOX_X + 20, BOX_Y + 30))

            hint = font_small.render(
                "SPACE - continue  |  ESC - skip",
                True, DIM)
            screen.blit(hint, (BOX_X + 20, BOX_Y + BOX_H - 25))

            pygame.display.flip()
            clock.tick(30)

        pygame.time.wait(300)

    return "done"