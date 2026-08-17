"""The authored Surface for the v1 slice: Larkhollow and the road to the delve.

Two screen-sized rooms linked east/west:
  (0,0) Larkhollow — a hillside hub with houses, one NPC, and the Sunbound Forge
        where your haul turns into gear (the safe place).
  (1,0) The Old Road — a tree, a teaser Karcite vein, a tutorial Pinchling, and
        the dungeon ENTRANCE you drop into.

Glyphs: # tile, P spawn, N npc, S smith (the Forge), E pinchling,
        ^ karcite (Searing), D entrance.
"""

START_AREA = (0, 0)

WORLD = {
    (0, 0): {
        "name": "Larkhollow",
        "theme": "surface",
        "npc_lines": [
            "Hessel: The tides are back, lad — on dry land. "
            "The signs of a Sinking. Don't go down there... but you will.",
        ],
        "rows": [
            "                        ",
            "                        ",
            "                        ",
            "                        ",
            "                        ",
            "          ##            ",
            "         ####           ",
            "        ######          ",
            "   ###      ###         ",
            "   ###      ###         ",
            "   ###      ###   ####   ",
            "   ###      ###   ####   ",
            "   ###      ###   ####   ",
            "      P        N     S   ",
            "########################",
        ],
    },
    (1, 0): {
        "name": "The Old Road",
        "theme": "surface",
        "npc_lines": [],
        "rows": [
            "                        ",
            "                        ",
            "                        ",
            "                        ",
            "                        ",
            "                        ",
            "             ####       ",
            "                        ",
            "      ####              ",
            "                        ",
            "                        ",
            "                        ",
            "                        ",
            "       E      ^      D   ",
            "########################",
        ],
    },
}
