import pygame
import math

# All these parameters are adjustable per level
def draw_flashlight(screen, darkness, pcx, pcy, angle,
                    cone_angle, flashlight_radius, num_rays=60,
                    ambient_alpha=240):
    WHITE = (255, 255, 255)
    darkness.fill((18, 20, 30)) # Refreshes darkness every frame

    # Polar coordinates sweep angle + radius -> (x, y), repeated 60 times across the cone width.
    cone_points = [(int(pcx), int(pcy))]
    for i in range(num_rays + 1):
        ray_angle = (angle - cone_angle / 2 + (cone_angle / num_rays) * i)
        ray_x = pcx + math.cos(ray_angle) * flashlight_radius
        ray_y = pcy + math.sin(ray_angle) * flashlight_radius
        cone_points.append((int(ray_x), int(ray_y)))

    # Cut a 'hole' through the darkness, shape of a cone
    pygame.draw.polygon(darkness, WHITE, cone_points)
    darkness.set_colorkey(WHITE)

    # Opacity control, used for the fixed fuse boxes feature
    darkness.set_alpha(ambient_alpha)

    screen.blit(darkness, (0, 0))