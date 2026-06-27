"""The procedurally generated descent (Drownways, for the slice).

Each level is a small branching graph: a **hub** with an **east** and a **west**
branch. Exactly one branch holds the **stairs down**; the other is a **dead-end**
with loot — "it branches out, only one section is right." The hub has an **exit**
(climb out) so you can leave with your loot. Take the stairs and the next level is
generated fresh; reach the bottom and you escape the run a winner.

Difficulty (hazards, enemies) and reward (loot) scale with depth. Theme is always
the cave palette here. Rooms reuse the shared ``Room`` engine and east/west borders.
"""

import random

from . import settings as cfg
from .area import Room, WEST, EAST

FLOOR_ROW = cfg.AREA_ROWS - 2   # tiles row below is solid; the player stands here


def _blank_grid():
    return [[" "] * cfg.AREA_COLS for _ in range(cfg.AREA_ROWS)]


def generate_room_rows(open_sides, rng, n_haz, n_enemy, n_loot,
                       stairs=False, exit_up=False):
    """Build one cave room as a list of ASCII rows."""
    g = _blank_grid()
    w, h = cfg.AREA_COLS, cfg.AREA_ROWS

    # Bounding shell: ceiling, floor, and side walls.
    for c in range(w):
        g[0][c] = "#"
        g[h - 1][c] = "#"
    for r in range(h):
        g[r][0] = "#"
        g[r][w - 1] = "#"
    # Carve a 2-tile doorway at ground level on each connected side.
    if WEST in open_sides:
        g[FLOOR_ROW][0] = " "
        g[FLOOR_ROW - 1][0] = " "
    if EAST in open_sides:
        g[FLOOR_ROW][w - 1] = " "
        g[FLOOR_ROW - 1][w - 1] = " "

    # A floating platform or two (plunge practice + loot perches).
    for _ in range(rng.randint(1, 2)):
        pr = rng.randint(6, 10)
        pc = rng.randint(3, w - 8)
        for c in range(pc, pc + rng.randint(3, 5)):
            g[pr][c] = "#"

    # Place content on the standing row, never blocking the doorways.
    cols = list(range(3, w - 3))
    if exit_up and 11 in cols:
        cols.remove(11)        # reserve the exit column
    rng.shuffle(cols)

    def take():
        return cols.pop() if cols else rng.randint(3, w - 4)

    if exit_up:
        g[FLOOR_ROW][11] = "<"
    if stairs:
        g[FLOOR_ROW][take()] = ">"
    for _ in range(n_enemy):
        g[FLOOR_ROW][take()] = "E"
    for _ in range(n_haz):
        g[FLOOR_ROW][take()] = "^"
    for _ in range(n_loot):
        g[FLOOR_ROW][take()] = "*"

    return ["".join(row) for row in g]


class Dungeon:
    def __init__(self, player, max_depth=2, seed=None):
        self.player = player
        self.max_depth = max_depth
        self.rng = random.Random(seed)
        self.depth = 0
        self.rooms = {}
        self.current = "hub"
        # hub<->branch links: border in current room -> (target key, entry border)
        self._links = {
            "hub": {EAST: ("east", WEST), WEST: ("west", EAST)},
            "east": {WEST: ("hub", EAST)},
            "west": {EAST: ("hub", WEST)},
        }
        self.visited = set()
        self.stairs_side = None
        self._build_level()

    # ----------------------------------------------------------- generation
    def _build_level(self):
        self.depth += 1
        d = self.depth
        haz = 1 + d                       # more Searing as you go deeper
        enemies = 1 + d
        loot = 1 + d

        self.stairs_side = self.rng.choice(("east", "west"))
        dead = "west" if self.stairs_side == "east" else "east"

        self.rooms = {
            "hub": Room(generate_room_rows({WEST, EAST}, self.rng, haz, 1, 0,
                                           exit_up=True), theme="cave"),
            self.stairs_side: Room(
                generate_room_rows({WEST if self.stairs_side == "east" else EAST},
                                   self.rng, haz, enemies, max(1, loot // 2),
                                   stairs=True), theme="cave"),
            dead: Room(
                generate_room_rows({WEST if dead == "east" else EAST},
                                   self.rng, haz + 1, enemies, loot + 1), theme="cave"),
        }
        self.current = "hub"
        self.visited = {"hub"}
        self._place_center()

    def _place_center(self):
        p = self.player.rect
        p.centerx = cfg.SCREEN_WIDTH // 2
        p.bottom = FLOOR_ROW * cfg.TILE_SIZE + cfg.TILE_SIZE
        self.player.vel.update(0, 0)

    def _place_at_border(self, entry_border):
        p = self.player.rect
        m = cfg.BORDER_ENTRY_MARGIN
        p.bottom = FLOOR_ROW * cfg.TILE_SIZE + cfg.TILE_SIZE
        if entry_border == WEST:
            p.left = m
        else:  # EAST
            p.right = cfg.SCREEN_WIDTH - m
        self.player.vel.update(0, 0)

    # ----------------------------------------------------------- per frame
    @property
    def room(self):
        return self.rooms[self.current]

    @property
    def name(self):
        return f"Drownways · Depth {self.depth}"

    def update(self):
        result = self.room.update(self.player)
        border = self.room.check_border(self.player)
        if border is not None:
            links = self._links[self.current]
            if border in links:
                target, entry = links[border]
                self.current = target
                self.visited.add(target)
                self._place_at_border(entry)
            else:
                self.room.clamp_player(self.player, border)
        return result

    # ----------------------------------------------------------- interaction
    def interact(self):
        prop = self.room.nearby_prop(self.player)
        if prop is None:
            return None
        if prop.kind == "stairs":
            if self.depth >= self.max_depth:
                return ("bottom",)
            self._build_level()
            return ("descend",)
        if prop.kind == "exit":
            return ("exit",)
        return None

    def interact_prompt(self):
        prop = self.room.nearby_prop(self.player)
        return prop.prompt if prop else None

    def draw(self, surface):
        self.room.draw(surface)
        self.player.draw(surface)
