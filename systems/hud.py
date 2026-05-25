import pygame

def draw_hud(screen, font, health, max_health, glitch_intensity, has_wrench):
    W, H = screen.get_size()

    pygame.draw.rect(screen, (40, 40, 40), (20, 20, 200, 16))

    ratio     = health / 100
    bar_color = (int(255 * (1 - ratio)), int(200 * ratio), 50)
    pygame.draw.rect(screen, bar_color, (20, 20, int(200 * ratio), 16))
    pygame.draw.rect(screen, (100, 100, 100), (20, 20, 200, 16), 1)

    label = font.render(f"VITALS: {int(health)}%", True, (180, 180, 180))
    screen.blit(label, (20, 40))

    if glitch_intensity > 10:
        warn = font.render("! LUNAR EXPOSURE DETECTED !", True, (200, 50, 50))
        screen.blit(warn, (W // 2 - warn.get_width() // 2, 20))

    if has_wrench:
        wrench_text = font.render("[ WRENCH : READY ]", True, (180, 140, 80))
    else:
        wrench_text = font.render("[ WRENCH : THROWN ]", True, (80, 80, 80))
    screen.blit(wrench_text, (20, H - 40))