"""Static and simple dynamic entities: tiles, coins, enemies, and the goal.

All entities are ``pygame.sprite.Sprite`` subclasses so they can live in
sprite groups. Drawing is handled here (each knows how to render itself),
while the camera applies a scroll offset at draw time.
"""

import math

import pygame

from . import settings as cfg


class Tile(pygame.sprite.Sprite):
    """A solid, immovable block the player and enemies collide with."""

    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, cfg.TILE_SIZE, cfg.TILE_SIZE)

    def draw(self, surface, offset):
        r = self.rect.move(offset)
        pygame.draw.rect(surface, cfg.TILE_COLOR, r)
        # A lighter strip along the top sells the "grassy ground" look.
        top = pygame.Rect(r.x, r.y, r.width, 6)
        pygame.draw.rect(surface, cfg.TILE_TOP_COLOR, top)


class Coin(pygame.sprite.Sprite):
    """A collectible that bobs gently and is removed when picked up."""

    def __init__(self, x, y):
        super().__init__()
        size = cfg.TILE_SIZE
        self.rect = pygame.Rect(x, y, size, size)
        self.radius = size // 4
        self._phase = (x + y) * 0.01  # desync the bob between coins
        self._t = 0.0

    def update(self):
        self._t += 0.1

    def draw(self, surface, offset):
        bob = math.sin(self._t + self._phase) * 4
        cx = self.rect.centerx + offset[0]
        cy = self.rect.centery + offset[1] + bob
        pygame.draw.circle(surface, cfg.COIN_COLOR, (int(cx), int(cy)), self.radius)
        pygame.draw.circle(
            surface, cfg.COIN_SHINE, (int(cx - 2), int(cy - 2)), max(2, self.radius // 3)
        )


class Enemy(pygame.sprite.Sprite):
    """A walker that patrols back and forth, turning at ledges and walls."""

    def __init__(self, x, y):
        super().__init__()
        size = cfg.TILE_SIZE
        # Slightly smaller than a tile so it sits nicely on platforms.
        self.rect = pygame.Rect(x + 4, y + 8, size - 8, size - 8)
        self.direction = 1
        self.speed = cfg.ENEMY_SPEED

    def update(self, tiles):
        # Horizontal move, then resolve against walls.
        self.rect.x += self.direction * self.speed
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.direction > 0:
                    self.rect.right = tile.rect.left
                else:
                    self.rect.left = tile.rect.right
                self.direction *= -1
                return

        # Turn around at ledges so the enemy stays on its platform.
        ahead_x = self.rect.right + 1 if self.direction > 0 else self.rect.left - 1
        probe = pygame.Rect(ahead_x, self.rect.bottom + 1, 1, 2)
        if not any(probe.colliderect(t.rect) for t in tiles):
            self.direction *= -1

    def draw(self, surface, offset):
        r = self.rect.move(offset)
        pygame.draw.rect(surface, cfg.ENEMY_COLOR, r, border_radius=6)
        # Two little eyes facing the travel direction.
        eye_y = r.y + r.height // 3
        ex = r.centerx + self.direction * 5
        pygame.draw.circle(surface, cfg.PLAYER_EYE_COLOR, (ex - 4, eye_y), 3)
        pygame.draw.circle(surface, cfg.PLAYER_EYE_COLOR, (ex + 4, eye_y), 3)
