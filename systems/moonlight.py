import pygame
import random

def draw_moonlight(screen, moon_beam, moon_color):
    WIDTH, HEIGHT = screen.get_size()
    beam_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(beam_surf, moon_color, moon_beam)
    screen.blit(beam_surf, (0, 0))

def apply_glitch(screen, intensity, WIDTH, HEIGHT):
    t = intensity / 100

    if intensity > 20:
        shake_x = random.randint(-int(5 * t), int(5 * t))
        shake_y = random.randint(-int(5 * t), int(5 * t))
        shot = screen.copy()
        screen.fill((0, 0, 0))
        screen.blit(shot, (shake_x, shake_y))

    num_lines = int(15 * t)
    for _ in range(num_lines):
        y      = random.randint(0, HEIGHT)
        h      = random.randint(2, 8)
        offset = random.randint(-int(40 * t), int(40 * t))
        strip  = screen.subsurface(
            pygame.Rect(0, max(0, y), WIDTH, min(h, HEIGHT - max(0, y)))
        ).copy()
        screen.blit(strip, (offset, max(0, y)))

    if intensity > 40:
        shift = int(8 * t)
        shot  = screen.copy()
        screen.blit(shot, (-shift, 0), special_flags=pygame.BLEND_RGB_ADD)
        screen.blit(shot, (shift, 0),  special_flags=pygame.BLEND_RGB_SUB)

    vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    alpha    = int(120 * t)
    for i in range(60):
        a = max(0, alpha - i * 2)
        pygame.draw.rect(vignette, (150, 0, 200, a),
                         (i, i, WIDTH - i*2, HEIGHT - i*2), 1)
    screen.blit(vignette, (0, 0))

    if intensity > 60 and random.random() < 0.3:
        static = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for _ in range(int(200 * t)):
            sx = random.randint(0, WIDTH)
            sy = random.randint(0, HEIGHT)
            pygame.draw.rect(static, (255, 255, 255, 80), (sx, sy, 3, 2))
        screen.blit(static, (0, 0))