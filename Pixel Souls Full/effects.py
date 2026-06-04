"""
effects.py — Visual effects for Pixel Souls

Expected assets:
    knight_animations/hit/          0.png … 7.png   (8 frames) — per-hit blood
    knight_animations/bossdeath/    0.png … 2.png   (3 frames) — death explosion
    assets/B100.png                                  — single-frame death splat
"""

import pygame
import os
from utils import load_animation
from settings import BASE_PATH, SPRITE_SCALE

ASSETS = os.path.join(BASE_PATH, "assets")

HIT_SCALE   = 2
DEATH_SCALE = SPRITE_SCALE + 2

_cache = {}

def _get_frames(folder, count, scale):
    key = (folder, scale)
    if key not in _cache:
        try:
            _cache[key] = load_animation(folder, count, scale)
        except Exception as e:
            print(f"[WARN] effects: could not load {folder}: {e}")
            s = pygame.Surface((64 * scale, 64 * scale), pygame.SRCALPHA)
            s.fill((200, 0, 0, 180))
            _cache[key] = [s] * count
    return _cache[key]


# ─────────────────────────────────────────────────────────────────────────────
# BLOOD HIT
# ─────────────────────────────────────────────────────────────────────────────
class BloodHit:
    FRAME_SPEED = 0.1

    def __init__(self, world_x, world_y):
        self.x      = float(world_x)
        self.y      = float(world_y)
        self.frames = _get_frames("hit", 4, HIT_SCALE)
        self.idx    = 0
        self.timer  = 0.0
        self.done   = False

    def update(self, dt):
        if self.done:
            return
        self.timer += dt
        if self.timer >= self.FRAME_SPEED:
            self.timer -= self.FRAME_SPEED
            self.idx += 1
            if self.idx >= len(self.frames):
                self.done = True

    def draw(self, surface, camera):
        if self.done:
            return
        img = self.frames[min(self.idx, len(self.frames) - 1)]
        sx, sy = camera.apply_xy(int(self.x), int(self.y))
        r = img.get_rect()
        r.center = (sx, sy)
        surface.blit(img, r)


# ─────────────────────────────────────────────────────────────────────────────
# BOSS DEATH EXPLOSION
# Cinematic sequence: 
# 0.0s - 0.6s : Flash red, Boss shakes violently (NO BLOOD YET).
# 0.6s - 2.2s : Blood abruptly erupts, boss continues fading out.
# 2.2s - 3.5s : Boss is fully gone. Blood lingers and slowly fades away.
# ─────────────────────────────────────────────────────────────────────────────
class BossDeathExplosion:
    DURATION         = 3.5   # Increased total duration
    SHAKE_DURATION   = 2.2   # Increased shake duration
    BLOOD_DELAY      = 0.6   # Wait 0.6 seconds before blood explodes!
    
    SPLAT_MAX_SCALE  = 5.0
    FLASH_ALPHA      = 160
    FLASH_DURATION   = 0.15

    def __init__(self, boss):
        import random
        self._rng = random.Random()
        
        # Save exact boss parameters for perfect rendering alignment
        self.boss_x = float(boss.x)
        self.boss_y = float(boss.y)
        self.center_x = boss.rect.centerx
        self.center_y = boss.rect.centery
        self.foot_offset = boss.FOOT_OFFSET
        self.facing_right = boss.facing_right
        self.idle_frames = boss.animations.get("idle", [])

        self.timer        = 0.0
        self.done         = False

        # Boss visual stats
        self.boss_alpha   = 255
        self.shake_x      = 0
        self.shake_y      = 0
        self._idle_idx    = 0
        self._idle_timer  = 0.0
        self._IDLE_SPEED  = 0.14
        
        # Flash stats
        self.flash_alpha  = self.FLASH_ALPHA

        # Blood & Splat stats
        self.splat_alpha  = 0
        self.splat_scale  = 0.2
        self.exp_alpha    = 0
        self.exp_idx      = 0
        self.exp_frames   = _get_frames("bossdeath", 3, DEATH_SCALE)

        # Load the splat image
        splat_path = os.path.join(ASSETS, "B100.png")
        try:
            self._splat_raw = pygame.image.load(splat_path).convert_alpha()
        except:
            self._splat_raw = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(self._splat_raw, (150, 0, 0, 150), (50, 50), 40)

    def update(self, dt):
        if self.done:
            return

        self.timer += dt
        if self.timer >= self.DURATION:
            self.done = True
            return

        # ── 1. Flash (Fades out quickly) ──
        if self.timer < self.FLASH_DURATION:
            self.flash_alpha = int(self.FLASH_ALPHA * (1.0 - (self.timer / self.FLASH_DURATION)))
        else:
            self.flash_alpha = 0

        # ── 2. Boss Shake and Fade (0.0s to 2.2s) ──
        self._idle_timer += dt
        if self._idle_timer >= self._IDLE_SPEED:
            self._idle_timer -= self._IDLE_SPEED
            self._idle_idx = (self._idle_idx + 1) % max(len(self.idle_frames), 1)

        if self.timer < self.SHAKE_DURATION:
            progress = self.timer / self.SHAKE_DURATION
            self.boss_alpha = int(255 * (1.0 - progress))
            amp = int(14 * (1.0 - progress))
            self.shake_x = self._rng.randint(-amp, amp) if amp > 0 else 0
            self.shake_y = self._rng.randint(-amp // 2, amp // 2) if amp > 0 else 0
        else:
            self.boss_alpha = 0

        # ── 3. Blood Explosion and Splat (DELAYED) ──
        if self.timer < self.BLOOD_DELAY:
            # Keep blood invisible while we wait
            self.splat_alpha = 0
            self.exp_alpha   = 0
            self.splat_scale = 0.2
            self.exp_idx     = 0
        else:
            # Blood has started! Calculate how far along it is.
            blood_timer = self.timer - self.BLOOD_DELAY
            blood_duration = self.SHAKE_DURATION - self.BLOOD_DELAY
            
            splat_progress = min(blood_timer / blood_duration, 1.0)
            self.splat_scale = 0.2 + (self.SPLAT_MAX_SCALE - 0.2) * splat_progress
            
            # Blood fades IN instantly (0.2s), holds, then fades OUT at the end
            if blood_timer < 0.2:
                alpha = int(255 * (blood_timer / 0.2))
            elif self.timer < self.SHAKE_DURATION:
                alpha = 255
            else:
                fade_out_progress = (self.timer - self.SHAKE_DURATION) / (self.DURATION - self.SHAKE_DURATION)
                alpha = int(255 * (1.0 - fade_out_progress))
                
            self.splat_alpha = alpha
            self.exp_alpha   = alpha

            # Sync the explosion frames to finish exactly as he finishes shaking!
            if self.exp_frames:
                self.exp_idx = int((splat_progress) * len(self.exp_frames))
                if self.exp_idx >= len(self.exp_frames):
                    self.exp_idx = len(self.exp_frames) - 1

    def draw(self, surface, camera):
        if self.done:
            return
            
        cx, cy = camera.apply_xy(self.center_x, self.center_y)

        # 1. Draw Splat (Bottom Layer)
        if self._splat_raw is not None and self.splat_alpha > 0:
            raw_w = self._splat_raw.get_width()
            raw_h = self._splat_raw.get_height()
            new_w = max(1, int(raw_w * self.splat_scale))
            new_h = max(1, int(raw_h * self.splat_scale))
            scaled = pygame.transform.scale(self._splat_raw, (new_w, new_h))
            scaled.set_alpha(self.splat_alpha)
            r = scaled.get_rect(center=(cx, cy))
            surface.blit(scaled, r)

        # 2. Draw Shaking Boss (Middle Layer)
        if self.boss_alpha > 0 and self.idle_frames:
            idx = min(self._idle_idx, len(self.idle_frames) - 1)
            img = self.idle_frames[idx].copy()
            img.set_alpha(self.boss_alpha)
            
            if not self.facing_right:
                img = pygame.transform.flip(img, True, False)
                
            r = img.get_rect()
            
            foot_x = int(self.boss_x) + 320
            foot_y = int(self.boss_y) + 640 + self.foot_offset
            sx, sy = camera.apply_xy(foot_x, foot_y)
            
            r.midbottom = (sx + self.shake_x, sy + self.shake_y)
            surface.blit(img, r)

        # 3. Draw Erupting Blood Explosion (Top Layer)
        if self.exp_frames and self.exp_alpha > 0:
            idx = min(self.exp_idx, len(self.exp_frames) - 1)
            img = self.exp_frames[idx].copy()
            img.set_alpha(self.exp_alpha)
            r = img.get_rect(center=(cx, cy))
            surface.blit(img, r)

    def draw_flash(self, surface):
        if self.flash_alpha > 0:
            flash_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            flash_surf.fill((180, 10, 10, self.flash_alpha))
            surface.blit(flash_surf, (0, 0))

# ─────────────────────────────────────────────────────────────────────────────
# EFFECT MANAGER
# ─────────────────────────────────────────────────────────────────────────────
class EffectManager:
    def __init__(self):
        self.hit_effects  = []
        self.death_effect = None

    def spawn_hit(self, world_x, world_y):
        self.hit_effects.append(BloodHit(world_x, world_y))

    def spawn_boss_death(self, boss):
        self.death_effect = BossDeathExplosion(boss)

    @property
    def boss_death_done(self):
        return self.death_effect is not None and self.death_effect.done

    def update(self, dt):
        for fx in self.hit_effects:
            fx.update(dt)
        self.hit_effects = [fx for fx in self.hit_effects if not fx.done]
        if self.death_effect and not self.death_effect.done:
            self.death_effect.update(dt)

    def draw(self, surface, camera):
        for fx in self.hit_effects:
            fx.draw(surface, camera)
        if self.death_effect:
            self.death_effect.draw(surface, camera)

    def draw_flash(self, surface):
        if self.death_effect:
            self.death_effect.draw_flash(surface)

    def reset(self):
        self.hit_effects  = []
        self.death_effect = None