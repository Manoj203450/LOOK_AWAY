import pygame
from systems.particles import ParticleSystem


class Lever:
    NEAR_RADIUS = 60
    ACTIVATE_DURATION = 180

    def __init__(self, x, y, width=48, height=48):
        self.rect = pygame.Rect(x, y, width, height)
        self.fixed = False
        self._hold_timer = 0

        self._col_unfixed = (80,  60,  30)
        self._col_fixed = (60, 180,  80)
        self._col_border = (160, 130,  60)

        self.particles = ParticleSystem()

        try:
            sheet = pygame.image.load("assets/sprites/lever.png").convert_alpha()
            # Each frame is half the total width
            frame_w = sheet.get_width() // 2
            frame_h = sheet.get_height()

            # Left frame
            self.img_off = pygame.transform.scale(sheet.subsurface((0, 0, frame_w, frame_h)),(width, height))

            # Right frame
            self.img_on = pygame.transform.scale(sheet.subsurface((frame_w, 0, frame_w, frame_h)),(width, height))

        except:
            self.img_off = None
            self.img_on = None

    def is_near(self, pcx, pcy):
        centre = pygame.Vector2(self.rect.centerx, self.rect.centery)
        return pygame.Vector2(pcx, pcy).distance_to(centre) < self.NEAR_RADIUS

    def update(self, holding_e):
        if self.fixed:
            self._hold_timer = 0
            self.particles.update()
            return False

        if holding_e:
            self._hold_timer += 1
            if self._hold_timer >= self.ACTIVATE_DURATION:
                self._hold_timer = 0
                self.fixed = True
                self.particles.emit(
                    self.rect.centerx, self.rect.centery,
                    colour=(100, 180, 255),
                    count=20,
                    speed=4.0,
                    size=3,
                    lifetime=40
                )
                self.particles.emit(
                    self.rect.centerx, self.rect.centery,
                    colour=(255, 255, 255),
                    count=10,
                    speed=6.0,
                    size=2,
                    lifetime=25
                )
                self.particles.update()
                return True
        else:
            # Reset progress if player releases or walks away
            self._hold_timer = 0

        self.particles.update()
        return False

    def sabotage_effect(self):
        self.particles.emit(
            self.rect.centerx, self.rect.centery,
            colour=(255, 200, 0),
            count=15,
            speed=3.5,
            size=3,
            lifetime=35
        )
        self.particles.emit(
            self.rect.centerx, self.rect.centery,
            colour=(255, 120, 0),
            count=8,
            speed=5.0,
            size=2,
            lifetime=20
        )

    def draw(self, screen, font_small):
        self.particles.draw(screen)

        if self.fixed:
            if self.img_on:
                screen.blit(self.img_on, (self.rect.x, self.rect.y))
            else:
                pygame.draw.rect(screen, self._col_fixed, self.rect)
                pygame.draw.rect(screen, self._col_border, self.rect, 2)
        else:
            if self.img_off:
                screen.blit(self.img_off, (self.rect.x, self.rect.y))
            else:
                pygame.draw.rect(screen, self._col_unfixed, self.rect)
                pygame.draw.rect(screen, self._col_border, self.rect, 2)

        # Hold-progress bar (only shown while player is actively holding)
        if not self.fixed and self._hold_timer > 0:
            bar_w = self.rect.width
            filled_w = int(bar_w * self._hold_timer / self.ACTIVATE_DURATION)
            bar_y = self.rect.bottom + 4
            pygame.draw.rect(screen, (50, 50, 50),
                             (self.rect.x, bar_y, bar_w, 6))
            pygame.draw.rect(screen, (100, 220, 120),
                             (self.rect.x, bar_y, filled_w, 6))

        # "HOLD E" prompt, only when timer is not yet running
        if not self.fixed and self._hold_timer == 0:
            try:
                hint = font_small.render("HOLD E", True, (160, 160, 100))
                screen.blit(hint, (self.rect.centerx - hint.get_width() // 2,
                                   self.rect.top - 18))
            except Exception:
                pass