# level_up.py — Dark Souls-style level-up menu overlay for Pixel Souls
#
# Open  : press  L  at a bonfire while State.RESTING
# Close : press  Escape  or  L  again (or when no souls / no upgrades possible)
#
# Layout (centre-screen panel):
#   ┌─────────────────────────────────────┐
#   │          LEVEL UP                   │
#   │  Level  7          Souls  1 240     │
#   ├─────────────────────────────────────┤
#   │  ►  Vitality     Lv 3   Cost  480   │
#   │     Endurance    Lv 1   Cost  200   │
#   │     Strength     Lv 2   Cost  340   │
#   ├─────────────────────────────────────┤
#   │  [J] Confirm    [Esc/L] Close       │
#   └─────────────────────────────────────┘

import pygame
from settings import WIDTH, HEIGHT

PANEL_W = 520
PANEL_H = 320
PANEL_X = WIDTH  // 2 - PANEL_W // 2
PANEL_Y = HEIGHT // 2 - PANEL_H // 2

# Colours
C_BG        = (10,  10,  14,  230)   # near-black panel background (alpha)
C_BORDER    = (120, 90,  40)          # dark gold border
C_TITLE     = (210, 175, 80)          # gold title
C_SOULS     = (180, 220, 100)         # green-gold souls count
C_STAT      = (200, 200, 200)         # normal stat row
C_SELECTED  = (255, 220, 80)          # highlighted row
C_COST      = (160, 140, 100)         # cost text
C_CANT      = (100, 80,  60)          # greyed-out (can't afford)
C_FOOTER    = (130, 120, 110)         # footer hint text
C_LEVEL     = (170, 170, 210)         # level number tint

STATS = [
    ("vitality",  "Vitality",  "HP"),
    ("endurance", "Endurance", "Stamina"),
    ("strength",  "Strength",  "Attack"),
]


class LevelUpMenu:
    def __init__(self):
        self.open      = False
        self._cursor   = 0             # 0-2 selected row
        self._confirm_flash = 0.0     # brief green flash on upgrade

        self.font_title  = pygame.font.SysFont("Georgia", 22, bold=True)
        self.font_stat   = pygame.font.SysFont("Georgia", 18)
        self.font_small  = pygame.font.SysFont("Georgia", 14)
        self.font_souls  = pygame.font.SysFont("Georgia", 16, bold=True)

    # ── Toggle ────────────────────────────────────────────────────────────────
    def toggle(self):
        self.open    = not self.open
        self._cursor = 0

    def close(self):
        self.open = False

    # ── Input ─────────────────────────────────────────────────────────────────
    def handle_event(self, event, souls_mgr, player):
        """Returns True if the event was consumed."""
        if not self.open:
            return False

        if event.type != pygame.KEYDOWN:
            return True   # eat all events while open

        if event.key in (pygame.K_ESCAPE, pygame.K_l):
            self.close()
            return True

        if event.key in (pygame.K_w, pygame.K_UP):
            self._cursor = (self._cursor - 1) % len(STATS)
            return True

        if event.key in (pygame.K_s, pygame.K_DOWN):
            self._cursor = (self._cursor + 1) % len(STATS)
            return True

        if event.key in (pygame.K_j, pygame.K_RETURN):
            stat_key = STATS[self._cursor][0]
            if souls_mgr.try_upgrade(stat_key):
                self._confirm_flash = 0.35
                # Apply stat changes immediately to the live player
                _apply_stats(souls_mgr, player)
            return True

        return True   # consume everything else too

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, dt):
        if self._confirm_flash > 0:
            self._confirm_flash = max(0.0, self._confirm_flash - dt)

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surface, souls_mgr):
        if not self.open:
            return

        # Semi-transparent backdrop
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        # Panel background
        panel = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
        panel.fill(C_BG)
        surface.blit(panel, (PANEL_X, PANEL_Y))

        # Border
        pygame.draw.rect(surface, C_BORDER,
                         (PANEL_X, PANEL_Y, PANEL_W, PANEL_H), 2)
        # Inner border inset
        pygame.draw.rect(surface, (80, 60, 20),
                         (PANEL_X + 4, PANEL_Y + 4, PANEL_W - 8, PANEL_H - 8), 1)

        x0 = PANEL_X + 28
        y  = PANEL_Y + 22

        # ── Title row ─────────────────────────────────────────────────────────
        title_surf = self.font_title.render("LEVEL  UP", True, C_TITLE)
        surface.blit(title_surf, (x0, y))

        lvl_surf = self.font_small.render(
            f"Player Level  {souls_mgr.player_level}", True, C_LEVEL)
        surface.blit(lvl_surf, (PANEL_X + PANEL_W - lvl_surf.get_width() - 28, y + 4))

        y += 38
        # Divider
        pygame.draw.line(surface, C_BORDER,
                         (PANEL_X + 12, y), (PANEL_X + PANEL_W - 12, y), 1)
        y += 12

        # ── Souls available ───────────────────────────────────────────────────
        souls_str = f"Souls  {souls_mgr.souls:,}"
        s_surf = self.font_souls.render(souls_str, True, C_SOULS)
        surface.blit(s_surf, (x0, y))
        y += 32

        # Divider
        pygame.draw.line(surface, C_BORDER,
                         (PANEL_X + 12, y), (PANEL_X + PANEL_W - 12, y), 1)
        y += 14

        # ── Stat rows ─────────────────────────────────────────────────────────
        for i, (key, label, bonus_label) in enumerate(STATS):
            selected = (i == self._cursor)
            cost     = souls_mgr.cost_for(key)
            can_buy  = souls_mgr.souls >= cost
            stat_lv  = getattr(souls_mgr, key)

            row_col  = C_SELECTED if selected else (C_STAT if can_buy else C_CANT)

            # Cursor arrow
            if selected:
                arrow = self.font_stat.render("►", True, C_SELECTED)
                surface.blit(arrow, (x0 - 20, y))

                # Highlight bar
                highlight = pygame.Surface((PANEL_W - 24, 24), pygame.SRCALPHA)
                alpha = 60 if not self._confirm_flash else 120
                highlight.fill((200, 180, 60, alpha))
                surface.blit(highlight, (PANEL_X + 12, y - 2))

            # Stat name
            name_surf = self.font_stat.render(label, True, row_col)
            surface.blit(name_surf, (x0, y))

            # Current level
            lv_surf = self.font_stat.render(f"Lv {stat_lv}", True, row_col)
            surface.blit(lv_surf, (x0 + 170, y))

            # Cost
            cost_col  = C_SOULS if can_buy else C_CANT
            cost_surf = self.font_stat.render(f"Cost  {cost:,}", True, cost_col)
            surface.blit(cost_surf, (x0 + 270, y))

            # Tooltip: what the next level gives
            tip = _stat_tip(key)
            tip_surf = self.font_small.render(tip, True, (100, 160, 100) if can_buy else (70, 70, 70))
            surface.blit(tip_surf, (x0 + 270, y + 18))

            y += 52

        # Divider
        pygame.draw.line(surface, C_BORDER,
                         (PANEL_X + 12, y), (PANEL_X + PANEL_W - 12, y), 1)
        y += 10

        # ── Footer ────────────────────────────────────────────────────────────
        footer = self.font_small.render(
            "W/S  Navigate      J  Upgrade      Esc / L  Close", True, C_FOOTER)
        surface.blit(footer, (PANEL_X + PANEL_W // 2 - footer.get_width() // 2, y))


# ── Helpers ───────────────────────────────────────────────────────────────────
def _stat_tip(key):
    from souls import HP_PER_VITALITY, STAMINA_PER_ENDURANCE, DAMAGE_PER_STRENGTH
    if key == "vitality":
        return f"+{HP_PER_VITALITY} Max HP"
    if key == "endurance":
        return f"+{STAMINA_PER_ENDURANCE} Max Stamina"
    if key == "strength":
        return f"+{DAMAGE_PER_STRENGTH} Attack Dmg"
    return ""


def _apply_stats(souls_mgr, player):
    """Push soul-manager stats onto the live player object."""
    new_max_hp  = souls_mgr.max_hp
    new_max_sta = souls_mgr.max_stamina

    # Preserve current HP/Stamina as a ratio so you don't get a free full heal
    hp_ratio  = player.hp      / player.MAX_HP      if player.MAX_HP      > 0 else 1.0
    sta_ratio = player.stamina / player.MAX_STAMINA if player.MAX_STAMINA > 0 else 1.0

    player.MAX_HP      = new_max_hp
    player.MAX_STAMINA = new_max_sta
    player.hp          = max(1, int(new_max_hp  * hp_ratio))
    player.stamina     = max(0, new_max_sta * sta_ratio)
    player._bonus_damage = souls_mgr.bonus_damage