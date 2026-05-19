import pygame
from enums import State
from settings import WIDTH, HEIGHT

class HUD:
    def __init__(self):
        self.font_large = pygame.font.SysFont("Georgia", 18, bold=True)
        self.font_small = pygame.font.SysFont("Georgia", 14)
        self.died_font  = pygame.font.SysFont("Georgia", 90, bold=True)
        self.sub_font   = pygame.font.SysFont("Georgia", 30)

    def draw(self, surface, player):
        bar_x, bar_y = 40, HEIGHT - 80
        bar_w, bar_h = 280, 14

        pygame.draw.rect(surface, (10, 10, 10), (bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4))
        pygame.draw.rect(surface, (60, 10, 10), (bar_x, bar_y, bar_w, bar_h))
        hp_fill = int(bar_w * max(player.hp, 0) / player.MAX_HP)
        if hp_fill > 0:
            pygame.draw.rect(surface, (180, 20, 20), (bar_x, bar_y, hp_fill, bar_h))
        pygame.draw.rect(surface, (230, 60, 60), (bar_x, bar_y, hp_fill, 3))
        pygame.draw.rect(surface, (80, 80, 80), (bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4), 1)

        hp_text = self.font_large.render(f"HP  {max(player.hp,0)} / {player.MAX_HP}", True, (200, 200, 200))
        surface.blit(hp_text, (bar_x, bar_y - 22))

        stam_y = bar_y + bar_h + 6
        pygame.draw.rect(surface, (10, 10, 10), (bar_x - 2, stam_y - 2, bar_w + 4, 10 + 4))
        pygame.draw.rect(surface, (20, 50, 20), (bar_x, stam_y, bar_w, 10))
        stam_fill = int(bar_w * max(player.stamina, 0) / player.MAX_STAMINA)
        if stam_fill > 0:
            pygame.draw.rect(surface, (60, 160, 60), (bar_x, stam_y, stam_fill, 10))
            pygame.draw.rect(surface, (120, 220, 120), (bar_x, stam_y, stam_fill, 2))
        pygame.draw.rect(surface, (80, 80, 80), (bar_x - 2, stam_y - 2, bar_w + 4, 10 + 4), 1)

        flask_x, flask_y = bar_x, stam_y + 20
        flask_text = self.font_small.render(f"Elixir  {'●' * player.flasks}{'○' * (player.MAX_FLASKS - player.flasks)}", True, (200, 175, 100))
        surface.blit(flask_text, (flask_x, flask_y))

        if player.state in (State.BLOCK, State.DEFEND):
            block_surf = self.font_large.render("BLOCKING", True, (180, 200, 255))
            surface.blit(block_surf, (bar_x, flask_y + 22))

        if player.is_dead:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))

            died_surf  = self.died_font.render("YOU DIED", True, (160, 20, 20))
            sub_surf   = self.sub_font.render("Press  R  to  rest  at  bonfire", True, (160, 140, 100))

            dx = WIDTH  // 2 - died_surf.get_width()  // 2
            dy = HEIGHT // 2 - died_surf.get_height() // 2 - 30
            surface.blit(died_surf, (dx, dy))
            if player.death_finished:
                surface.blit(sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, dy + 110))