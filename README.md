# Larkhollow — a Delver's Tale

A side-view action-platformer RPG built with pygame. You play a human teen of the
**Delvers' Guild**: raid the procedurally generated **Drownways** for Karcite,
crack the guarding crabs (the **Karcons**), and climb out with your haul — because
if you die down there, you lose what you carried.

This repo currently contains the **v1 vertical slice**: the core
descend → raid → return loop. The full design lives in [`STORYBOOK.md`](STORYBOOK.md).

## Run it

```bash
pip install -r requirements.txt
python main.py
```

## Controls

| action | keys |
|---|---|
| Move | `A` / `D` or `←` / `→` |
| Jump | `W` / `Space` / `↑` |
| Light swing | `J` |
| Shellbreaker (heavy) | `K` |
| Plunge (in air) | hold `↓` + `J` |
| Dash (i-frames) | `Shift` |
| Interact (talk / descend / climb out) | `E` |

## The combat, in one breath

Every enemy is a crab that **guards frontally** — swinging into a raised claw
**bounces**. Open them up by **flanking** (jump over / dash behind), **punishing**
the claw when it winds up to attack, **plunging** from above, or cracking the shell
with a **Shellbreaker** for a stagger window.

## What's in the slice

- Platformer movement + dash + plunge
- Swing / Shellbreaker / crack-the-shell combat vs the **Pinchling**
- Purple **Karcite Searing** hazard (the pretty thing hurts you)
- A hillside **Larkhollow** hub with an NPC and the dungeon entrance
- A procedurally generated descent: a **hub with two branches**, only one holding
  the stairs down (D2-Cloister style), loot in the dead-end
- Carry-loot, **lose it on death**, bank it by climbing out

## Tests

Headless (no window) smoke test of every system:

```bash
python smoke_test.py
```

## Layout

```
main.py             entry point
game/
  settings.py       all tunable constants
  player.py         platformer body + combat kit
  entities.py       tiles, Karcite hazard, loot, props, the Pinchling
  area.py           Room: parses a screen, draws it, resolves combat
  world.py          the authored Surface scene
  world_data.py     Larkhollow + the Old Road (ASCII)
  dungeon.py        the procedural descent generator
  game.py           window, loop, scenes, HUD, the run loop
STORYBOOK.md        the full story & design bible
```
