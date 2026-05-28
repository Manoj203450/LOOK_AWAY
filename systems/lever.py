import pygame


class Lever:
    """
    A hold-to-activate lever used in Level 6 to charge the cannon.

    The player stands near it and holds E for ACTIVATE_DURATION frames
    (3 seconds at 60 fps).  Everything else — the crewmate, movement,
    drawing — keeps running during activation.  No blocking game loop.

    Compatible with the Crewmate: exposes  .fixed (bool)  and  .rect
    so the crewmate can path to it and sabotage it without any changes.

    Usage in the level loop:
        # setup
        lever = Lever(x, y)

        # each frame
        holding = keys[pygame.K_e] and lever.is_near(pcx, pcy)
        just_activated = lever.update(holding)

        # draw
        lever.draw(screen, font_small)
    """

    NEAR_RADIUS       = 60    # px from centre — matches FuseBox.is_near
    ACTIVATE_DURATION = 180   # frames to hold E (3 s at 60 fps)

    def __init__(self, x, y, width=48, height=48):
        self.rect  = pygame.Rect(x, y, width, height)
        self.fixed = False
        self._hold_timer = 0   # counts up while player holds E nearby

        # colours
        self._col_unfixed = (80,  60,  30)
        self._col_fixed   = (60, 180,  80)
        self._col_border  = (160, 130,  60)

    # ────────────────────────────────────────────────────────────────

    def is_near(self, pcx, pcy):
        centre = pygame.Vector2(self.rect.centerx, self.rect.centery)
        return pygame.Vector2(pcx, pcy).distance_to(centre) < self.NEAR_RADIUS

    def update(self, holding_e):
        """
        Call once per frame.
        holding_e : bool — True when the player is near AND pressing E.

        Returns True on the single frame the lever becomes activated,
        False every other frame.
        """
        if self.fixed:
            self._hold_timer = 0
            return False

        if holding_e:
            self._hold_timer += 1
            if self._hold_timer >= self.ACTIVATE_DURATION:
                self._hold_timer = 0
                self.fixed = True
                return True
        else:
            # Reset progress if player releases or walks away
            self._hold_timer = 0

        return False

    def draw(self, screen, font_small):
        # Body
        colour = self._col_fixed if self.fixed else self._col_unfixed
        pygame.draw.rect(screen, colour, self.rect)
        pygame.draw.rect(screen, self._col_border, self.rect, 2)

        # Label
        try:
            text = font_small.render(
                "LEVER" if not self.fixed else "ACTIVE",
                True,
                (220, 220, 180) if not self.fixed else (140, 255, 140)
            )
            screen.blit(text, (self.rect.centerx - text.get_width() // 2,
                                self.rect.centery - text.get_height() // 2))
        except Exception:
            pass

        # Hold-progress bar (only shown while player is actively holding)
        if not self.fixed and self._hold_timer > 0:
            bar_w    = self.rect.width
            filled_w = int(bar_w * self._hold_timer / self.ACTIVATE_DURATION)
            bar_y    = self.rect.bottom + 4
            pygame.draw.rect(screen, (50, 50, 50),
                             (self.rect.x, bar_y, bar_w, 6))
            pygame.draw.rect(screen, (100, 220, 120),
                             (self.rect.x, bar_y, filled_w, 6))

        # "HOLD E" prompt — only when timer is not yet running
        if not self.fixed and self._hold_timer == 0:
            try:
                hint = font_small.render("HOLD E", True, (160, 160, 100))
                screen.blit(hint, (self.rect.centerx - hint.get_width() // 2,
                                   self.rect.top - 18))
            except Exception:
                pass
