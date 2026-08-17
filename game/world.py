"""The Surface scene: the authored, persistent overworld.

Owns a grid of authored Rooms and a *shared* player (the Game owns the player so
it can hand the same character to the Dungeon). Handles border travel between
surface rooms and reports interactions (talking to the NPC, entering the delve).
"""

import pygame

from . import settings as cfg
from . import world_data
from .area import Room, WEST, EAST, NORTH, SOUTH

_NEIGHBOUR = {WEST: (-1, 0), EAST: (1, 0), NORTH: (0, -1), SOUTH: (0, 1)}


class World:
    def __init__(self, player):
        self.player = player
        self._cache = {}
        self.coord = world_data.START_AREA
        room = self._room(self.coord)
        spawn = room.spawn_tile or (cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 2)
        player.rect.topleft = spawn
        player.spawn = spawn

    def _room(self, coord):
        if coord not in self._cache:
            data = world_data.WORLD[coord]
            self._cache[coord] = Room(data["rows"], data["theme"], data.get("npc_lines"))
        return self._cache[coord]

    @property
    def room(self):
        return self._room(self.coord)

    @property
    def name(self):
        return world_data.WORLD[self.coord]["name"]

    # ------------------------------------------------------------- per frame
    def update(self):
        result = self.room.update(self.player)
        border = self.room.check_border(self.player)
        if border is not None:
            self._cross(border)
        return result   # {"picked": [...]}

    def _cross(self, border):
        dx, dy = _NEIGHBOUR[border]
        target = (self.coord[0] + dx, self.coord[1] + dy)
        if target not in world_data.WORLD:
            self.room.clamp_player(self.player, border)
            return
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

    def return_to_entrance(self):
        """Put the player back on the surface beside the dungeon entrance."""
        entrance_coord = next(
            (c for c, d in world_data.WORLD.items() if "D" in "".join(d["rows"])),
            self.coord,
        )
        self.coord = entrance_coord
        room = self.room
        if room.entrance is not None:
            self.player.rect.midbottom = (
                room.entrance.rect.centerx - 28,
                (cfg.AREA_ROWS - 1) * cfg.TILE_SIZE,
            )
        else:
            self.player.rect.midbottom = (cfg.SCREEN_WIDTH // 2,
                                          (cfg.AREA_ROWS - 1) * cfg.TILE_SIZE)
        self.player.vel.update(0, 0)

    # ----------------------------------------------------------- interaction
    def interact(self):
        """Player pressed the interact key. Returns an event tuple or None."""
        prop = self.room.nearby_prop(self.player)
        if prop is None:
            return None
        if prop.kind == "entrance":
            return ("enter_dungeon",)
        if prop.kind == "npc":
            return ("dialogue", prop.line)
        if prop.kind == "smith":
            return ("forge",)
        return None

    def interact_prompt(self):
        prop = self.room.nearby_prop(self.player)
        return prop.prompt if prop else None

    def draw(self, surface):
        self.room.draw(surface)
        self.player.draw(surface)
