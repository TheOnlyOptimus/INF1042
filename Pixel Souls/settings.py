import os
from enums import State

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

WIDTH, HEIGHT = 1280, 720
BG_COLOR  = (18, 18, 24)
PLAT_COL  = (60, 60, 70)

SPRITE_SCALE = 4
PLAYER_WIDTH  = 128 * SPRITE_SCALE
PLAYER_HEIGHT = 128 * SPRITE_SCALE
GROUND_Y = 600


# New format: (folder_name, frame_count)
ANIM_MANIFEST = {
    State.IDLE:          ("Idle", 4),
    State.IDLE_2:        ("Idle_2", 5),
    State.WALK:          ("Walk", 8),
    State.RUN:           ("Run", 7),
    State.JUMP:          ("Jump", 6),
    State.ROLL:          ("Roll", 6),
    State.HANG:          ("Hang", 6),
    State.PULL_UP:       ("Pull_up", 6),
    State.CLIMB:         ("Climb", 6),

    State.ATTACK_1:      ("Attack_1", 5),
    State.ATTACK_2:      ("Attack_2", 4),
    State.ATTACK_3:      ("Attack_3", 4),

    State.RUN_ATTACK:    ("Run_Attack", 6),
    State.JUMP_ATTACK:   ("Jump_Attack", 5),

    State.POWER_ATK_1:   ("Power_attack_1", 5),
    State.POWER_ATK_2:   ("Power_attack_2", 4),

    State.SHIELD_STRIKE: ("Shield_strike", 4),

    State.BLOCK:         ("Defend", 5),
    State.DEFEND:        ("Protect", 1),

    State.HURT:          ("Hurt", 2),
    State.DEAD:          ("Dead", 6),

    State.ELIXIR:        ("Elixir", 4),
    State.INVOCATION:    ("Invocation", 5),
    State.PICK_UP:       ("Pick_up", 5),
}

ANIM_SPEEDS = {
    State.IDLE:          0.14,
    State.IDLE_2:        0.14,
    State.WALK:          0.12,
    State.RUN:           0.08,
    State.JUMP:          0.10,
    State.ROLL:          0.08,
    State.ATTACK_1:      0.07,
    State.ATTACK_2:      0.07,
    State.ATTACK_3:      0.07,
    State.RUN_ATTACK:    0.10,
    State.JUMP_ATTACK:   0.13,
    State.POWER_ATK_1:   0.08,
    State.POWER_ATK_2:   0.08,
    State.SHIELD_STRIKE: 0.10,
    State.BLOCK:         0.12,
    State.DEFEND:        0.06,
    State.HURT:          0.08,
    State.DEAD:          0.14,
    State.ELIXIR:        0.14,
    State.INVOCATION:    0.10,
    State.PICK_UP:       0.12,
}

ANIM_OFFSETS = {
    State.IDLE:         (0, 0),
    State.WALK:         (0, 0),
    State.RUN:          (0, 0),
    State.JUMP:         (0, -4),
    State.ATTACK_1:     (12, 0),
    State.RUN_ATTACK:   (18, 0),
    State.JUMP_ATTACK:  (15, -5),
    State.POWER_ATK_1:  (25, 0),
    State.POWER_ATK_2:  (25, 0),
    State.SHIELD_STRIKE:(10, 0),
}

LIGHT_COMBO =[
    (State.ATTACK_1, 5),
    (State.ATTACK_2, 4),
    (State.ATTACK_3, 4),
]

HEAVY_COMBO =[
    (State.POWER_ATK_1, 5),
    (State.POWER_ATK_2, 4),
]

COMBO_BUFFER = 0.18