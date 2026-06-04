"""
boss.py — The Hooded Knight, boss of Area 1
"""

import pygame
import os
import random
import sfx   
from utils import load_animation
from settings import LEVEL_W, SPRITE_SCALE, BASE_PATH, WIDTH, HEIGHT

BOSS_SCALE = SPRITE_SCALE + 1   

BOSS_W = 128 * BOSS_SCALE       
BOSS_H = 128 * BOSS_SCALE       

ANIM_FRAMES = {
    "idle":              6,
    "walk":              10,
    "attack_1":          17,
    "phase_transition": 18,
    "attack_2":         18,
    "hurt":              4,
    "dead":             10,
}

FOLDER_MAP = {
    "idle":             "Idle",
    "walk":             "Walk",
    "attack_1":         "Attack_1",
    "phase_transition": "Phase_Transition",
    "attack_2":         "Attack_2",
    "hurt":             "Hurt",
    "dead":             "Dead",
}

# ─────────────────────────────────────────────────────────────────────────────
class LightningBolt:
    SPEED  = 11          
    DAMAGE = 25         
    W      = 156         
    H      = 100          

    def __init__(self, x, y, going_right):
        self.x           = float(x)
        self.y           = float(y)
        self.going_right = going_right
        self.alive       = True

        path = os.path.join(BASE_PATH, "assets", "Lightning.png")
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.rotate(img, 90)
            img = pygame.transform.scale(img, (self.W, self.H))
            if not going_right:
                img = pygame.transform.flip(img, True, False)
            self.img = img
        except Exception:
            self.img = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            self.img.fill((255, 220, 0, 200))

        bright = self.img.copy()
        bright.fill((255, 255, 180, 80), special_flags=pygame.BLEND_RGBA_ADD)
        self._imgs    = [self.img, bright]
        self._flicker = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def update(self, dt, player):
        self.x       += self.SPEED * (1 if self.going_right else -1)
        self._flicker = 1 - self._flicker
        if self.x < -400 or self.x > LEVEL_W + 400:
            self.alive = False
            return
        if self.rect.colliderect(player.rect):
            player.take_damage(self.DAMAGE, knockback_right=self.going_right)
            self.alive = False

    def draw(self, surface, camera):
        sx, sy = camera.apply_xy(int(self.x), int(self.y))
        surface.blit(self._imgs[self._flicker], (sx, sy - self.H // 2))

# ─────────────────────────────────────────────────────────────────────────────
class HoodedKnight:
    MAX_HP           = 1000
    GRAVITY          = 0.7
    FOOT_OFFSET      = 0
    IFRAMES          = 0.6
    KNOCKBACK        = 2
    SOUL_DROP        = 5000   # big reward for killing the boss

    P1_SPEED         = 2.5
    P1_ATTACK_RANGE  = 260       
    P1_ATTACK_CD     = 2.0       
    P1_DAMAGE        = 22
    P1_ANIM_SPEED    = 0.11
    P1_IDLE_RANGE    = 180       

    P2_HP_THRESHOLD  = 0.65
    P2_SPEED         = 4.0
    P2_MELEE_RANGE   = 260       
    P2_LIGHTNING_RANGE = 700     
    P2_ATTACK_CD     = 1.8       
    P2_LIGHTNING_CD  = 3.5       
    P2_MELEE_DAMAGE  = 30
    P2_LIGHTNING_DMG = 35        
    P2_ANIM_SPEED    = 0.085

    ATTACK_FRAMES = {
        "attack_1": (8, 11),
        "attack_2": (6, 8),
    }

    def __init__(self, x, y, platforms):
        self.x             = float(x)
        self.y             = float(y)
        self.platforms     = platforms
        self.facing_right  = False
        self.vy            = 0.0
        self.on_ground     = False

        self.hp            = self.MAX_HP
        self.is_dead       = False
        self.death_done    = False
        self.fight_active  = False
        self.phase         = 1
        self.transitioning = False

        self.state         = "idle"
        self.frame_idx     = 0
        self.frame_timer   = 0.0

        self.iframe_timer      = 0.0
        self.attack_timer      = 0.0
        self.lightning_timer   = 0.0   
        self.hitbox_active     = False
        self.attack_damage     = 0

        self.lightning_bolts        = []
        self._shot_this_attack      = False
        self._phase2_music_needed   = False   
        self._pending_soul_drop     = False   # main.py picks this up on boss death
        
        self._prev_state            = "idle"
        self._last_step_frame       = -1

        self.animations = {}
        self._load_anims()
        self._hud_fonts = None   

    def _load_anims(self):
        for key, count in ANIM_FRAMES.items():
            folder = f"HoodedKnight/{FOLDER_MAP[key]}"
            try:
                frames = load_animation(folder, count, BOSS_SCALE)
            except Exception as e:
                s = pygame.Surface((BOSS_W, BOSS_H), pygame.SRCALPHA)
                s.fill((120, 60, 180, 200))
                frames = [s] * count
            self.animations[key] = frames

    @property
    def rect(self):
        cw = int(BOSS_W * 0.25)
        ch = int(BOSS_H * 0.6)
        cx = int(self.x) + BOSS_W // 2 - cw // 2
        cy = int(self.y) + BOSS_H - ch + self.FOOT_OFFSET
        return pygame.Rect(cx, cy, cw, ch)

    @property
    def attack_hitbox(self):
        if not self.hitbox_active:
            return None
        hw = int(BOSS_W * 0.4)
        hh = int(BOSS_H * 0.3)
        if self.facing_right:
            hx = int(self.x) + int(BOSS_W * 0.5)
        else:
            hx = int(self.x) + int(BOSS_W * 0.5) - hw
        hy = int(self.y) + int(BOSS_H * 0.4)
        return pygame.Rect(hx, hy, hw, hh)

    def _dist(self, player):
        return abs((self.x + BOSS_W // 2) - (player.x + BOSS_W // 2))

    def _player_right(self, player):
        return player.x > self.x

    def _set_state(self, s):
        if self.state != s:
            self.state       = s
            self.frame_idx   = 0
            self.frame_timer = 0.0

    def _anim_spd(self):
        return self.P2_ANIM_SPEED if self.phase == 2 else self.P1_ANIM_SPEED

    def _spd(self):
        return self.P2_SPEED if self.phase == 2 else self.P1_SPEED

    def _atk_cd(self):
        return self.P2_ATTACK_CD if self.phase == 2 else self.P1_ATTACK_CD

    def take_damage(self, amount, knockback_right=True):
        if self.iframe_timer > 0 or self.is_dead or self.transitioning: return
        if not self.fight_active: return

        self.hp          -= amount
        self.iframe_timer = self.IFRAMES

        if self.hp <= 0:
            sfx.play("death", 1.0) 
            self.hp      = 0
            self.is_dead = True
            self._set_state("dead")
            self._pending_soul_drop = True   # main.py picks this up
            return

        if self.phase == 1 and self.hp <= self.MAX_HP * self.P2_HP_THRESHOLD and not self.transitioning:
            self.transitioning = True
            self.hitbox_active = False   
            self.vy = 0.0             
            self._set_state("phase_transition")
            self._start_fadeout = True  
            return

    def _resolve_platforms(self):
        self.y += self.vy
        on_ground = False
        pr = self.rect
        for plat in self.platforms:
            if not pr.colliderect(plat):
                continue
            if self.vy >= 0 and (pr.bottom - self.vy) <= plat.top + 40:
                self.y      = float(plat.top - BOSS_H + self.FOOT_OFFSET)
                self.vy     = 0.0
                on_ground   = True
        return on_ground

    def _sword_handle_pos(self):
        if self.facing_right:
            hx = int(self.x) + int(BOSS_W * 0.75)
        else:
            hx = int(self.x) + int(BOSS_W * 0.25)
        hy = int(self.y) + int(BOSS_H * 0.70)
        return hx, hy

    def _fire_lightning(self):
        hx, hy = self._sword_handle_pos()
        self.lightning_bolts.append(LightningBolt(hx, hy, self.facing_right))
        self._shot_this_attack = True
        sfx.play("boss_lightning", 0.9)

    def _ai(self, player):
        if not self.fight_active:
            self._set_state("idle")
            return

        dist = self._dist(player)
        self.facing_right = self._player_right(player)

        if self.transitioning:
            return

        in_attack = self.state in ("attack_1", "attack_2")

        if self.phase == 1:
            if dist < self.P1_ATTACK_RANGE and self.attack_timer <= 0 and not in_attack:
                self._set_state("attack_1")
                self.attack_timer      = self.P1_ATTACK_CD
                self._shot_this_attack = False
                return

            if not in_attack:
                if dist > self.P1_ATTACK_RANGE:
                    self.x += self.P1_SPEED * (1 if self._player_right(player) else -1)
                    self._set_state("walk")
                else:
                    self._set_state("idle")

            if self.state == "attack_1":
                start_f, end_f = self.ATTACK_FRAMES["attack_1"]
                self.hitbox_active = (start_f <= self.frame_idx <= end_f)
                self.attack_damage = self.P1_DAMAGE
            else:
                self.hitbox_active = False

        else:
            if not in_attack:
                if dist < self.P2_MELEE_RANGE:
                    if self.attack_timer <= 0:
                        self._set_state("attack_1")
                        self.attack_timer = self.P2_ATTACK_CD
                    else:
                        self._set_state("idle")   
                elif dist < self.P2_LIGHTNING_RANGE:
                    self.x += self.P2_SPEED * (1 if self._player_right(player) else -1)
                    self._set_state("walk")
                    if self.lightning_timer <= 0 and dist > self.P2_MELEE_RANGE + 100:
                        self._set_state("attack_2")
                        self._shot_this_attack = False
                        self.lightning_timer   = self.P2_LIGHTNING_CD
                else:
                    self.x += self.P2_SPEED * (1 if self._player_right(player) else -1)
                    self._set_state("walk")

            if self.state == "attack_1":
                start_f, end_f = self.ATTACK_FRAMES["attack_1"]
                self.hitbox_active = (start_f <= self.frame_idx <= end_f)
                self.attack_damage = self.P2_MELEE_DAMAGE
            elif self.state == "attack_2":
                start_f, end_f = self.ATTACK_FRAMES["attack_2"]
                self.hitbox_active = (start_f <= self.frame_idx <= end_f)
                self.attack_damage = self.P2_MELEE_DAMAGE
                if self.frame_idx == 5 and not self._shot_this_attack:
                    self._fire_lightning()
            else:
                self.hitbox_active = False

    def _tick_anim(self, dt):
        frames = self.animations.get(self.state)
        if not frames: return
        
        self.frame_timer += dt
        if self.frame_timer < self._anim_spd(): return
        self.frame_timer -= self._anim_spd()
        nxt = self.frame_idx + 1

        if self.state in ("attack_1", "attack_2"):
            if nxt >= len(frames):
                self.hitbox_active = False
                self._set_state("idle")
            else:
                self.frame_idx = nxt
            return

        if self.state == "phase_transition":
            if nxt >= len(frames):
                self.phase         = 2
                self.transitioning = False
                self.hitbox_active = False
                self.stun_timer = 1.0  
                self.attack_timer = 1.5 
                self._phase2_music_needed = True
                self._set_state("idle")
            else:
                self.frame_idx = nxt
            return

        self.frame_idx = nxt % len(frames)

    def _play_sfx(self, dt):
        s = self.state
        prev = self._prev_state

        if s != prev:
            self._swing_played = False   
            if s == "attack_2":
                sfx.play("boss_magic", 0.8)  
            elif s == "phase_transition":
                sfx.play("boss_phase", 1.0)

        # Attack windup sound
        if s == "attack_1":
            if self.frame_idx == 6 and not getattr(self, '_swing_played', False):
                sfx.play("boss_swing", 0.8)
                self._swing_played = True

        # NEW: Perfect Footsteps! Synced to exact animation frames (3 and 8)
        if self.on_ground and s == "walk":
            if self.frame_idx in (3, 8):
                if self.frame_idx != self._last_step_frame:
                    sfx.play("boss_step", 0.6)  # Bumped volume so you can hear his weight
                    self._last_step_frame = self.frame_idx
            else:
                self._last_step_frame = -1

        self._prev_state = s

    def update(self, dt, player):
        if self.iframe_timer  > 0: self.iframe_timer  = max(0.0, self.iframe_timer  - dt)
        if self.attack_timer  > 0: self.attack_timer  = max(0.0, self.attack_timer  - dt)
        if self.lightning_timer > 0: self.lightning_timer = max(0.0, self.lightning_timer - dt)

        self.vy       += self.GRAVITY
        self.on_ground = self._resolve_platforms()
        self.x = max(0.0, min(self.x, LEVEL_W - BOSS_W))

        if self.is_dead:
            if not self.death_done:
                frames = self.animations.get("dead", [])
                if frames:
                    self.frame_timer += dt
                    if self.frame_timer >= self._anim_spd():
                        self.frame_timer -= self._anim_spd()
                        if self.frame_idx < len(frames) - 1:
                            self.frame_idx += 1
                        else:
                            self.death_done = True
            return

        self._ai(player)

        if self.hitbox_active and self.attack_hitbox:
            if self.attack_hitbox.colliderect(player.rect):
                player.take_damage(self.attack_damage, knockback_right=self._player_right(player))

        for bolt in self.lightning_bolts:
            bolt.update(dt, player)
        self.lightning_bolts = [b for b in self.lightning_bolts if b.alive]

        self._tick_anim(dt)
        self._play_sfx(dt)  

    def draw(self, surface, camera):
        frames = self.animations.get(self.state)
        if not frames: return
        idx = max(0, min(self.frame_idx, len(frames) - 1))
        img = frames[idx]
        
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)

        foot_x = int(self.x) + BOSS_W // 2
        foot_y = int(self.y) + BOSS_H + self.FOOT_OFFSET
        sx, sy = camera.apply_xy(foot_x, foot_y)
        
        r = img.get_rect()
        r.midbottom = (sx, sy)
        surface.blit(img, r)

        for bolt in self.lightning_bolts:
            bolt.draw(surface, camera)

    def draw_hud(self, surface):
        if self.is_dead or self.death_done or not self.fight_active: return

        if self._hud_fonts is None:
            self._hud_fonts = {
                "title":    pygame.font.SysFont("Georgia", 20, bold=True),
                "subtitle": pygame.font.SysFont("Georgia", 13),
                "phase":    pygame.font.SysFont("Georgia", 12),
            }

        bar_w = 500
        bar_h = 10
        bar_x = WIDTH  // 2 - bar_w // 2
        bar_y = HEIGHT - 80

        fill_c = (160, 30, 30)
        hi_c   = (200, 80, 80)
        ttl_c  = (255, 255, 255)
        sub_c  = (130, 115, 80)

        t = self._hud_fonts["title"].render("The  Fallen  Knight", True, ttl_c)
        surface.blit(t, (WIDTH // 2 - t.get_width() // 2, bar_y - 30))

        pygame.draw.rect(surface, (15, 8, 8), (bar_x, bar_y, bar_w, bar_h))
        fill = int(bar_w * max(self.hp, 0) / self.MAX_HP)
        if fill > 0:
            pygame.draw.rect(surface, fill_c, (bar_x, bar_y, fill, bar_h))
            pygame.draw.rect(surface, hi_c,   (bar_x, bar_y, fill, 2))

        cc = (80, 60, 60)
        pygame.draw.line(surface, cc, (bar_x,         bar_y - 3), (bar_x,         bar_y + bar_h + 3), 1)
        pygame.draw.line(surface, cc, (bar_x + bar_w, bar_y - 3), (bar_x + bar_w, bar_y + bar_h + 3), 1)