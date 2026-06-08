import pygame
from sprite_loader import AnimatedSprite
from systems.particles import ParticleSystem


class Crewmate:
    BASE_SPEED = 1.6
    SPEED_PER_FIX = 0.6
    SABOTAGE_RADIUS = 60
    SABOTAGE_DURATION = 120
    STUN_COOLDOWN = 180

    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.size = 48
        self.speed = self.BASE_SPEED
        self.state = "chase"

        self.sprite = AnimatedSprite(
            "assets/sprites/crewmate_bw.png",
            num_frames=4,
            frame_duration=8,
            scale=1
        )

        self._stun_cooldown = 0
        self._stun_timer = 0
        self._sabotage_timer = 0
        self._sabotage_target = None
        self._sabotage_mode = False

        self.particles = ParticleSystem()

    def update(self, player_pos, player_size, levers,
               valid_rooms=None, obstacle_rects=None):

        if self.state == "stunned":
            self.sprite.update(False)
            self._stun_timer -= 1
            if self._stun_timer <= 0:
                self.state = "chase"
            self.particles.update()
            return

        current_fixed = sum(1 for l in levers if l.fixed)
        self.speed = self.BASE_SPEED + current_fixed * self.SPEED_PER_FIX

        if self._stun_cooldown > 0:
            self._stun_cooldown -= 1

        ecx = self.pos.x + self.size // 2
        ecy = self.pos.y + self.size // 2
        pcx = player_pos.x + player_size // 2
        pcy = player_pos.y + player_size // 2

        fixed_levers = [l for l in levers if l.fixed]

        if not fixed_levers:
            self._sabotage_mode = False
            self._sabotage_target = None
            self._sabotage_timer = 0
            self.state = "chase"
            self._move_to_player(ecx, ecy, pcx, pcy,
                                 valid_rooms, obstacle_rects)
        elif self._sabotage_mode:
            self.state = "sabotage"
            self._move_to_sabotage(ecx, ecy, fixed_levers,
                                   valid_rooms, obstacle_rects)
        else:
            self.state = "chase"
            self._move_to_player(ecx, ecy, pcx, pcy,
                                 valid_rooms, obstacle_rects)

        self.sprite.update(moving=True)
        self.particles.update()

    def try_stun_player(self, player_pos, player_size,
                        has_fixed_levers=False):
        if self.state == "stunned" or self._stun_cooldown > 0:
            return False
        if self.get_rect().colliderect(
                pygame.Rect(player_pos.x, player_pos.y,
                            player_size, player_size)):
            self._stun_cooldown = self.STUN_COOLDOWN
            if has_fixed_levers:
                self._sabotage_mode = True
            return True
        return False

    def stun(self, duration=180, hit_x=None, hit_y=None):
        self.state = "stunned"
        self._stun_timer = duration
        self._sabotage_mode = False
        self._sabotage_target = None
        self._sabotage_timer = 0

        if hit_x is not None and hit_y is not None:
            self.particles.emit(
                hit_x, hit_y,
                colour=(255, 200, 50),
                count=12,
                speed=3.5,
                size=4,
                lifetime=20
            )
            self.particles.emit(
                hit_x, hit_y,
                colour=(255, 255, 255),
                count=6,
                speed=5.0,
                size=2,
                lifetime=15
            )

    def draw(self, screen):
        self.particles.draw(screen)
        self.sprite.draw(screen, int(self.pos.x), int(self.pos.y))

        try:
            font = pygame.font.SysFont("courier", 12)
        except Exception:
            font = pygame.font.SysFont(None, 12)

        if self.state == "chase":
            label = font.render("!", True, (255, 160, 0))
            screen.blit(label, (self.pos.x + 8, self.pos.y - 18))
        elif self.state == "sabotage":
            if self._sabotage_timer > 0:
                pct = 1.0 - self._sabotage_timer / self.SABOTAGE_DURATION
                bar_w = int(40 * pct)
                bar_x = int(self.pos.x + 4)
                bar_y = int(self.pos.y - 10)
                pygame.draw.rect(screen, (60, 60, 60),
                                 (bar_x, bar_y, 40, 5))
                pygame.draw.rect(screen, (255, 60, 60),
                                 (bar_x, bar_y, bar_w, 5))
            label = font.render("!!", True, (255, 60, 60))
            screen.blit(label, (self.pos.x + 4, self.pos.y - 18))
        elif self.state == "stunned":
            label = font.render("zz", True, (150, 150, 255))
            screen.blit(label, (self.pos.x + 4, self.pos.y - 18))

    def get_rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)

    def _move_to_player(self, ecx, ecy, pcx, pcy,
                        valid_rooms, obstacle_rects):
        direction = pygame.Vector2(pcx - ecx, pcy - ecy)
        if direction.length() == 0:
            return
        self._apply_move(direction.normalize(), valid_rooms, obstacle_rects)

    def _move_to_sabotage(self, ecx, ecy, fixed_levers,
                          valid_rooms, obstacle_rects):
        nearest = min(
            fixed_levers,
            key=lambda l: pygame.Vector2(ecx, ecy).distance_to(
                pygame.Vector2(l.rect.centerx, l.rect.centery))
        )

        target = pygame.Vector2(nearest.rect.centerx, nearest.rect.centery)
        direction = target - pygame.Vector2(ecx, ecy)

        if direction.length() < self.SABOTAGE_RADIUS:
            if self._sabotage_target is not nearest:
                self._sabotage_target = nearest
                self._sabotage_timer = self.SABOTAGE_DURATION
            else:
                self._sabotage_timer -= 1
                if self._sabotage_timer <= 0:
                    nearest.fixed = False
                    nearest.sabotage_effect()
                    self._sabotage_target = None
                    self._sabotage_timer = 0
                    self._sabotage_mode = False
        else:
            if self._sabotage_target is nearest:
                self._sabotage_target = None
                self._sabotage_timer  = 0
            self._apply_move(direction.normalize(), valid_rooms, obstacle_rects)

    def _apply_move(self, direction, valid_rooms, obstacle_rects):
        full = self.pos + direction * self.speed
        axial_x = pygame.Vector2(self.pos.x + direction.x * self.speed,
                                 self.pos.y)
        axial_y = pygame.Vector2(self.pos.x,
                                 self.pos.y + direction.y * self.speed)

        if (self._in_valid_area(full, valid_rooms) and
                not self._hits_obstacle(full, obstacle_rects)):
            self.pos = full
        elif (self._in_valid_area(axial_x, valid_rooms) and
                not self._hits_obstacle(axial_x, obstacle_rects)):
            self.pos = axial_x
        elif (self._in_valid_area(axial_y, valid_rooms) and
                not self._hits_obstacle(axial_y, obstacle_rects)):
            self.pos = axial_y

    def _in_valid_area(self, pos, valid_rooms):
        if valid_rooms is None:
            return True
        entity_rect = pygame.Rect(pos.x, pos.y, self.size, self.size)
        return any(room.contains(entity_rect) for room in valid_rooms)

    def _hits_obstacle(self, pos, obstacle_rects):
        if not obstacle_rects:
            return False
        entity_rect = pygame.Rect(pos.x, pos.y, self.size, self.size)
        return any(entity_rect.colliderect(r) for r in obstacle_rects)