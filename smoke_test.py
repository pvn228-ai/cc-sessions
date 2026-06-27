"""Headless smoke test for the v1 vertical slice (no display).

Covers: surface parsing, platformer physics, the Pinchling shell rules
(bounce/flank/punish/plunge/Shellbreaker), Searing damage, loot pickup,
dungeon generation (hub + two branches, exactly one with stairs), descending
to the bottom, the death/return loop, and rendering both scenes.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from game import settings as cfg  # noqa: E402
from game.area import Room  # noqa: E402
from game.entities import Pinchling  # noqa: E402
from game.player import Player  # noqa: E402
from game.world import World  # noqa: E402
from game.dungeon import Dungeon  # noqa: E402
from game.game import Game, TITLE, SURFACE, DUNGEON, DEATH  # noqa: E402


class _NoKeys:
    def __getitem__(self, _):
        return False


NOKEYS = _NoKeys()
FLOOR = "#" * cfg.AREA_COLS


def test_surface_parses():
    pygame.init()
    w = World(Player(0, 0))
    assert w.room.spawn_tile is not None, "Larkhollow has no spawn"
    assert any(p.kind == "npc" for p in w.room.props), "no NPC in Larkhollow"
    w.coord = (1, 0)
    assert w.room.entrance is not None, "no dungeon entrance on the Old Road"
    print("[ok] surface parses (spawn, NPC, entrance)")


def test_player_lands():
    pygame.init()
    p = Player(100, 0)
    room = Room(["                        "] * 14 + [FLOOR], "surface")
    for _ in range(200):
        p.handle_input(NOKEYS)
        room.update(p)
        if p.on_ground:
            break
    assert p.on_ground, "player never landed"
    print("[ok] platformer physics lands the player")


def test_pinchling_shell_rules():
    pygame.init()
    c = Pinchling(400, 400)
    c.facing = -1                       # guarding to its left
    cx = c.rect.centerx
    front = cx - 100                    # attacker on the guarded (left) side
    back = cx + 100                     # attacker behind (right) flank

    assert Pinchling(400, 400).receive(1, "light", front) is False or True  # smoke
    a = Pinchling(400, 400); a.facing = -1
    assert a.receive(1, "light", front) is False, "front light should bounce"
    b = Pinchling(400, 400); b.facing = -1
    assert b.receive(1, "light", back) is True, "flank should land"
    h = Pinchling(400, 400); h.facing = -1
    assert h.receive(1, "heavy", front) is True, "Shellbreaker should land"
    assert h.staggered(), "Shellbreaker should crack the shell (stagger)"
    pl = Pinchling(400, 400); pl.facing = -1
    assert pl.receive(1, "plunge", front) is True, "plunge ignores the guard"
    print("[ok] Pinchling shell rules: bounce / flank / Shellbreaker+stagger / plunge")


def test_searing_damages():
    pygame.init()
    rows = ["                        "] * 13 + ["     ^                  ", FLOOR]
    room = Room(rows, "cave")
    p = Player(5 * cfg.TILE_SIZE, 13 * cfg.TILE_SIZE)
    before = p.hp
    for _ in range(40):
        room.update(p)
    assert p.hp < before, "Searing did not damage the player"
    print(f"[ok] Karcite Searing damages the player ({before} -> {p.hp})")


def test_loot_pickup():
    pygame.init()
    rows = ["                        "] * 13 + ["     *                  ", FLOOR]
    room = Room(rows, "cave")
    p = Player(5 * cfg.TILE_SIZE, 13 * cfg.TILE_SIZE)
    picked = []
    for _ in range(10):
        picked += room.update(p).get("picked", [])
    assert len(picked) == 1 and picked[0].kind == "karcite", "loot not collected"
    print("[ok] loot is picked up")


def test_dungeon_generation():
    pygame.init()
    d = Dungeon(Player(0, 0), max_depth=2)
    assert set(d.rooms) == {"hub", "east", "west"}, "level is not hub+2 branches"
    with_stairs = [k for k in ("east", "west") if d.rooms[k].stairs is not None]
    assert len(with_stairs) == 1, "exactly one branch must hold the stairs"
    assert d.rooms["hub"].exit_prop is not None, "hub needs a climb-out exit"
    assert d.depth == 1
    print("[ok] dungeon generates hub + 2 branches, one stairway, an exit")


def test_descend_to_bottom():
    pygame.init()
    player = Player(0, 0)
    d = Dungeon(player, max_depth=2)
    # Level 1 -> take the stairs.
    d.current = d.stairs_side
    player.rect.center = d.room.stairs.rect.center
    assert d.interact() == ("descend",), "stairs should descend"
    assert d.depth == 2
    # Level 2 (the bottom) -> stairs should end the run.
    d.current = d.stairs_side
    player.rect.center = d.room.stairs.rect.center
    assert d.interact() == ("bottom",), "deepest stairs should reach the bottom"
    print("[ok] descending the stairs reaches the bottom across levels")


def test_game_loop_and_death():
    pygame.init()
    g = Game()
    assert g.state == TITLE
    g._new_game()
    assert g.state == SURFACE
    g._draw()

    # Force into the dungeon and collect/lose loot.
    g.dungeon = Dungeon(g.player, max_depth=2)
    g.state = DUNGEON
    g.run_loot["karcite"] = 5
    g._draw()
    g.player.hp = 0
    g.player.dead = True
    g._update()  # should flip to DEATH
    assert g.state == DEATH, "death not detected"
    g._respawn_in_town()
    assert g.state == SURFACE and g.run_loot["karcite"] == 0, "loot not lost on death"
    print("[ok] game loop: title -> surface -> dungeon -> death -> respawn (loot lost)")


def test_no_crash_over_frames():
    pygame.init()
    g = Game()
    g._new_game()
    g.dungeon = Dungeon(g.player, max_depth=3)
    g.state = DUNGEON
    for i in range(600):
        if i % 50 == 0:
            g.player.on_attack_light()
        if i % 80 == 0:
            g.player.on_attack_heavy()
        g.player.handle_input(NOKEYS)
        g.scene.update()
        g._draw()
        if g.player.dead:
            g.player.revive()
    print("[ok] 600 dungeon frames render without crashing")


if __name__ == "__main__":
    test_surface_parses()
    test_player_lands()
    test_pinchling_shell_rules()
    test_searing_damages()
    test_loot_pickup()
    test_dungeon_generation()
    test_descend_to_bottom()
    test_game_loop_and_death()
    test_no_crash_over_frames()
    print("\nAll smoke tests passed.")
