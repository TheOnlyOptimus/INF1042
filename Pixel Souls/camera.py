import pygame
from settings import WIDTH, HEIGHT


class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

    def update(self, cx, cy):
        # We lock the camera in place (0.0) so it doesn't pan around.
        # This prevents the player from sliding up into the air
        # against your static background image.
        self.x = 0.0
        self.y = 0.0

    def apply(self, rect):
        return pygame.Rect(rect.x - int(self.x), rect.y - int(self.y), rect.w, rect.h)

    def screen_to_world(self, sx, sy):
        return sx + int(self.x), sy + int(self.y)