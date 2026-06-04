# sfx.py — Sound effect loader and player
import pygame
import os
from settings import BASE_PATH

# NEW: The game will now check ALL of these folders for your audio files!
SFX_FOLDERS = [
    os.path.join(BASE_PATH, "assets", "sfx", "player"),
    os.path.join(BASE_PATH, "assets", "sfx", "boss"),
    os.path.join(BASE_PATH, "assets", "sfx", "enemies"),
    os.path.join(BASE_PATH, "assets", "sfx"),  # Fallback if you just put them in the main sfx folder
]

_cache = {}

def _load(name):
    if name in _cache:
        return _cache[name]
        
    for ext in ("ogg", "wav", "mp3"):
        for folder in SFX_FOLDERS:
            path = os.path.join(folder, f"{name}.{ext}")
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    _cache[name] = sound
                    return sound
                except Exception as e:
                    print(f"[WARN] sfx: could not load {name}: {e}")
                    return None
                    
    print(f"[INFO] sfx: no file found for '{name}' in any SFX folders")
    return None

def play(name, volume=1.0):
    sound = _load(name)
    if sound:
        sound.set_volume(volume)
        sound.play()