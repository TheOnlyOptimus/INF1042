"""
enemies.py — Enemy classes for Pixel Souls

Expected animation folders in knight_animations/:
    SkeletonSword/   → Idle (4), Walk (8), Attack (5), Hurt (2), Dead (6)
    SkeletonKnight/  → Idle (4), Walk (6), Attack (6), Block (4), Hurt (2), Dead (6)
    Archer/          → Idle (4), Walk (6), Attack (6), Hurt (2), Dead (6)
"""

import pygame
import sfx   # <--- IMPORTED SFX HERE
from utils import load_animation
from settings import LEVEL_W, SPRITE_SCALE

SCALE = SPRITE_SCALE + 1   # 6 — noticeably larger than the player

# Width/height of the sprite canvas
SPR_W = 128 * SCALE
SPR_H = 128 * SCALE


# ─────────────────────────────────────────────────────────────────────────────
# BASE ENEMY
# ─────────────────────────────────────────────────────────────────────────────
class BaseEnemy:
    GRAVITY      = 0.7
    FOOT_OFFSET  = 1
    MAX_HP       = 60
    DAMAGE       = 10
    SPEED        = 3
    KNOCKBACK    = 8
    IFRAMES      = 0.5          
    ATTACK_RANGE = 180          
    AGGRO_RANGE  = 600          
    ANIM_SPEED   = 0.12
    SOUL_DROP    = 100          # base souls — override per subclass         

    def __init__(self, x, y, platforms, facing_right=True):
        self.x            = float(x)
        self.y            = float(y)
        self.platforms    = platforms
        self.facing_right = facing_right
        self.vy           = 0.0
        self.on_ground    = False

        self.hp           = self.MAX_HP
        self.is_dead      = False
        self.death_done   = False    
        self.needs_cull   = False    

        self.state        = "idle"
        self.frame_idx    = 0
        self.frame_timer  = 0.0

        self.iframe_timer = 0.0     
        self.attack_timer = 0.0     
        self.stun_timer   = 0.0     

        self.hitbox_active = False  
        self.animations    = {}
        self._pending_soul_drop = False   # set True when killed; main.py drains it
        self._load_anims()

    def _load_anims(self):
        raise NotImplementedError

    def _ai(self, dt, player):
        raise NotImplementedError

    @property
    def rect(self):
        cw = SPR_W // 4   
        ch = int(SPR_H * 0.40)
        cx = int(self.x) + SPR_W // 2 - cw // 2
        cy = int(self.y) + SPR_H - ch + self.FOOT_OFFSET
        return pygame.Rect(cx, cy, cw, ch)

    @property
    def attack_hitbox(self):
        if not self.hitbox_active:
            return None
        hw = int(SPR_W * 0.35)
        hh = SPR_H // 4
        if self.facing_right:
            hx = int(self.x) + int(SPR_W * 0.6)
        else:
            hx = int(self.x) + int(SPR_W * 0.4) - hw
        hy = int(self.y) + SPR_H // 3
        return pygame.Rect(hx, hy, hw, hh)

    def _dist_to_player(self, player):
        return abs((self.x + SPR_W // 2) - (player.x + SPR_W // 2))

    def _player_is_right(self, player):
        return player.x > self.x

    def _set_state(self, s):
        if self.state != s:
            self.state       = s
            self.frame_idx   = 0
            self.frame_timer = 0.0

    def _anim_speed(self):
        return self.ANIM_SPEED

    def take_damage(self, amount, knockback_right=True):
        if self.iframe_timer > 0 or self.is_dead:
            return
        self.hp -= amount
        self.iframe_timer = self.IFRAMES
        self.stun_timer   = 0.18
        
        if self.hp <= 0:
            sfx.play("death", 1.0)  # <--- ENEMY DEATH SOUND
            self.hp      = 0
            self.is_dead = True
            self._set_state("dead")
            self._pending_soul_drop = True   # main.py picks this up
        else:
            self._set_state("hurt")
            self.x += self.KNOCKBACK * (1 if knockback_right else -1)

    def _resolve_platforms(self):
        self.y += self.vy
        on_ground = False
        pr = self.rect
        for plat in self.platforms:
            if not pr.colliderect(plat):
                continue
            if self.vy >= 0 and (pr.bottom - self.vy) <= plat.top + 16:
                self.y      = float(plat.top - SPR_H + self.FOOT_OFFSET)
                self.vy     = 0.0
                on_ground   = True
        return on_ground

    def update(self, dt, player):
        if self.iframe_timer > 0:
            self.iframe_timer = max(0.0, self.iframe_timer - dt)
        if self.attack_timer > 0:
            self.attack_timer = max(0.0, self.attack_timer - dt)
        if self.stun_timer > 0:
            self.stun_timer = max(0.0, self.stun_timer - dt)

        self.vy       += self.GRAVITY
        self.on_ground = self._resolve_platforms()
        self.x = max(0.0, min(self.x, LEVEL_W - SPR_W))

        if self.is_dead:
            if not self.death_done:
                frames = self.animations.get("dead", [])
                if frames:
                    self.frame_timer += dt
                    speed = self._anim_speed()
                    if self.frame_timer >= speed:
                        self.frame_timer -= speed
                        if self.frame_idx < len(frames) - 1:
                            self.frame_idx += 1
                        else:
                            self.death_done = True   
            return

        if self.stun_timer <= 0:
            self._ai(dt, player)

        if self.hitbox_active and self.attack_hitbox:
            if self.attack_hitbox.colliderect(player.rect):
                player.take_damage(self.DAMAGE,
                                   knockback_right=self._player_is_right(player))

        self._tick_anim(dt)

    def _tick_anim(self, dt, loop=True, on_finish=None):
        frames = self.animations.get(self.state)
        if not frames:
            return
        self.frame_timer += dt
        speed = self._anim_speed()
        if self.frame_timer < speed:
            return
        self.frame_timer -= speed
        next_idx = self.frame_idx + 1
        if next_idx >= len(frames):
            if loop:
                self.frame_idx = 0
            else:
                self.frame_idx = len(frames) - 1   
                if on_finish == "done":
                    self.death_done = True           
                elif on_finish == "idle":
                    self._set_state("idle")
        else:
            self.frame_idx = next_idx

    def draw(self, surface, camera):
        frames = self.animations.get(self.state)
        if not frames:
            return
        idx = max(0, min(self.frame_idx, len(frames) - 1))
        img = frames[idx]
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)

        foot_x = int(self.x) + SPR_W // 2
        foot_y = int(self.y) + SPR_H + self.FOOT_OFFSET
        sx, sy = camera.apply_xy(foot_x, foot_y)

        r = img.get_rect()
        r.midbottom = (sx, sy)
        surface.blit(img, r)

        if 0 < self.hp < self.MAX_HP:
            bw, bh = 80, 6
            bx = sx - bw // 2
            by = sy - int(SPR_H * 0.55)  
            pygame.draw.rect(surface, (40, 10, 10), (bx, by, bw, bh))
            fill = int(bw * self.hp / self.MAX_HP)
            pygame.draw.rect(surface, (180, 30, 30), (bx, by, fill, bh))


# ─────────────────────────────────────────────────────────────────────────────
class SkeletonSword(BaseEnemy):
    MAX_HP        = 50
    DAMAGE        = 10
    SPEED         = 3
    ATTACK_RANGE  = 200
    AGGRO_RANGE   = 550
    ATTACK_CD     = 0.8
    BLOCK_DURATION = 1.0
    SOUL_DROP     = 150    

    def __init__(self, *args, **kwargs):
        self.block_timer      = 0.0
        self.is_blocking      = False
        super().__init__(*args, **kwargs)

    def _load_anims(self):
        def _try(folder, n):
            try:    return load_animation(folder, n, SCALE)
            except: return _fallback(n)
        def _fallback(n):
            s = pygame.Surface((SPR_W, SPR_H), pygame.SRCALPHA)
            s.fill((255, 0, 200))
            return [s] * n

        self.animations = {
            "idle":   _try("SkeletonSword/Idle",   4),
            "walk":   _try("SkeletonSword/Walk",   4),
            "attack": _try("SkeletonSword/Attack", 8),
            "block":  _try("SkeletonSword/Block",  4),  
            "hurt":   _try("SkeletonSword/Hurt",   4),
            "dead":   _try("SkeletonSword/Dead",   4),
        }

    def take_damage(self, amount, knockback_right=True):
        if self.is_blocking:
            amount = max(1, amount // 4)    
            if self.iframe_timer > 0 or self.is_dead:
                return
            self.hp -= amount
            self.iframe_timer = self.IFRAMES
            
            if self.hp <= 0:
                sfx.play("death", 1.0)  # <--- SHIELD BREAK DEATH SOUND
                self.hp      = 0
                self.is_dead = True
                self._set_state("dead")
            return
        super().take_damage(amount, knockback_right)

    def _should_block(self, player):
        if self.is_dead or self.state == "attack":
            return False
        dist = self._dist_to_player(player)
        if dist > self.ATTACK_RANGE * 1.5:
            return False
        player_facing_us = ((player.facing_right and player.x < self.x) or
                            (not player.facing_right and player.x > self.x))
        return player_facing_us and player.hitbox_active

    def _ai(self, dt, player):
        if self._should_block(player):
            self.is_blocking  = True
            self.block_timer  = self.BLOCK_DURATION
            self._set_state("block")
            return

        if self.block_timer > 0:
            self.block_timer -= dt
            self.is_blocking  = self.block_timer > 0
            if self.is_blocking:
                self._set_state("block")
                return
            else:
                self._set_state("idle")

        dist = self._dist_to_player(player)
        if dist < self.AGGRO_RANGE:
            self.facing_right = self._player_is_right(player)

        if dist < self.ATTACK_RANGE and self.attack_timer <= 0:
            self._set_state("attack")
            self.attack_timer = self.ATTACK_CD
            return

        if dist < self.AGGRO_RANGE and self.state != "attack":
            # AI SPACING FIX: Stand still and wait for cooldown instead of walking into player
            if dist > self.ATTACK_RANGE - 40:
                self.x += self.SPEED * (1 if self._player_is_right(player) else -1)
                self._set_state("walk")
            else:
                self._set_state("idle")
            return

        if self.state not in ("attack", "hurt", "block"):
            self._set_state("idle")

        if self.state == "attack":
            self.hitbox_active = (6 <= self.frame_idx <= 7)
        else:
            self.hitbox_active = False

    def _tick_anim(self, dt, loop=True, on_finish=None):
        if self.state in ("attack", "hurt"):
            super()._tick_anim(dt, loop=False, on_finish="idle")
        else:
            super()._tick_anim(dt, loop=loop, on_finish=on_finish)


# ─────────────────────────────────────────────────────────────────────────────
class SkeletonKnight(BaseEnemy):
    MAX_HP      = 120
    DAMAGE      = 18
    SPEED       = 2
    KNOCKBACK   = 4
    ATTACK_RANGE = 220
    AGGRO_RANGE  = 500
    SOUL_DROP   = 300

    ATTACK_DEFS = {
        "attack_low":       (15,     1.2),  # FASTER COOLDOWNS
        "attack_forward":   (20,     1.6),
        "attack_side":      (25,     1.4),
        "attack_combo":     (45,     2.2),
    }

    def __init__(self, *args, **kwargs):
        self.attack_timer = 0.0
        super().__init__(*args, **kwargs)

    def _load_anims(self):
        def _try(folder, n):
            try:    return load_animation(folder, n, SCALE)
            except: return _fallback(n)
        def _fallback(n):
            s = pygame.Surface((SPR_W, SPR_H), pygame.SRCALPHA)
            s.fill((80, 80, 200))
            return [s] * n

        self.animations = {
            "idle":           _try("SkeletonKnight/Idle",          11),
            "walk":           _try("SkeletonKnight/Walk",          9),
            "attack_low":     _try("SkeletonKnight/Attack_Low",    7),
            "attack_forward": _try("SkeletonKnight/Attack_Forward",7),
            "attack_side":    _try("SkeletonKnight/Attack_Side",   7),
            "attack_combo":   _try("SkeletonKnight/Attack_Combo",  21),
            "hurt":           _try("SkeletonKnight/Hurt",          2),
            "dead":           _try("SkeletonKnight/Dead",          9),
        }
        self._current_damage = 18   

    def _choose_attack(self, dist):
        import random
        if dist < 160:
            return random.choice(["attack_low", "attack_combo"])
        elif dist < 200:
            return random.choice(["attack_side", "attack_forward"])
        else:
            return "attack_forward"

    def _ai(self, dt, player):
        dist = self._dist_to_player(player)
        if dist < self.AGGRO_RANGE:
            self.facing_right = self._player_is_right(player)

        in_attack = self.state in self.ATTACK_DEFS
        if dist < self.ATTACK_RANGE and self.attack_timer <= 0 and not in_attack:
            chosen = self._choose_attack(dist)
            dmg, cd = self.ATTACK_DEFS[chosen]
            self._current_damage = dmg
            self.attack_timer    = cd
            self._set_state(chosen)
            return

        if dist < self.AGGRO_RANGE and not in_attack:
            # AI SPACING FIX: Stand still and wait for cooldown instead of walking into player
            if dist > self.ATTACK_RANGE - 40:
                self.x += self.SPEED * (1 if self._player_is_right(player) else -1)
                self._set_state("walk")
            else:
                self._set_state("idle")
            return

        if not in_attack and self.state not in ("hurt",):
            self._set_state("idle")

        if in_attack:
            frames = self.animations.get(self.state, [])
            n = len(frames)
            hit_start = int(n * 0.55)
            hit_end   = int(n * 0.85)
            self.hitbox_active = hit_start <= self.frame_idx <= hit_end
            self.attack_damage = self._current_damage
        else:
            self.hitbox_active = False

    def _tick_anim(self, dt, loop=True, on_finish=None):
        if self.state in self.ATTACK_DEFS or self.state == "hurt":
            super()._tick_anim(dt, loop=False, on_finish="idle")
        else:
            super()._tick_anim(dt, loop=loop, on_finish=on_finish)


# ─────────────────────────────────────────────────────────────────────────────
class Arrow:
    SPEED  = 15
    DAMAGE = 12
    WIDTH  = 200   
    HEIGHT = 100   

    def __init__(self, x, y, going_right, vy=0):
        self.x           = float(x)
        self.y           = float(y)
        self.going_right = going_right
        self.vy          = vy       
        self.alive       = True

        import os
        from settings import BASE_PATH
        import pygame
        
        arrow_path = os.path.join(BASE_PATH, "assets", "arrow.png")
        img = pygame.image.load(arrow_path).convert_alpha()
        img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
        img = pygame.transform.flip(img, True, False)
        if not going_right:
            img = pygame.transform.flip(img, True, False)
            
        self.img = img

    @property
    def rect(self):
        hitbox_w = 40  
        hitbox_h = 16  
        if self.going_right:
            hx = int(self.x) + self.WIDTH - hitbox_w - 5
        else:
            hx = int(self.x) + 5
        hy = int(self.y) - (hitbox_h // 2)
        return pygame.Rect(hx, hy, hitbox_w, hitbox_h)

    def update(self, dt, platforms, player):
        self.x += self.SPEED * (1 if self.going_right else -1)
        self.y += self.vy

        if self.x < -200 or self.x > LEVEL_W + 200:
            self.alive = False
            return
        for plat in platforms:
            if self.rect.colliderect(plat):
                self.alive = False
                return
        if self.rect.colliderect(player.rect):
            player.take_damage(self.DAMAGE, knockback_right=self.going_right)
            self.alive = False

    def draw(self, surface, camera):
        sx, sy = camera.apply_xy(int(self.x), int(self.y))
        surface.blit(self.img, (sx, sy - self.HEIGHT // 2))


class Archer(BaseEnemy):
    MAX_HP         = 40
    SPEED          = 3
    AGGRO_RANGE    = 800
    PREFERRED_DIST = 450
    TOO_CLOSE_DIST = 220
    ATTACK_CD      = 2.0
    ATTACK_RANGE   = 750
    SOUL_DROP      = 200

    def __init__(self, *args, **kwargs):
        self.arrows              = []
        self._shot_this_attack   = False
        super().__init__(*args, **kwargs)

    def _load_anims(self):
        def _try(folder, n):
            try:    return load_animation(folder, n, SCALE)
            except: return _fallback(n)
        def _fallback(n):
            s = pygame.Surface((SPR_W, SPR_H), pygame.SRCALPHA)
            s.fill((60, 180, 60))
            return [s] * n

        self.animations = {
            "idle":          _try("Archer/Idle",          2),
            "walk":          _try("Archer/Walk",          8),
            "attack":        _try("Archer/Attack",        11),  
            "hurt":          _try("Archer/Hurt",          4),
            "dead":          _try("Archer/Dead",          10),
        }

    def _fire_arrow(self, player):
        # FIX: Perfectly anchor arrow spawn to the body center and lower to chest!
        center_x = int(self.x) + SPR_W // 2
        
        # Adjusting arrow to spawn correctly at the bow
        bow_x = center_x + (60 if self.facing_right else -60)
        
        # Lowering the arrow spawn point to match the archer's torso instead of his head
        arrow_y = int(self.y) + int(SPR_H * 0.75)
        
        # Subtract arrow width when facing left so the tip aligns with the bow
        if not self.facing_right:
            bow_x -= 200  # Arrow.WIDTH
            
        self.arrows.append(Arrow(bow_x, arrow_y, self.facing_right, vy=0))
        self._shot_this_attack = True

    def _ai(self, dt, player):
        dist = self._dist_to_player(player)
        if dist < self.AGGRO_RANGE:
            self.facing_right = self._player_is_right(player)

        if dist < self.TOO_CLOSE_DIST and self.state != "attack":
            self.x -= self.SPEED * (1 if self._player_is_right(player) else -1)
            self._set_state("walk")
            return

        in_attack = (self.state == "attack")
        
        if dist < self.ATTACK_RANGE and self.attack_timer <= 0 and not in_attack:
            self._shot_this_attack = False
            self.attack_timer      = self.ATTACK_CD
            self._set_state("attack")
            return

        if dist < self.AGGRO_RANGE and not in_attack:
            if dist < self.PREFERRED_DIST - 60:
                self.x -= self.SPEED * (1 if self._player_is_right(player) else -1)
                self._set_state("walk")
            elif dist > self.PREFERRED_DIST + 60:
                self.x += self.SPEED * (1 if self._player_is_right(player) else -1)
                self._set_state("walk")
            else:
                self._set_state("idle")
            return

        if not in_attack and self.state not in ("hurt",):
            self._set_state("idle")

        if in_attack:
            frames = self.animations[self.state]
            fire_frame = len(frames) // 2
            if self.frame_idx == fire_frame and not self._shot_this_attack:
                self._fire_arrow(player)

    def update(self, dt, player):
        super().update(dt, player)
        for arrow in self.arrows:
            arrow.update(dt, self.platforms, player)
        self.arrows = [a for a in self.arrows if a.alive]

    def draw(self, surface, camera):
        super().draw(surface, camera)
        for arrow in self.arrows:
            arrow.draw(surface, camera)

    def _tick_anim(self, dt, loop=True, on_finish=None):
        if self.state in ("attack", "hurt"):
            super()._tick_anim(dt, loop=False, on_finish="idle")
        else:
            super()._tick_anim(dt, loop=loop, on_finish=on_finish)