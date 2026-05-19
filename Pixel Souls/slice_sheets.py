"""
slice_sheets.py  —  run once:  python slice_sheets.py

Slices every spritesheet into individual frames and saves them as
plain RGB PNGs. No background removal happens here — pygame handles
that with set_colorkey((0,0,0)) at load time.
"""

from PIL import Image
import os

ANIM_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knight_animations")

SHEETS = {
    "Idle.png":            4,
    "Idle_2.png":          5,
    "Walk.png":            8,
    "Run.png":             7,
    "Jump.png":            6,
    "Roll.png":            6,
    "Hang.png":            6,
    "Pull_up.png":         6,
    "Climb.png":           6,
    "Attack_1.png":        5,
    "Attack_2.png":        4,
    "Attack_3.png":        4,
    "Run_Attack.png":      6,
    "Jump_Attack.png":     5,
    "Power_Attack_1.png":  5,
    "Power_Attack_2.png":  4,
    "Shield_Strike.png":   4,
    "Protect.png":         1,
    "Defend.png":          5,
    "Hurt.png":            2,
    "Dead.png":            6,
    "Elixir.png":          4,
    "Invocation.png":      5,
    "Pick_Up.png":         5,
}

FOLDER_NAMES = {
    "Idle.png":            "Idle",
    "Idle_2.png":          "Idle_2",
    "Walk.png":            "Walk",
    "Run.png":             "Run",
    "Jump.png":            "Jump",
    "Roll.png":            "Roll",
    "Hang.png":            "Hang",
    "Pull_up.png":         "Pull_up",
    "Climb.png":           "Climb",
    "Attack_1.png":        "Attack_1",
    "Attack_2.png":        "Attack_2",
    "Attack_3.png":        "Attack_3",
    "Run_Attack.png":      "Run+Attack",
    "Jump_Attack.png":     "Jump+Attack",
    "Power_Attack_1.png":  "Power_attack_1",
    "Power_Attack_2.png":  "Power_attack_2",
    "Shield_Strike.png":   "Shield_Strike",
    "Protect.png":         "Protect",
    "Defend.png":          "Defend",
    "Hurt.png":            "Hurt",
    "Dead.png":            "Dead",
    "Elixir.png":          "Elixir",
    "Invocation.png":      "Invocation",
    "Pick_Up.png":         "Pick_up",
}


def slice_sheet(sheet_path, frame_count, out_folder):
    img = Image.open(sheet_path).convert("RGB")
    w, h = img.size
    os.makedirs(out_folder, exist_ok=True)

    frame_w = w / frame_count
    for i in range(frame_count):
        x_start = int(round(i * frame_w))
        x_end   = min(int(round((i + 1) * frame_w)), w)
        frame   = img.crop((x_start, 0, x_end, h))
        frame.save(os.path.join(out_folder, f"{i}.png"))

    print(f"  ✓  {os.path.basename(sheet_path):30s} → {frame_count} frames")


if __name__ == "__main__":
    if not os.path.isdir(ANIM_DIR):
        print(f"[ERROR] Not found: {ANIM_DIR}")
        exit(1)

    print(f"Slicing: {ANIM_DIR}\n")
    missing = []
    for sheet_file, frame_count in SHEETS.items():
        sheet_path = os.path.join(ANIM_DIR, sheet_file)
        if not os.path.exists(sheet_path):
            missing.append(sheet_file)
            continue
        slice_sheet(sheet_path, frame_count, os.path.join(ANIM_DIR, FOLDER_NAMES[sheet_file]))

    if missing:
        print(f"\n[WARN] Not found, skipped:")
        for m in missing: print(f"  {m}")

    print("\n✓ Done.")
