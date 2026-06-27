"""The player character and its platforming physics.

Collision uses the standard "move on one axis, then resolve" approach so
the player never tunnels through tiles. The feel is rounded out with
coyote time, a jump buffer, and variable jump height.
"""

import pygame

from . import settings as cfg


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, cfg.TILE_SIZE - 8, cfg.TILE_SIZE - 2)
        self.spawn = (x, y)
        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False
        self.facing = 1

        self._coyote = 0          # frames since last grounded
        self._jump_buffer = 0     # frames since jump was pressed
        self._jump_held = False

    # -- input ---------------------------------------------------------------
    def handle_input(self, keys):
        self.vel.x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -cfg.PLAYER_SPEED
            self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = cfg.PLAYER_SPEED
            self.facing = 1

        jump_down = keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
        if jump_down and not self._jump_held:
            self._jump_buffer = cfg.JUMP_BUFFER_FRAMES
        # Releasing jump while rising cuts the jump short (variable height).
        if not jump_down and self.vel.y < 0:
            self.vel.y *= cfg.JUMP_CUT_MULTIPLIER
        self._jump_held = jump_down

    # -- physics -------------------------------------------------------------
    def update(self, tiles):
        # Gravity.
        self.vel.y = min(self.vel.y + cfg.GRAVITY, cfg.MAX_FALL_SPEED)

        # Consume buffered jump if we are grounded or within coyote time.
        if self._jump_buffer > 0 and (self.on_ground or self._coyote > 0):
            self.vel.y = -cfg.JUMP_SPEED
            self._jump_buffer = 0
            self._coyote = 0
            self.on_ground = False

        # Horizontal movement and resolution.
        self.rect.x += round(self.vel.x)
        self._resolve(tiles, axis="x")

        # Vertical movement and resolution.
        was_on_ground = self.on_ground
        self.on_ground = False
        self.rect.y += round(self.vel.y)
        self._resolve(tiles, axis="y")

        # Update timers.
        self._coyote = cfg.COYOTE_FRAMES if self.on_ground else max(0, self._coyote - 1)
        self._jump_buffer = max(0, self._jump_buffer - 1)
        _ = was_on_ground  # reserved for landing effects/sounds later

    def _resolve(self, tiles, axis):
        for tile in tiles:
            if not self.rect.colliderect(tile.rect):
                continue
            if axis == "x":
                if self.vel.x > 0:
                    self.rect.right = tile.rect.left
                elif self.vel.x < 0:
                    self.rect.left = tile.rect.right
            else:  # axis == "y"
                if self.vel.y > 0:
                    self.rect.bottom = tile.rect.top
                    self.on_ground = True
                    self.vel.y = 0
                elif self.vel.y < 0:
                    self.rect.top = tile.rect.bottom
                    self.vel.y = 0

    def respawn(self):
        self.rect.topleft = self.spawn
        self.vel.update(0, 0)
        self.on_ground = False

    # -- drawing -------------------------------------------------------------
    def draw(self, surface, offset):
        r = self.rect.move(offset)
        pygame.draw.rect(surface, cfg.PLAYER_COLOR, r, border_radius=8)
        # Eyes look in the facing direction.
        eye_y = r.y + r.height // 3
        ex = r.centerx + self.facing * 4
        pygame.draw.circle(surface, cfg.PLAYER_EYE_COLOR, (ex - 5, eye_y), 4)
        pygame.draw.circle(surface, cfg.PLAYER_EYE_COLOR, (ex + 5, eye_y), 4)
        pygame.draw.circle(surface, cfg.SHADOW_COLOR, (ex - 5 + self.facing, eye_y), 2)
        pygame.draw.circle(surface, cfg.SHADOW_COLOR, (ex + 5 + self.facing, eye_y), 2)
