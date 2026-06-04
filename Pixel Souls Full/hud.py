import pygame
import math
from enums import State
from settings import WIDTH, HEIGHT


# ── Soul orb pulsing colours ──────────────────────────────────────────────────
ORB_COL_INNER = (255, 255, 255)
ORB_COL_OUTER = (255,  255,  255)
ORB_COL_LOST  = (80,  80,   80)   # greyed orb when player died with souls


class HUD:
    def __init__(self):
        self.font_large  = pygame.font.SysFont("Georgia", 18, bold=True)
        self.font_small  = pygame.font.SysFont("Georgia", 14)
        self.font_souls  = pygame.font.SysFont("Georgia", 20, bold=True)
        self.font_gain   = pygame.font.SysFont("Georgia", 15, bold=True)
        self.died_font   = pygame.font.SysFont("Georgia", 90, bold=True)
        self.sub_font    = pygame.font.SysFont("Georgia", 30)
        self._pulse      = 0.0   # drives the orb glow animation

    def update(self, dt):
        self._pulse += dt * 2.5

    def draw(self, surface, player):
        self.update(0)   # called from main each frame via hud.draw; pulse via draw_souls

        # ── HP bar ────────────────────────────────────────────────────────────
        bar_x, bar_y = 40, HEIGHT - 80
        bar_w, bar_h = 280, 14

        pygame.draw.rect(surface, (10, 10, 10), (bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4))
        pygame.draw.rect(surface, (60, 10, 10), (bar_x, bar_y, bar_w, bar_h))
        hp_fill = int(bar_w * max(player.hp, 0) / player.MAX_HP)
        if hp_fill > 0:
            pygame.draw.rect(surface, (180, 20, 20), (bar_x, bar_y, hp_fill, bar_h))
        pygame.draw.rect(surface, (230, 60, 60), (bar_x, bar_y, hp_fill, 3))
        pygame.draw.rect(surface, (80, 80, 80), (bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4), 1)

        hp_text = self.font_large.render(
            f"HP  {max(player.hp,0)} / {player.MAX_HP}", True, (255, 255, 255))
        surface.blit(hp_text, (bar_x, bar_y - 22))

        # ── Stamina bar ───────────────────────────────────────────────────────
        stam_y = bar_y + bar_h + 6
        pygame.draw.rect(surface, (10, 10, 10), (bar_x - 2, stam_y - 2, bar_w + 4, 10 + 4))
        pygame.draw.rect(surface, (20, 50, 20), (bar_x, stam_y, bar_w, 10))
        stam_fill = int(bar_w * max(player.stamina, 0) / player.MAX_STAMINA)
        if stam_fill > 0:
            pygame.draw.rect(surface, (60, 160, 60), (bar_x, stam_y, stam_fill, 10))
            pygame.draw.rect(surface, (120, 220, 120), (bar_x, stam_y, stam_fill, 2))
        pygame.draw.rect(surface, (80, 80, 80), (bar_x - 2, stam_y - 2, bar_w + 4, 10 + 4), 1)

        # ── Flasks ────────────────────────────────────────────────────────────
        flask_x, flask_y = bar_x, stam_y + 20
        flask_text = self.font_small.render(
            f"Elixir  {'●' * player.flasks}{'○' * (player.MAX_FLASKS - player.flasks)}",
            True, (200, 175, 100))
        surface.blit(flask_text, (flask_x, flask_y))

        if player.state in (State.BLOCK, State.DEFEND):
            block_surf = self.font_large.render("BLOCKING", True, (180, 200, 255))
            surface.blit(block_surf, (bar_x, flask_y + 22))

        # ── Souls counter (bottom-right, near HP bar) ─────────────────────────
        self._draw_souls(surface, player)

        # ── YOU DIED overlay ──────────────────────────────────────────────────
        if player.is_dead:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))

            died_surf = self.died_font.render("YOU DIED", True, (160, 20, 20))
            sub_surf  = self.sub_font.render(
                "Press  R  to  rest  at  bonfire", True, (160, 140, 100))

            dx = WIDTH  // 2 - died_surf.get_width()  // 2
            dy = HEIGHT // 2 - died_surf.get_height() // 2 - 30
            surface.blit(died_surf, (dx, dy))
            if player.death_finished:
                surface.blit(sub_surf,
                             (WIDTH // 2 - sub_surf.get_width() // 2, dy + 110))

    # ── Souls counter widget ──────────────────────────────────────────────────
    def _draw_souls(self, surface, player):
        sm = player.souls_mgr
        self._pulse += 0.04

        # Position: bottom-left, just below the stamina bar area
        bar_x  = 40
        bar_y  = HEIGHT - 80
        orb_cx = bar_x + 12
        orb_cy = bar_y - 52
        orb_r  = 9

        # Pulsing glow
        pulse   = 0.5 + 0.5 * math.sin(self._pulse)
        glow_r  = int(orb_r * (1.2 + 0.25 * pulse))

        # Draw glow circle
        glow_surf = pygame.Surface((glow_r * 4, glow_r * 4), pygame.SRCALPHA)
        glow_alpha = int(60 + 40 * pulse)
        pygame.draw.circle(glow_surf, (*ORB_COL_OUTER, glow_alpha),
                           (glow_r * 2, glow_r * 2), glow_r * 2)
        surface.blit(glow_surf, (orb_cx - glow_r * 2, orb_cy - glow_r * 2))

        # Draw the orb
        pygame.draw.circle(surface, ORB_COL_OUTER, (orb_cx, orb_cy), orb_r)
        pygame.draw.circle(surface, ORB_COL_INNER, (orb_cx, orb_cy), orb_r - 3)
        # Tiny specular highlight
        pygame.draw.circle(surface, (200, 255, 210),
                           (orb_cx - 3, orb_cy - 3), 2)

        # Souls number
        souls_text = self.font_souls.render(f"{sm.souls:,}", True, (255, 255, 255))
        surface.blit(souls_text, (orb_cx + orb_r + 6, orb_cy - souls_text.get_height() // 2))

        # Tiny "SOULS" label
        label = self.font_small.render("SOULS", True, (255, 255, 255))
        surface.blit(label, (orb_cx + orb_r + 6,
                              orb_cy + souls_text.get_height() // 2 - 2))

        # ── +N souls gain notification ────────────────────────────────────────
        if sm.gain_notif_timer > 0 and sm.gain_notif > 0:
            alpha   = int(255 * min(sm.gain_notif_timer / 0.5, 1.0))
            rise    = int((1.6 - sm.gain_notif_timer) * 18)
            notif   = self.font_gain.render(f"+{sm.gain_notif:,}", True, (255, 255, 255))
            notif_x = orb_cx + orb_r + 6 + souls_text.get_width() + 8
            notif_y = orb_cy - notif.get_height() // 2 - rise
            notif_s = notif.copy()
            notif_s.set_alpha(alpha)
            surface.blit(notif_s, (notif_x, notif_y))

        # ── Dropped-soul recovery hint ────────────────────────────────────────
        if sm.has_dropped_souls:
            hint = self.font_small.render(
                f"  ◉ Retrieve  {sm.dropped_amount:,}  souls", True, (255, 255, 255))
            surface.blit(hint, (orb_cx - 4,
                                orb_cy + souls_text.get_height() // 2 + 14))

        # ── Level-up hint (at bonfire) ────────────────────────────────────────
        # Drawn by main.py via draw_bonfire_prompt — nothing to do here

    # ── Soul orb in world (draw at drop location) ─────────────────────────────
    def draw_soul_orb(self, surface, camera, player):
        """Renders the floating orb on the ground where the player died."""
        sm = player.souls_mgr
        if not sm.has_dropped_souls:
            return
        if player._soul_drop_x is None:
            return

        sx, sy = camera.apply_xy(player._soul_drop_x, player._soul_drop_y)

        # Floating bob
        bob = int(4 * math.sin(self._pulse * 1.5))
        cy  = sy + bob
        r   = 12

        # Glow
        glow = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
        pulse = 0.5 + 0.5 * math.sin(self._pulse)
        pygame.draw.circle(glow, (255, 255, 255, int(40 + 30 * pulse)),
                           (r * 3, r * 3), r * 3)
        surface.blit(glow, (sx - r * 3, cy - r * 3))

        pygame.draw.circle(surface, ORB_COL_OUTER, (sx, cy), r)
        pygame.draw.circle(surface, ORB_COL_INNER, (sx, cy), r - 4)
        pygame.draw.circle(surface, (200, 255, 210), (sx - 4, cy - 4), 3)

        # Amount label above orb
        lbl = self.font_small.render(f"{sm.dropped_amount:,}", True, (160, 240, 180))
        surface.blit(lbl, (sx - lbl.get_width() // 2, cy - r - 16))

# ─────────────────────────────────────────────────────────────────────────────
# AREA POPUP  —  Dark Souls-style area name banner
# ─────────────────────────────────────────────────────────────────────────────
class AreaPopup:
    """
    Displays an area name centred on screen, Dark Souls style.
    Call  show(name, subtitle="")  to trigger it.
    Timeline:  fade-in → hold → fade-out
    """
    FADE_IN  = 1.2
    HOLD     = 2.6
    FADE_OUT = 1.2
    LINE_COL = (255, 255, 255)   # warm-gold separator lines

    def __init__(self):
        self._font_name = pygame.font.SysFont("Georgia", 48, bold=True)
        self._font_sub  = pygame.font.SysFont("Georgia", 20)
        self._timer = 9999.0
        self._total = self.FADE_IN + self.HOLD + self.FADE_OUT
        self._name  = ""
        self._sub   = ""

    def show(self, area_name, subtitle=""):
        self._name  = area_name
        self._sub   = subtitle
        self._timer = 0.0
        try:
            import sfx as _sfx
            _sfx.play("area_discover", volume=0.8)
        except Exception:
            pass

    @property
    def active(self):
        return self._timer < self._total

    def update(self, dt):
        if self._timer < self._total:
            self._timer += dt

    def draw(self, surface):
        if not self.active:
            return

        t = self._timer
        if t < self.FADE_IN:
            alpha = int(255 * (t / self.FADE_IN))
        elif t < self.FADE_IN + self.HOLD:
            alpha = 255
        else:
            alpha = int(255 * max(0.0, 1.0 - (t - self.FADE_IN - self.HOLD) / self.FADE_OUT))

        if alpha <= 0:
            return

        cx = WIDTH  // 2
        cy = 250                  # near the top of the screen

        name_surf = self._font_name.render(self._name, True, (255, 255, 255))
        name_surf.set_alpha(alpha)
        nw = name_surf.get_width()
        nh = name_surf.get_height()

        # Separator lines — slightly wider than the text
        line_w = max(nw + 90, 360)
        line_surf = pygame.Surface((line_w, 2), pygame.SRCALPHA)
        line_surf.fill((*self.LINE_COL, alpha))

        y_top  = cy - nh // 2 - 14
        y_bot  = cy + nh // 2 + 14

        surface.blit(line_surf,  (cx - line_w // 2, y_top))
        surface.blit(name_surf,  (cx - nw  // 2,    cy - nh // 2))
        surface.blit(line_surf,  (cx - line_w // 2, y_bot))

        if self._sub:
            sub_surf = self._font_sub.render(self._sub, True, (170, 155, 110))
            sub_surf.set_alpha(alpha)
            surface.blit(sub_surf, (cx - sub_surf.get_width() // 2, y_bot + 10))


# ─────────────────────────────────────────────────────────────────────────────
# VICTORY POPUP  —  shown once after boss death animation finishes
# ─────────────────────────────────────────────────────────────────────────────
class VictoryPopup:
    """
    Shows "VICTORY ACHIEVED" in gold once the boss death effect completes.
    Call  trigger()  exactly once.  Call  reset()  when restarting the run.
    """
    DELAY    = 0.6     # brief silence before text appears
    FADE_IN  = 1.5
    HOLD     = 4.8
    FADE_OUT = 1.7
    GOLD     = (210, 180, 70)
    GOLD_DIM = (170, 145, 55)

    def __init__(self):
        self._font     = pygame.font.SysFont("Georgia", 54, bold=True)
        self._font_sub = pygame.font.SysFont("Georgia", 22)
        self._timer    = 9999.0
        self._total    = self.DELAY + self.FADE_IN + self.HOLD + self.FADE_OUT
        self._fired    = False

    def trigger(self):
        """Call once when the boss death animation finishes."""
        if not self._fired:
            self._fired = True
            self._timer = 0.0
            try:
                import sfx as _sfx
                _sfx.play("boss_defeated", volume=0.9)
            except Exception:
                pass

    @property
    def active(self):
        return self._timer < self._total

    def reset(self):
        self._fired = False
        self._timer = 9999.0

    def update(self, dt):
        if self._timer < self._total:
            self._timer += dt

    def draw(self, surface):
        if not self.active:
            return

        t = self._timer
        if t < self.DELAY:
            return

        t2 = t - self.DELAY
        if t2 < self.FADE_IN:
            alpha = int(255 * (t2 / self.FADE_IN))
        elif t2 < self.FADE_IN + self.HOLD:
            alpha = 255
        else:
            alpha = int(255 * max(0.0, 1.0 - (t2 - self.FADE_IN - self.HOLD) / self.FADE_OUT))

        if alpha <= 0:
            return

        cx = WIDTH  // 2
        cy = HEIGHT // 2 - 28

        title = self._font.render("VICTORY ACHIEVED", True, self.GOLD)
        title.set_alpha(alpha)
        tw = title.get_width()
        th = title.get_height()

        # Thin gold lines flanking the text
        line_w = tw + 50
        line_surf = pygame.Surface((line_w, 1), pygame.SRCALPHA)
        line_surf.fill((*self.GOLD_DIM, alpha))

        surface.blit(line_surf, (cx - line_w // 2, cy - th // 2 - 12))
        surface.blit(title,     (cx - tw  // 2,    cy - th // 2))
        surface.blit(line_surf, (cx - line_w // 2, cy + th // 2 + 12))