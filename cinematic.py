import pygame
import sys
import random
from math import cos, sin, pi as PI

_PARTICLE_COLOURS = [
    (80,  160, 255),   # electric blue
    (120, 200, 255),   # sky blue
    (210, 235, 255),   # white-blue
    (255, 245, 160),   # warm yellow
    (175, 130, 255),   # violet
    (100, 255, 215),   # teal
]


class ChargeParticle:
    def __init__(self, cx, cy):
        self.cx       = cx
        self.cy       = cy
        self.theta    = random.uniform(0, 360)
        self.rad      = random.uniform(100, 220)
        self.rot_spd  = random.uniform(2.0, 5.0) * random.choice([-1, 1])
        self.contract = random.uniform(0.55, 1.1)   # px per frame
        self.alpha    = random.randint(10, 50)
        self.size     = random.randint(3, 7)
        self.color    = random.choice(_PARTICLE_COLOURS)

    def update(self):
        self.theta += self.rot_spd
        self.rad   -= self.contract
        self.alpha  = min(240, self.alpha + 5)

    def world_pos(self):
        a = self.theta * PI / 180
        return (self.cx + self.rad * cos(a),
                self.cy + self.rad * sin(a) * 0.5)   # flattened (elliptical)

    def is_dead(self):
        return self.rad < 5

    def draw(self, surface, view_top, screen_w, screen_h):
        wx, wy = self.world_pos()
        sx, sy = int(wx), int(wy - view_top)
        if not (-self.size <= sx <= screen_w + self.size and
                -self.size <= sy <= screen_h + self.size):
            return

        s = pygame.Surface((self.size * 2 + 2, self.size * 2 + 2), pygame.SRCALPHA)

        pygame.draw.circle(s, (*self.color, int(self.alpha)),(self.size + 1, self.size + 1), self.size)

        surface.blit(s, (sx - self.size - 1, sy - self.size - 1))


def run_cinematic_ending(screen, clock):
    WIDTH, HEIGHT = screen.get_size()

    # --
    # Font
    # --
    try:
        font_big   = pygame.font.Font("assets/fonts/menu_font.ttf", 52)
        font_small = pygame.font.Font("assets/fonts/menu_font.ttf", 20)
    except Exception:
        font_big   = pygame.font.SysFont("courier", 52, bold=True)
        font_small = pygame.font.SysFont("courier", 20)

    # --
    # Cannon Sprite
    # --
    cannon_img = None
    cannon_w, cannon_h = 100, 80
    try:
        sheet  = pygame.image.load("assets/sprites/cannon.png").convert_alpha()
        fw, fh = sheet.get_width() // 2, sheet.get_height()
        th     = cannon_h
        tw     = int(fw * th / fh)
        cannon_w = tw
        cannon_img = pygame.transform.scale(
            sheet.subsurface((fw, 0, fw, fh)), (tw, th))
    except Exception:
        pass

    # --
    # Element positions
    # --
    CANNON_WX     = WIDTH // 2
    CANNON_WY     = 220
    BARREL_TIP_WY = CANNON_WY - 40     # particles converge here and laser starts here
    MOON_WX       = WIDTH // 2
    MOON_WY       = -560

    # --
    # Camera
    # --
    # view_top = world-Y that maps to screen top edge.
    # screen_y = world_y - view_top
    view_top        = 0.0
    target_view_top = 0.0

    def to_screen(wx, wy):
        return int(wx), int(wy - view_top)

    # --
    # Random stars creation
    # --
    random.seed(77)
    STARS = [(random.randint(0, WIDTH), random.randint(int(MOON_WY) - 200, int(CANNON_WY) + 400)) for _ in range(120)]
    random.seed()

    # --
    # Moon entity
    # --
    CRATERS      = [(-22, -18, 13), (18, 22, 9), (-6, 28, 7), (28, -12, 11), (-32, 12, 8), (10, -30, 6)]
    BASE_MOON_R  = 75

    # --
    # Helper: Draw moon
    # --
    def draw_moon(radius, red_t):
        cx, cy = to_screen(MOON_WX, MOON_WY)
        R      = max(1, int(radius))
        pad    = 40
        s      = pygame.Surface((R * 2 + pad * 2, R * 2 + pad * 2), pygame.SRCALPHA)
        mc     = (R + pad, R + pad)

        # glow ring
        for gr in range(R + 35, R, -4):
            ga = max(0, int(45 * (1.0 - (gr - R) / 35.0)))
            gc = (int(180 + 75 * red_t),
                  int(220 * (1 - red_t * 0.8)),
                  int(255 * (1 - red_t)),
                  ga)
            pygame.draw.circle(s, gc, mc, gr)

        # body
        bc = (int(195 + 60 * red_t),
              int(210 * (1 - red_t * 0.65)),
              int(218 * (1 - red_t)),
              255)
        pygame.draw.circle(s, bc, mc, R)

        # craters scale with moon, fade as it reddens
        ca = int(255 * (1.0 - red_t * 0.85))
        for ox, oy, cr in CRATERS:
            so  = int(ox * R / BASE_MOON_R)
            so2 = int(oy * R / BASE_MOON_R)
            scr = max(1, int(cr * R / BASE_MOON_R))
            pygame.draw.circle(s, (168, 178, 188, ca),(mc[0] + so, mc[1] + so2), scr)

        screen.blit(s, (cx - R - pad, cy - R - pad))

    # --
    # Helper: Draw laser
    # --
    def draw_laser(alpha, absorb_frac):
        if alpha <= 0:
            return
        b_sx, b_sy = to_screen(CANNON_WX, BARREL_TIP_WY)
        t_sx, t_sy = to_screen(MOON_WX,   MOON_WY)

        eff_top_sy = int(t_sy + (b_sy - t_sy) * absorb_frac)
        h = b_sy - eff_top_sy
        if h <= 0:
            return

        lw     = 8
        layers = [
            (lw * 4, (120, 180, 255), 0.18),
            (lw * 2, (170, 215, 255), 0.45),
            (lw,     (230, 245, 255), 1.00),
        ]
        for width, col, a_frac in layers:
            ls = pygame.Surface((width, h), pygame.SRCALPHA)
            ls.fill((*col, int(alpha * a_frac)))
            screen.blit(ls, (CANNON_WX - width // 2, eff_top_sy))

    # --
    # Helper: Draw ship
    # --
    def draw_ship():
        ship_top_wy = CANNON_WY + cannon_h // 2 + 4
        sy_top      = int(ship_top_wy - view_top)
        if sy_top > HEIGHT + 10:
            return

        cx     = CANNON_WX
        hull_w = 220
        hull_h = 150
        hx     = cx - hull_w // 2
        hy     = sy_top

        # main hull
        pygame.draw.rect(screen, (50, 53, 65), (hx, hy, hull_w, hull_h))
        # centre recessed panel
        pygame.draw.rect(screen, (36, 38, 48), (hx + 60, hy + 14, 100, hull_h - 28))
        # horizontal ribs
        for i in range(4):
            rib_y = hy + 18 + i * 30
            pygame.draw.line(screen, (68, 72, 88),
                             (hx + 8,          rib_y),
                             (hx + hull_w - 8, rib_y), 1)
        # detail bolts
        for bx_off in (70, 110, 150):
            pygame.draw.rect(screen, (55, 58, 72),
                             (hx + bx_off - 3, hy + hull_h // 2 - 3, 6, 6))
        # hull border
        pygame.draw.rect(screen, (65, 70, 85), (hx, hy, hull_w, hull_h), 2)

        # left wing
        wing_w, wing_h = 65, 55
        lwx = hx - wing_w
        lwy = hy + 24
        pygame.draw.rect(screen, (42, 45, 56), (lwx, lwy, wing_w, wing_h))
        pygame.draw.rect(screen, (55, 58, 72),  (lwx + 8,  lwy + 10, 38, 24))
        pygame.draw.rect(screen, (62, 66, 80),  (lwx, lwy, wing_w, wing_h), 1)

        # right wing
        rwx = hx + hull_w
        pygame.draw.rect(screen, (42, 45, 56), (rwx, lwy, wing_w, wing_h))
        pygame.draw.rect(screen, (55, 58, 72),  (rwx + 19, lwy + 10, 38, 24))
        pygame.draw.rect(screen, (62, 66, 80),  (rwx, lwy, wing_w, wing_h), 1)

        # exhaust nozzles
        noz_y = hy + hull_h - 18
        for ox in (-70, -30, 10, 50):
            nx = cx + ox
            pygame.draw.rect(screen, (28, 30, 40), (nx, noz_y, 20, 16))
            pygame.draw.rect(screen, (55, 58, 72), (nx, noz_y, 20, 16), 1)

        # cannon collar
        col_w, col_h = 38, 20
        col_x = cx - col_w // 2
        col_y = sy_top - col_h
        pygame.draw.rect(screen, (62, 65, 78),  (col_x, col_y, col_w, col_h))
        pygame.draw.rect(screen, (82, 87, 102), (col_x, col_y, col_w, col_h), 1)



    # --
    # States
    # --
    S_CHARGING  = 0
    S_FIRING    = 1
    S_PANNING   = 2
    S_ABSORBING = 3
    S_PAUSE     = 4
    S_MOON_RED  = 5
    S_FADE      = 6
    S_TEXT      = 7

    DURATIONS = {
        S_CHARGING:  300,   # 5s
        S_FIRING:     60,   # 1s
        S_PANNING:   150,   # 2.5s
        S_ABSORBING: 120,   # 2s
        S_PAUSE:      90,   # 1.5s
        S_MOON_RED:  120,   # 2s
        S_FADE:       90,   # 1.5s
    }

    state       = S_CHARGING
    timer       = 0
    laser_alpha = 0
    absorb_frac = 0.0
    moon_radius = float(BASE_MOON_R)
    moon_red_t  = 0.0
    fade_alpha  = 0
    particles   = []

    ENDING_LINES = [
        ("The cannon fires.",                   font_big,   (180, 180, 180)),
        ("The moon absorbs the energy.",         font_small, (140, 140, 140)),
        ("It grows.",                            font_big,   (200,  60,  60)),
        ("The earth is the first to go.",        font_small, (160,  60,  60)),
        ("The crew never made it off the ship.", font_small, (120, 120, 120)),
        ("Neither did you.",                     font_small, (120, 120, 120)),
        ("The moon got what it wanted.",         font_big,   (160,  30,  30)),
    ]




    while True:
        clock.tick(60)
        timer += 1
        dur = DURATIONS.get(state, 99999)
        t   = min(1.0, timer / max(1, dur))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and state == S_TEXT:
                return

        # --
        # Cinematic 'animation' step-by-step
        # --
        if state == S_CHARGING:
            target_view_top = CANNON_WY - HEIGHT / 2
            if timer % 2 == 0:
                particles.append(ChargeParticle(CANNON_WX, BARREL_TIP_WY))
            if timer >= dur:
                state, timer = S_FIRING, 0
                particles.clear()

        elif state == S_FIRING:
            target_view_top = CANNON_WY - HEIGHT / 2
            laser_alpha     = min(255, laser_alpha + 14)
            if timer >= dur:
                state, timer = S_PANNING, 0

        elif state == S_PANNING:
            target_view_top = MOON_WY - HEIGHT / 4
            if timer >= dur:
                state, timer = S_ABSORBING, 0

        elif state == S_ABSORBING:
            absorb_frac = t
            laser_alpha = int(255 * (1.0 - t))
            moon_radius = BASE_MOON_R + (HEIGHT * 0.28 - BASE_MOON_R) * t
            if timer >= dur:
                state, timer = S_PAUSE, 0

        elif state == S_PAUSE:
            moon_radius = HEIGHT * 0.28
            if timer >= dur:
                state, timer = S_MOON_RED, 0

        elif state == S_MOON_RED:
            moon_red_t  = t
            moon_radius = HEIGHT * 0.28 + HEIGHT * 0.10 * t
            if timer >= dur:
                state, timer = S_FADE, 0

        elif state == S_FADE:
            fade_alpha = int(255 * t)
            if timer >= dur:
                state, timer = S_TEXT, 0

        # --
        # Smooth camera control
        # --
        view_top += (target_view_top - view_top) * 0.04


        screen.fill((3, 3, 12))

        # stars
        for s_wx, s_wy in STARS:
            s_sy = int(s_wy - view_top)
            if 0 <= s_sy < HEIGHT:
                pygame.draw.circle(screen, (190, 195, 210), (s_wx, s_sy), 1)

        # ship hull (drawn first so cannon renders on top)
        draw_ship()

        # cannon
        csx, csy = to_screen(CANNON_WX, CANNON_WY)
        if -cannon_h < csy < HEIGHT + cannon_h:
            if cannon_img:
                screen.blit(cannon_img,
                            (csx - cannon_img.get_width() // 2,
                             csy - cannon_img.get_height() // 2))
            else:
                pygame.draw.rect(screen, (80, 80, 100),
                                 (csx - 50, csy - 25, 100, 50))
            if state == S_FIRING:
                gw   = cannon_w + 30
                gh   = cannon_h + 30
                glow = pygame.Surface((gw, gh), pygame.SRCALPHA)
                pygame.draw.ellipse(glow, (100, 180, 255, 60), glow.get_rect())
                screen.blit(glow, (csx - gw // 2, csy - gh // 2))

        # charge particles
        for p in particles[:]:
            p.update()
            if p.is_dead():
                particles.remove(p)
            else:
                p.draw(screen, view_top, WIDTH, HEIGHT)

        # laser
        if state in (S_FIRING, S_PANNING, S_ABSORBING):
            draw_laser(laser_alpha, absorb_frac)

        # moon
        if state >= S_PANNING:
            draw_moon(moon_radius, moon_red_t)

        # black fade overlay
        if fade_alpha > 0:
            ov = pygame.Surface((WIDTH, HEIGHT))
            ov.fill((0, 0, 0))
            ov.set_alpha(fade_alpha)
            screen.blit(ov, (0, 0))

        # ending text
        if state == S_TEXT:
            screen.fill((0, 0, 0))
            total_h = len(ENDING_LINES) * 60
            y       = HEIGHT // 2 - total_h // 2
            for i, (text, f, col) in enumerate(ENDING_LINES):
                reveal = min(1.0, max(0.0, (timer - i * 45) / 45.0))
                if reveal > 0:
                    surf = f.render(text, True, col)
                    surf.set_alpha(int(255 * reveal))
                    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))
                y += 60
            if timer > 300:
                hint = font_small.render("press any key", True, (50, 50, 50))
                screen.blit(hint,
                            (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 50))

        pygame.display.flip()
