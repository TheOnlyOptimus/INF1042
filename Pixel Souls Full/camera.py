import pygame
from settings import WIDTH, HEIGHT, LEVEL_W, LEVEL_H


class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

    def update(self, cx, cy):
        # Smoothly follow the target centre point
        tx = cx - WIDTH  // 2
        ty = cy - HEIGHT // 2
        self.x += (tx - self.x) * 0.12
        self.y += (ty - self.y) * 0.12
        # Clamp so we never show outside the level
        self.x = max(0.0, min(self.x, LEVEL_W - WIDTH))
        self.y = max(0.0, min(self.y, LEVEL_H - HEIGHT))

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(
            rect.x - int(self.x),
            rect.y - int(self.y),
            rect.w, rect.h,
        )

    def apply_xy(self, x, y):
        return x - int(self.x), y - int(self.y)

    def screen_to_world(self, sx, sy):
        return sx + int(self.x), sy + int(self.y)
