import pygame
import math

def draw_flashlight(screen, darkness, pcx, pcy, angle,
                    cone_angle, flashlight_radius, num_rays=60):
    WHITE = (255, 255, 255)
    darkness.fill((18, 20, 30))

    cone_points = [(int(pcx), int(pcy))]
    for i in range(num_rays + 1):
        ray_angle = (angle - cone_angle / 2
                     + (cone_angle / num_rays) * i)
        ray_x = pcx + math.cos(ray_angle) * flashlight_radius
        ray_y = pcy + math.sin(ray_angle) * flashlight_radius
        cone_points.append((int(ray_x), int(ray_y)))

    pygame.draw.polygon(darkness, WHITE, cone_points)
    darkness.set_colorkey(WHITE)

    darkness.set_alpha(254)

    screen.blit(darkness, (0, 0))