# souls.py — Dark Souls-style leveling system for Pixel Souls
# Stats: Vitality (HP), Endurance (Stamina), Strength (Attack)
# Souls are dropped on death and can be recollected once.

# ── Soul cost formula (matches Dark Souls scaling) ───────────────────────────
def soul_cost(current_level):
    """Returns the souls needed to go from current_level to current_level+1."""
    # Roughly mirrors DS1: cheap early, steep late
    return int(100 + (current_level ** 1.7) * 12)


# ── Stat growth per level ─────────────────────────────────────────────────────
HP_PER_VITALITY       = 20     # +20 max HP per Vitality level
STAMINA_PER_ENDURANCE = 15     # +15 max Stamina per Endurance level
DAMAGE_PER_STRENGTH   = 5      # +5 attack damage per Strength level

BASE_HP      = 100
BASE_STAMINA = 100
BASE_DAMAGE  = 10   # base light attack damage (before Strength)


class SoulManager:
    """Tracks souls, levels, and stats. Lives on the Player."""

    def __init__(self):
        # Souls
        self.souls          = 0
        self.total_souls    = 0   # lifetime counter for HUD glow effect
        self._dropped_souls = 0   # souls left at death location
        self._souls_dropped = False

        # Level & stats (each stat starts at level 1)
        self.player_level  = 1
        self.vitality      = 1    # governs HP
        self.endurance     = 1    # governs Stamina
        self.strength      = 1    # governs attack damage

        # Floating "+N souls" notification
        self.gain_notif       = 0      # amount to flash
        self.gain_notif_timer = 0.0

    # ── Properties derived from stats ────────────────────────────────────────
    @property
    def max_hp(self):
        return BASE_HP + (self.vitality - 1) * HP_PER_VITALITY

    @property
    def max_stamina(self):
        return BASE_STAMINA + (self.endurance - 1) * STAMINA_PER_ENDURANCE

    @property
    def bonus_damage(self):
        return (self.strength - 1) * DAMAGE_PER_STRENGTH

    # ── Soul cost for NEXT upgrade of a given stat ────────────────────────────
    def cost_for(self, stat_name):
        level = getattr(self, stat_name)
        return soul_cost(self.player_level + level - 1)

    # ── Gain souls (enemy killed) ─────────────────────────────────────────────
    def add_souls(self, amount):
        self.souls       += amount
        self.total_souls += amount
        self.gain_notif       = amount
        self.gain_notif_timer = 1.6   # seconds to show the popup

    # ── Spend souls to upgrade a stat ────────────────────────────────────────
    def try_upgrade(self, stat_name):
        """Returns True if the upgrade succeeded."""
        cost = self.cost_for(stat_name)
        if self.souls < cost:
            return False
        self.souls        -= cost
        self.player_level += 1
        setattr(self, stat_name, getattr(self, stat_name) + 1)
        return True

    # ── Death / soul drop ─────────────────────────────────────────────────────
    def on_death(self):
        """Call when the player dies. Stashes the souls for retrieval."""
        self._dropped_souls = self.souls
        self._souls_dropped = self.souls > 0
        self.souls          = 0

    def try_collect_dropped(self, player_rect, drop_rect):
        """Call every frame. Returns amount collected (0 if nothing)."""
        if not self._souls_dropped or self._dropped_souls <= 0:
            return 0
        if player_rect.colliderect(drop_rect):
            amount              = self._dropped_souls
            self._dropped_souls = 0
            self._souls_dropped = False
            self.add_souls(amount)
            return amount
        return 0

    @property
    def has_dropped_souls(self):
        return self._souls_dropped and self._dropped_souls > 0

    @property
    def dropped_amount(self):
        return self._dropped_souls

    # ── Notification tick ─────────────────────────────────────────────────────
    def update(self, dt):
        if self.gain_notif_timer > 0:
            self.gain_notif_timer = max(0.0, self.gain_notif_timer - dt)