"""The player: a nimble human teen who runs, jumps, dashes, and swings.

Platformer physics (gravity, jump, coyote time, variable jump) carry over from
the prototype. On top sits the combat kit: a light swing, a heavy "Shellbreaker",
an aerial plunge, a dashing dodge with i-frames, plus HP and stamina.

Attacks are exposed as a transient hitbox (``attack_rect`` + ``attack_type`` +
``facing``) that the current Room resolves against enemies, so the player does
not need to know what it is hitting.
"""

import pygame

from . import settings as cfg
from .progress import Progress


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, progress=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, cfg.TILE_SIZE - 12, cfg.TILE_SIZE - 4)
        self.spawn = (x, y)
        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False
        self.facing = 1

        # Levels and gear live in Progress; a fresh one reports the base stats.
        self.progress = progress or Progress()
        self.hp = self.max_hp
        self.stamina = self.stamina_max
        self.iframes = 0
        self.dead = False

        # jump feel
        self._coyote = 0
        self._jump_buffer = 0
        self._jump_held = False

        # dash
        self._dash_timer = 0
        self._dash_cd = 0
        self._dash_dir = 1

        # attack
        self.attack_type = None        # None | "light" | "heavy" | "plunge"
        self._attack_timer = 0
        self._windup = 0
        self._hit_ids = set()
        self.attack_rect = None

    # -------------------------------------------------------- geared-up stats
    @property
    def max_hp(self):
        return self.progress.max_hp

    @property
    def stamina_max(self):
        return self.progress.stamina_max

    # ------------------------------------------------------------------ input
    def on_jump(self):
        self._jump_buffer = cfg.JUMP_BUFFER_FRAMES

    def on_attack_light(self):
        if self.attack_type is None and not self._dashing():
            self.attack_type = "light"
            self._attack_timer = cfg.SWING_FRAMES
            self._windup = 0
            self._hit_ids = set()

    def on_attack_heavy(self):
        if self.attack_type is None and not self._dashing() and self.stamina >= cfg.HEAVY_COST:
            self.stamina -= cfg.HEAVY_COST
            self.attack_type = "heavy"
            self._windup = cfg.HEAVY_WINDUP
            self._attack_timer = cfg.HEAVY_FRAMES
            self._hit_ids = set()

    def on_plunge(self):
        if not self.on_ground and self.attack_type != "plunge":
            self.attack_type = "plunge"
            self._attack_timer = 999  # ends on landing
            self._windup = 0
            self._hit_ids = set()
            self.vel.y = cfg.PLUNGE_SPEED

    def on_dash(self):
        cost = self.progress.dash_cost
        if self._dash_cd <= 0 and self.stamina >= cost and not self._dashing():
            self.stamina -= cost
            self._dash_timer = cfg.DASH_FRAMES
            self._dash_cd = cfg.DASH_FRAMES + self.progress.dash_cooldown
            self._dash_dir = self.facing
            self.iframes = max(self.iframes, cfg.DASH_IFRAMES)

    def _dashing(self):
        return self._dash_timer > 0

    def handle_input(self, keys):
        if self._dashing():
            return  # dash controls horizontal velocity
        move = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move += 1
        # No turning/strafing mid-heavy-windup — committing to the swing.
        if self._windup > 0:
            move = 0
        self.vel.x = move * cfg.PLAYER_SPEED
        if move != 0:
            self.facing = move

        jump_down = keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
        if not jump_down and self.vel.y < 0:
            self.vel.y *= cfg.JUMP_CUT_MULTIPLIER  # variable jump height
        self._jump_held = jump_down

    # ---------------------------------------------------------------- physics
    def update(self, tiles):
        if self.dead:
            return

        if self.stamina < self.stamina_max:
            self.stamina = min(self.stamina_max, self.stamina + cfg.STAMINA_REGEN)
        if self._dash_cd > 0:
            self._dash_cd -= 1
        if self.iframes > 0:
            self.iframes -= 1

        if self._dashing():
            self.vel.x = self._dash_dir * cfg.DASH_SPEED
            self.vel.y = 0
            self._dash_timer -= 1
        else:
            self.vel.y = min(self.vel.y + cfg.GRAVITY, cfg.MAX_FALL_SPEED)
            if self._jump_buffer > 0 and (self.on_ground or self._coyote > 0):
                self.vel.y = -cfg.JUMP_SPEED
                self._jump_buffer = 0
                self._coyote = 0
                self.on_ground = False

        # Horizontal, then vertical, resolving collisions per axis.
        self.rect.x += round(self.vel.x)
        self._resolve(tiles, "x")
        self.on_ground = False
        self.rect.y += round(self.vel.y)
        self._resolve(tiles, "y")

        self._coyote = cfg.COYOTE_FRAMES if self.on_ground else max(0, self._coyote - 1)
        self._jump_buffer = max(0, self._jump_buffer - 1)

        self._update_attack()

    def _resolve(self, tiles, axis):
        for tile in tiles:
            if not self.rect.colliderect(tile.rect):
                continue
            if axis == "x":
                if self.vel.x > 0:
                    self.rect.right = tile.rect.left
                elif self.vel.x < 0:
                    self.rect.left = tile.rect.right
                if self._dashing():
                    self._dash_timer = 0
            else:
                if self.vel.y > 0:
                    self.rect.bottom = tile.rect.top
                    self.on_ground = True
                    self.vel.y = 0
                    if self.attack_type == "plunge":
                        self.attack_type = None  # plunge ends on landing
                        self.attack_rect = None
                elif self.vel.y < 0:
                    self.rect.top = tile.rect.bottom
                    self.vel.y = 0

    def _update_attack(self):
        if self.attack_type is None:
            self.attack_rect = None
            return
        if self._windup > 0:
            self._windup -= 1
            self.attack_rect = None
            return
        if self.attack_type == "plunge":
            # Hitbox sits just below the feet for the whole fall.
            self.attack_rect = pygame.Rect(self.rect.x - 4, self.rect.bottom - 6,
                                           self.rect.width + 8, 18)
            return
        reach = cfg.HEAVY_REACH if self.attack_type == "heavy" else cfg.SWING_REACH
        if self.facing > 0:
            ax = self.rect.right
        else:
            ax = self.rect.left - reach
        self.attack_rect = pygame.Rect(ax, self.rect.y + 4, reach, self.rect.height - 8)
        self._attack_timer -= 1
        if self._attack_timer <= 0:
            self.attack_type = None
            self.attack_rect = None

    def already_hit(self, enemy):
        return id(enemy) in self._hit_ids

    def mark_hit(self, enemy):
        self._hit_ids.add(id(enemy))

    @property
    def attack_damage(self):
        return {"light": self.progress.swing_damage,
                "heavy": self.progress.heavy_damage,
                "plunge": self.progress.plunge_damage}.get(self.attack_type, 0)

    # ------------------------------------------------------------- being hurt
    def take_hit(self, damage, source_x):
        if self.iframes > 0 or self.dead:
            return False
        self.hp -= damage
        self.iframes = cfg.PLAYER_IFRAMES
        knock = cfg.PLAYER_KNOCKBACK if self.rect.centerx >= source_x else -cfg.PLAYER_KNOCKBACK
        self.vel.x = knock
        self.vel.y = -6
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
        return True

    def sear(self):
        """Environmental Karcite damage — bypasses knockback but respects i-frames."""
        if self.iframes > 0 or self.dead:
            return False
        self.hp -= cfg.SEARING_DAMAGE
        self.iframes = self.progress.searing_interval
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
        return True

    def revive(self, spawn=None):
        self.hp = self.max_hp
        self.stamina = self.stamina_max
        self.dead = False
        self.iframes = 0
        self.vel.update(0, 0)
        self.attack_type = None
        self.attack_rect = None
        if spawn is not None:
            self.rect.topleft = spawn

    # --------------------------------------------------------------- drawing
    def draw(self, surface, offset=(0, 0)):
        r = self.rect.move(offset)
        if self._dashing():
            color = cfg.PLAYER_DASH_COLOR
        elif self.iframes > 0 and (self.iframes // 4) % 2 == 0:
            color = cfg.PLAYER_IFRAME_COLOR
        else:
            color = cfg.PLAYER_COLOR
        pygame.draw.rect(surface, color, r, border_radius=7)

        eye_y = r.y + r.height // 3
        ex = r.centerx + self.facing * 4
        pygame.draw.circle(surface, cfg.PLAYER_EYE_COLOR, (ex - 4, eye_y), 4)
        pygame.draw.circle(surface, cfg.PLAYER_EYE_COLOR, (ex + 4, eye_y), 4)
        pygame.draw.circle(surface, cfg.SHADOW_COLOR, (ex - 4 + self.facing, eye_y), 2)
        pygame.draw.circle(surface, cfg.SHADOW_COLOR, (ex + 4 + self.facing, eye_y), 2)

        # Show the swing arc when its hitbox is live.
        if self.attack_rect is not None:
            ar = self.attack_rect.move(offset)
            width = 0 if self.attack_type == "heavy" else 3
            pygame.draw.rect(surface, cfg.SWING_COLOR, ar, width, border_radius=4)
