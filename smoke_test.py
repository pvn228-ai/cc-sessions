"""Headless smoke test for the world-map platformer.

Runs without a display (SDL dummy drivers). Verifies that every area parses,
physics works, coins collect *and persist*, all four border transitions take
you to the right neighbour, map-edge borders are solid, and a full frame
renders.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from game import settings as cfg  # noqa: E402
from game import world_data  # noqa: E402
from game.area import Area  # noqa: E402
from game.world import World  # noqa: E402
from game.game import Game, MENU, EXPLORING  # noqa: E402


class _NoKeys:
    """Stand-in for pygame.key.get_pressed(): every key reads as released."""

    def __getitem__(self, _key):
        return False


NOKEYS = _NoKeys()


def test_areas_parse():
    assert world_data.START_AREA in world_data.WORLD, "start area missing from world"
    for coord, data in world_data.WORLD.items():
        area = Area(data["name"], data["rows"])
        assert len(area.tiles) > 0, f"area {coord} has no tiles"
        # Every authored floor row should be a full 24 tiles wide somewhere.
    spawns = [c for c, d in world_data.WORLD.items() if Area(d["name"], d["rows"]).spawn_tile]
    assert len(spawns) >= 1, "no area defines a player spawn 'P'... using fallback"
    print(f"[ok] {len(world_data.WORLD)} areas parse with tiles")


def test_physics_lands():
    pygame.init()
    w = World()
    for _ in range(240):
        w.handle_input(NOKEYS)
        w.update()
        if w.player.on_ground:
            break
    assert w.player.on_ground, "player never landed"
    print("[ok] gravity + collision lands the player")


def test_coin_collection_and_persistence():
    pygame.init()
    w = World()
    area = w.area
    assert len(area.coins) > 0
    coin = next(iter(area.coins))
    w.player.rect.center = coin.rect.center
    before = w.coins_collected
    w.handle_input(NOKEYS)
    w.update()
    assert w.coins_collected == before + 1, "coin not collected"
    remaining = len(w.area.coins)

    # Leave to the east and come back; the collected coin must stay gone.
    start = w.coord
    w.player.rect.right = cfg.SCREEN_WIDTH + 5
    w.update()
    assert w.coord != start, "did not transition east"
    w.player.rect.left = -5
    w.update()
    assert w.coord == start, "did not transition back west"
    assert len(w.area.coins) == remaining, "area state was not persistent"
    print("[ok] coins collect and the area persists across visits")


def test_all_four_transitions():
    pygame.init()
    home = world_data.START_AREA
    cases = {
        "west": ("rect.left", -5, (home[0] - 1, home[1])),
        "east": ("rect.right", cfg.SCREEN_WIDTH + 5, (home[0] + 1, home[1])),
        "north": ("rect.top", -5, (home[0], home[1] - 1)),
        "south": ("rect.top", cfg.SCREEN_HEIGHT + 5, (home[0], home[1] + 1)),
    }
    for name, (attr, value, expected) in cases.items():
        w = World()
        obj, field = w.player.rect, attr.split(".")[1]
        setattr(obj, field, value)
        w.update()
        assert w.coord == expected, f"{name}: expected {expected}, got {w.coord}"
    print("[ok] west/east/north/south borders lead to the correct neighbours")


def test_map_edge_is_solid():
    pygame.init()
    w = World()
    # Travel west to the grove, then try to leave the map westward.
    w.player.rect.left = -5
    w.update()
    edge = w.coord
    assert (edge[0] - 1, edge[1]) not in world_data.WORLD, "test assumes a map edge here"
    w.player.rect.left = -5
    w.update()
    assert w.coord == edge, "player escaped past a map edge"
    assert w.player.rect.left >= 0, "player not clamped at solid border"
    print("[ok] borders with no neighbour are solid walls")


def test_state_machine_and_render():
    pygame.init()
    game = Game()
    assert game.state == MENU
    game._start_game()
    assert game.state == EXPLORING
    for _ in range(30):
        game._update()
    game._draw()  # raises if any draw call is broken
    print("[ok] menu -> exploring, and a full frame renders (incl. minimap)")


if __name__ == "__main__":
    test_areas_parse()
    test_physics_lands()
    test_coin_collection_and_persistence()
    test_all_four_transitions()
    test_map_edge_is_solid()
    test_state_machine_and_render()
    print("\nAll smoke tests passed.")
