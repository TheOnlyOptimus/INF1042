import pygame
import os
from settings import BASE_PATH


def get_path(folder_name):
    return os.path.join(BASE_PATH, "knight_animations", folder_name)


def load_animation(folder_name, frame_count, scale=4):
    """Load frames named 0.png, 1.png, 2.png ... from a subfolder"""
    frames = []
    folder_path = get_path(folder_name)

    for i in range(frame_count):
        frame_path = os.path.join(folder_path, f"{i}.png")
        
        if not os.path.exists(frame_path):
            print(f"[WARN] Missing frame: {frame_path}")
            continue

        try:
            img = pygame.image.load(frame_path).convert_alpha()
            # Scale to desired size
            new_size = (int(img.get_width() * scale), int(img.get_height() * scale))
            scaled_img = pygame.transform.scale(img, new_size).convert_alpha()
            frames.append(scaled_img)
        except Exception as e:
            print(f"[ERROR] Failed loading {frame_path}: {e}")

    # Fallback if no frames loaded
    if not frames:
        print(f"[FALLBACK] Using magenta placeholders for {folder_name}")
        placeholder = pygame.Surface((128 * scale, 128 * scale), pygame.SRCALPHA)
        placeholder.fill((255, 0, 255))
        frames = [placeholder] * frame_count

    print(f"✅ Loaded {len(frames)} frames for {folder_name}")
    return frames