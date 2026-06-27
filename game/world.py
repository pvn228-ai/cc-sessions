"""The persistent world map and the rules for moving between areas.

The World lazily builds Area objects from ``world_data.WORLD`` and caches
them, so each area keeps its state (e.g. collected coins) for the whole
session. It owns the player, the current area coordinate, and the logic that
swaps areas when the player crosses a border.
"""

import pygame

from . import settings as cfg
from . import world_data
from .area import Area, WEST, EAST, NORTH, SOUTH
from .player import Player

# (col, row) deltas for each border direction.
_NEIGHBOUR = {
    WEST: (-1, 0),
    EAST: (1, 0),
    NORTH: (0, -1),
    SOUTH: (0, 1),
}


class World:
    def __init__(self):
        self._cache = {}                      # (col,row) -> Area (persistent)
        self.coord = world_data.START_AREA
        self.coins_collected = 0
        self.deaths = 0

        area = self._get_area(self.coord)
        spawn = area.spawn_tile or (cfg.SCREEN_WIDTH // 2, 0)
        self.player = Player(*spawn)
        self.player.spawn_area = self.coord    # where 'R' / death sends us back
        self.player.spawn = spawn

    # -- area cache ----------------------------------------------------------
    def _get_area(self, coord):
        if coord not in self._cache:
            data = world_data.WORLD[coord]
            self._cache[coord] = Area(data["name"], data["rows"])
        return self._cache[coord]

    @property
    def area(self):
        return self._get_area(self.coord)

    # -- input / update ------------------------------------------------------
    def handle_input(self, keys):
        self.player.handle_input(keys)

    def update(self):
        area = self.area
        self.coins_collected += area.update(self.player)

        border = area.check_border(self.player)
        if border is not None:
            self._cross_border(border)

        if area is self.area and area.player_hit_enemy(self.player):
            # Only check hazards if we did not just leave for another area.
            self._respawn()

    def _cross_border(self, border):
        dx, dy = _NEIGHBOUR[border]
        target = (self.coord[0] + dx, self.coord[1] + dy)

        if target not in world_data.WORLD:
            self.area.clamp_player(self.player, border)
            return

        # Enter the neighbouring area from the opposite side, keeping the
        # perpendicular position so movement feels continuous.
        self.coord = target
        m = cfg.BORDER_ENTRY_MARGIN
        p = self.player.rect
        if border == WEST:
            p.right = cfg.SCREEN_WIDTH - m
        elif border == EAST:
            p.left = m
        elif border == NORTH:
            p.bottom = cfg.SCREEN_HEIGHT - m
        elif border == SOUTH:
            p.top = m

    # -- respawn / restart ---------------------------------------------------
    def _respawn(self):
        self.deaths += 1
        self.coord = self.player.spawn_area
        self.player.respawn()

    def restart_area(self):
        """Rebuild the current area, restoring its coins and enemies."""
        self._cache.pop(self.coord, None)

    # -- drawing -------------------------------------------------------------
    def draw(self, surface):
        self.area.draw(surface)
        self.player.draw(surface, (0, 0))
