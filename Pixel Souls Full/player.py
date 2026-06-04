import pygame
from enums import State
import sfx
from utils import load_animation
from souls import SoulManager
from settings import (
    WIDTH, HEIGHT, LEVEL_W, SPRITE_SCALE,
    ANIM_MANIFEST, ANIM_SPEEDS, ANIM_OFFSETS,
    LIGHT_COMBO, HEAVY_COMBO, COMBO_BUFFER,
    PLAYER_HEIGHT, PLAYER_WIDTH,
)

# Locked states — block most input
LOCKED_STATES = (
    State.ROLL, State.HURT, State.DEAD,
    State.ATTACK_1, State.ATTACK_2, State.ATTACK_3,
    State.RUN_ATTACK, State.JUMP_ATTACK,
    State.POWER_ATK_1, State.POWER_ATK_2,
    State.SHIELD_STRIKE,
    State.PULL_UP, State.ELIXIR, State.PICK_UP,
    State.INVOCATION,
    State.RESTING,
    State.STAND_UP
)

ONE_SHOT_STATES = (
    State.HURT, State.PULL_UP, State.ELIXIR,
    State.PICK_UP, State.INVOCATION,State.STAND_UP,
)
ACTIVE_HITBOX_FRAMES = {
    State.ATTACK_1:      (2, 4),  # Hits on frames 3, 4, 5
    State.ATTACK_2:      (1, 3),  
    State.ATTACK_3:      (1, 3),  
    State.RUN_ATTACK:    (3, 5),  
    State.JUMP_ATTACK:   (2, 4),  
    State.POWER_ATK_1:   (3, 4),  
    State.POWER_ATK_2:   (2, 3),  
    State.SHIELD_STRIKE: (1, 3),
}


class Player:
    GRAVITY       = 0.7
    JUMP_FORCE    = -14
    SPEED         = 5
    RUN_SPEED     = 9
    COYOTE_TIME   = 0.12

    MAX_HP        = 100
    MAX_STAMINA   = 100
    MAX_FLASKS    = 10
    FLASK_HEAL    = 40

    IFRAMES_HIT   = 0.7
    HIT_KNOCKBACK = 25

    ROLL_DURATION = 0.45
    ROLL_SPEED    = 11

    STAMINA_REGEN         = 20
    STAMINA_ROLL          = 25
    STAMINA_ATTACK        = 20
    STAMINA_HEAVY         = 30
    STAMINA_SHIELD_STRIKE = 20
    STAMINA_BLOCK_DRAIN   = 10
    STAMINA_RUN = 10
    FOOT_OFFSET           = + 1

    def __init__(self, platforms, spawn_x=300, spawn_y=None):
        self.platforms = platforms   # list of pygame.Rect

        # Spawn on top of first platform if no y given
        if spawn_y is None:
            spawn_y = platforms[0].top - PLAYER_HEIGHT + self.FOOT_OFFSET

        self.x       = float(spawn_x)
        self.y       = float(spawn_y)
        self.spawn_x = self.x
        self.spawn_y = self.y

        self.vy            = 0.0
        self.facing_right  = True
        self.on_ground     = False
        self.coyote_timer  = 0.0

        self.hp             = self.MAX_HP
        self.stamina        = float(self.MAX_STAMINA)
        self.flasks         = self.MAX_FLASKS
        self.is_dead        = False
        self.death_finished = False

        self.invulnerable  = False
        self.iframe_timer  = 0.0
        self.roll_timer    = 0.0

        self.combo_chain        = []
        self.combo_idx          = -1
        self.combo_queued       = False
        self.combo_buffer_timer = 0.0
        self.is_heavy           = False
        self.hitbox_active      = False
        self.attack_damage      = 0

        self.state       = State.IDLE
        self.frame_idx   = 0
        self.frame_timer = 0.0
        self._walk_timer   = 0.0
        self._prev_state   = State.IDLE
        self._was_grounded = False

        # ── Soul / leveling system ──────────────────────────────────────────
        self.souls_mgr    = SoulManager()
        self._bonus_damage = 0   # updated by level_up._apply_stats

        # ── Dropped-soul orb (world position of last death) ─────────────────
        self._soul_drop_x  = None
        self._soul_drop_y  = None

        self.animations = {}
        for state, (folder_name, frame_count) in ANIM_MANIFEST.items():
            self.animations[state] = load_animation(folder_name, frame_count,
                                                     SPRITE_SCALE)
        if State.STAND_UP in self.animations:
            self.animations[State.STAND_UP] = self.animations[State.STAND_UP][::-1]
    # ── collision rect ─────────────────────────────────────────────────────────
    @property
    def rect(self):
        cw = PLAYER_WIDTH // 3
        ch = int(PLAYER_HEIGHT * 0.55)
        cx = int(self.x) + PLAYER_WIDTH // 2 - cw // 2
        cy = int(self.y) + PLAYER_HEIGHT - ch + self.FOOT_OFFSET
        return pygame.Rect(cx, cy, cw, ch)
    
    # ── helpers ────────────────────────────────────────────────────────────────
    def _set_state(self, s):
        if self.state != s:
            self.state       = s
            self.frame_idx   = 0
            self.frame_timer = 0.0

    def _is_locked(self):
        return self.state in LOCKED_STATES

    def _use_stamina(self, amount):
        if self.stamina < amount:
            return False
        self.stamina -= amount
        return True

    def _in_combo(self):
        return self.combo_idx >= 0 and bool(self.combo_chain)

    def _get_attack_hitbox(self):
        attack_states = (
            State.ATTACK_1, State.ATTACK_2, State.ATTACK_3,
            State.RUN_ATTACK, State.JUMP_ATTACK,
            State.POWER_ATK_1, State.POWER_ATK_2,
            State.SHIELD_STRIKE,
        )
        if not self.hitbox_active or self.state not in attack_states:
            return None

        hand_x = int(self.x) + PLAYER_WIDTH // 2
        hand_y = int(self.y) + int(PLAYER_HEIGHT * 0.60)

        # REDUCED THE SWORD REACH
        sword_len = int(PLAYER_WIDTH * 0.4)    
        sword_h   = int(PLAYER_HEIGHT * 0.12)  

        if self.facing_right:
            hx = hand_x
        else:
            hx = hand_x - sword_len

        return pygame.Rect(hx, hand_y, sword_len, sword_h)

    # ── combo ──────────────────────────────────────────────────────────────────
    def _start_combo(self, chain, heavy=False):
        if not chain:
            return
        if not self._use_stamina(self.STAMINA_HEAVY if heavy else self.STAMINA_ATTACK):
            return
        self.combo_chain        = chain
        self.combo_idx          = 0
        self.is_heavy           = heavy
        self.combo_queued       = False
        self.combo_buffer_timer = 0.0
        self._set_state(chain[0][0])

    def _advance_combo(self):
        next_idx = self.combo_idx + 1
        if next_idx < len(self.combo_chain) and self.combo_queued:
            cost = self.STAMINA_HEAVY if self.is_heavy else self.STAMINA_ATTACK
            if self._use_stamina(cost):
                self.combo_idx          = next_idx
                self.combo_queued       = False
                self.combo_buffer_timer = 0.0
                self._set_state(self.combo_chain[next_idx][0])
                return
        self.combo_chain        = []
        self.combo_idx          = -1
        self.combo_queued       = False
        self.combo_buffer_timer = 0.0
        self.hitbox_active      = False
        self._set_state(State.IDLE)

    # ── damage ─────────────────────────────────────────────────────────────────
    def take_damage(self, amount, knockback_right=True):
        if self.invulnerable or self.is_dead:
            return
        if self.state in (State.BLOCK, State.DEFEND):
            amount = max(1, amount // 4)
            self._use_stamina(self.STAMINA_BLOCK_DRAIN)
        self.hp -= amount
        self._cancel_actions()
        if self.hp <= 0:
            self.hp      = 0
            self.is_dead = True
            self._set_state(State.DEAD)
            # Drop souls at death location
            self.souls_mgr.on_death()
            self._soul_drop_x = int(self.x) + PLAYER_WIDTH // 2
            # FIX: Anchor the orb to the floor at your feet, not up in the sky!
            self._soul_drop_y = int(self.y) + PLAYER_HEIGHT + self.FOOT_OFFSET - 30
        else:
            self._set_state(State.HURT)
            self.x += self.HIT_KNOCKBACK * (1 if knockback_right else -1)
        self.invulnerable = True
        self.iframe_timer = self.IFRAMES_HIT

    def _cancel_actions(self):
        self.roll_timer         = 0.0
        self.combo_chain        = []
        self.combo_idx          = -1
        self.combo_queued       = False
        self.combo_buffer_timer = 0.0
        self.hitbox_active      = False

    def respawn(self):
        self.hp             = self.MAX_HP
        self.stamina        = float(self.MAX_STAMINA)
        self.flasks         = self.MAX_FLASKS
        self.is_dead        = False
        self.death_finished = False
        self.invulnerable   = False
        self.iframe_timer   = 0.0
        self.x              = self.spawn_x
        self.y              = self.spawn_y
        self.vy             = 0.0
        self._cancel_actions()
        self._set_state(State.IDLE)
        # Note: souls_mgr keeps dropped souls in place — player must walk to them

    # ── platform collision ─────────────────────────────────────────────────────
    def _resolve_platforms(self):
        """Aggressive stabilization and fixed ceiling collision"""
        self.y += self.vy
        
        on_ground = False
        pr = self.rect

        for plat in self.platforms:
            if not pr.colliderect(plat):
                continue

            # Landing: Ensure we were falling and previously ABOVE the platform
            if self.vy >= 0 and (pr.bottom - self.vy) <= plat.top + 30:
                self.y = float(plat.top - PLAYER_HEIGHT + self.FOOT_OFFSET)
                self.vy = 0.0
                on_ground = True
                pr = self.rect  # refresh hitbox after snapping to the floor
                continue

            # Ceiling: Ensure we were jumping and previously BELOW the platform
            # This prevents walls you walked into from acting like ceilings!
            elif self.vy < 0 and (pr.top - self.vy) >= plat.bottom - 20:
                ch = int(PLAYER_HEIGHT * 0.75)
                # Correct math to perfectly align your head to the ceiling, NOT teleport you into the void!
                self.y = float(plat.bottom - PLAYER_HEIGHT + ch - self.FOOT_OFFSET)
                self.vy = 0.0
                pr = self.rect  # refresh hitbox after hitting ceiling

        return on_ground
    # ── input ──────────────────────────────────────────────────────────────────
    def handle_event(self, event, keys):
        if event.type != pygame.KEYDOWN:
            return

        # ==================== OTHER INPUTS ====================
        if event.key == pygame.K_SPACE:
            if (self.on_ground or self.coyote_timer > 0) and not self._is_locked():
                self.vy = self.JUMP_FORCE
                self.on_ground = False
                self.coyote_timer = 0.0

        if event.key == pygame.K_q:
            if self.on_ground and not self._is_locked():
                if self._use_stamina(self.STAMINA_ROLL):
                    self._cancel_actions()
                    self._set_state(State.ROLL)
                    self.roll_timer = self.ROLL_DURATION
                    self.invulnerable = True

        if event.key == pygame.K_w:
            self._set_state(State.SHIELD_STRIKE)
        if self.state == State.SHIELD_STRIKE:
            self._use_stamina(self.STAMINA_SHIELD_STRIKE)


        if event.key == pygame.K_j:
            if self._in_combo() and self.state in (State.ATTACK_1, State.ATTACK_2):
                if self.combo_idx < len(self.combo_chain) - 1:
                    self.combo_queued = True
                    if self.combo_buffer_timer > 0:
                        self.combo_buffer_timer = 0.0
                        self._advance_combo()
            elif not self._is_locked():
                if not self.on_ground and self.state == State.JUMP:
                    if self._use_stamina(self.STAMINA_ATTACK):
                        self._set_state(State.JUMP_ATTACK)
                elif self.state == State.RUN:
                    if self._use_stamina(self.STAMINA_ATTACK):
                        self._set_state(State.RUN_ATTACK)
                else:
                    self._start_combo(LIGHT_COMBO)

        if event.key == pygame.K_k:
            if self._in_combo() and self.state == State.POWER_ATK_1:
                self.combo_queued = True
                if self.combo_buffer_timer > 0:
                    self.combo_buffer_timer = 0.0
                    self._advance_combo()
            elif not self._is_locked():
                self._start_combo(HEAVY_COMBO, heavy=True)

        if event.key == pygame.K_f:
            if self.flasks > 0 and not self._is_locked() and self.on_ground:
                self.flasks -= 1
                # ADD THIS LINE: Actually restore the HP!
                self.hp = min(self.MAX_HP, self.hp + self.FLASK_HEAL)
                self._set_state(State.ELIXIR)

        if event.key == pygame.K_t:
            if not self._is_locked() and self.on_ground:
                self._set_state(State.INVOCATION)

        if event.key == pygame.K_e:
            if not self._is_locked() and self.on_ground:
                self._set_state(State.PICK_UP)

    # ── update ─────────────────────────────────────────────────────────────────
    def update(self, dt, keys):
        # iframes
        if self.iframe_timer > 0:
            self.iframe_timer -= dt
            if self.iframe_timer <= 0:
                self.iframe_timer = 0.0
                if self.roll_timer <= 0:
                    self.invulnerable = False

        # stamina regen
        blocking = keys[pygame.K_l] and not self._is_locked()
        if not blocking and self.state not in (State.BLOCK, State.DEFEND):
            self.stamina = min(self.MAX_STAMINA,
                               self.stamina + self.STAMINA_REGEN * dt)

        # dead — physics only, no input
        if self.is_dead:
            self.vy       += self.GRAVITY
            self.on_ground = self._resolve_platforms()
            self._play_sfx(dt)
            self._tick_anim(dt)
            return

        # blocking
        if blocking and self.on_ground and not self._is_locked():
            self._set_state(State.BLOCK)
        elif self.state in (State.BLOCK, State.DEFEND) and not blocking:
            self._set_state(State.IDLE)

        # roll
        if self.roll_timer > 0:
            self.x         += self.ROLL_SPEED * (1 if self.facing_right else -1)
            self.roll_timer -= dt
            if self.roll_timer <= 0:
                self.roll_timer   = 0.0
                self.invulnerable = False
                self._set_state(State.IDLE)

        # run/jump attack momentum
        if self.state == State.RUN_ATTACK:
            self.x += (self.RUN_SPEED * 0.7) * (1 if self.facing_right else -1)
        if self.state == State.JUMP_ATTACK:
            self.x += (self.SPEED * 0.7) * (1 if self.facing_right else -1)

        # combo buffer
        if self.combo_buffer_timer > 0:
            self.combo_buffer_timer -= dt
            if self.combo_buffer_timer <= 0 and not self.combo_queued:
                self._advance_combo()

        # horizontal movement
        is_moving  = False
        is_running = False
        if not self._is_locked() and self.state not in (State.BLOCK, State.DEFEND):
            run   = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            speed = self.RUN_SPEED if run else self.SPEED
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.x           -= speed
                self.facing_right = False
                is_moving         = True
                is_running        = run
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.x           += speed
                self.facing_right = True
                is_moving         = True
                is_running        = run
            if run and is_moving:
                self._use_stamina(self.STAMINA_RUN * 0.06)

        # attack hitbox
        ATTACK_STATES = (
            State.ATTACK_1, State.ATTACK_2, State.ATTACK_3,
            State.RUN_ATTACK, State.JUMP_ATTACK,
            State.POWER_ATK_1, State.POWER_ATK_2,
            State.SHIELD_STRIKE,
        )
        if self.state not in ATTACK_STATES:
            self.hitbox_active = False
            self.attack_damage = 0
        else:
            # Check the dictionary to see if the current frame is a damage frame
            active_range = ACTIVE_HITBOX_FRAMES.get(self.state, (0, 0))
            if active_range[0] <= self.frame_idx <= active_range[1]:
                self.hitbox_active = True
            else:
                self.hitbox_active = False

            # Set the damage
            if self._in_combo():
                self.attack_damage = (20 if self.is_heavy else 10) + self._bonus_damage
            else:
                self.attack_damage = 15 + self._bonus_damage


        # clamp to level
        self.x = max(0.0, min(self.x, LEVEL_W - PLAYER_WIDTH))

        # gravity + platform collision
        self.vy       += self.GRAVITY
        was_grounded   = self.on_ground
        self.on_ground = self._resolve_platforms()

        if was_grounded and not self.on_ground:
            self.coyote_timer = self.COYOTE_TIME
        if self.coyote_timer > 0:
            self.coyote_timer -= dt

                
        # === STATE MACHINE ===
        if not self._is_locked() and self.state not in (State.BLOCK, State.DEFEND):
            if self.state in (State.JUMP_ATTACK, State.RUN_ATTACK, State.RESTING):
                pass  # let special states continue
            elif not self.on_ground:
                self._set_state(State.JUMP)
            elif is_running:
                self._set_state(State.RUN)
            elif is_moving:
                self._set_state(State.WALK)
            else:
                self._set_state(State.IDLE)

        self._tick_anim(dt)
        self._play_sfx(dt)
        self.souls_mgr.update(dt)
        self.x = round(self.x)
        self.y = round(self.y)

    # ── animation tick ─────────────────────────────────────────────────────────
    def _tick_anim(self, dt):
        self.frame_timer += dt
        speed  = ANIM_SPEEDS.get(self.state, 0.10)
        frames = self.animations[self.state]

        if self.frame_timer < speed:
            return
        self.frame_timer -= speed
        next_idx = self.frame_idx + 1

        if self.state == State.DEAD:
            if next_idx >= len(frames):
                self.frame_idx      = len(frames) - 1
                self.death_finished = True
            else:
                self.frame_idx = next_idx
            return

        if self.state in (State.RUN_ATTACK, State.JUMP_ATTACK,
                           State.SHIELD_STRIKE):
            if next_idx >= len(frames):
                self._set_state(
                    State.JUMP if self.state == State.JUMP_ATTACK
                    and not self.on_ground else State.IDLE
                )
            else:
                self.frame_idx = next_idx
            return

        if self.state in ONE_SHOT_STATES:
            if next_idx >= len(frames):
                self._set_state(State.IDLE)
            else:
                self.frame_idx = next_idx
            return

        if self._in_combo():
            _, seg_end = self.combo_chain[self.combo_idx]
            if next_idx > seg_end:
                if self.combo_queued:
                    self._advance_combo()
                elif self.combo_idx < len(self.combo_chain) - 1:
                    if self.combo_buffer_timer <= 0:
                        self.combo_buffer_timer = COMBO_BUFFER
                else:
                    self._advance_combo()
            else:
                self.frame_idx = next_idx
            return

        # Group RESTING with ROLL so they both lock on their final frame!
        if self.state in (State.ROLL, State.RESTING):
            self.frame_idx = min(next_idx, len(frames) - 1)
            return

        self.frame_idx = next_idx % len(frames)
    def _play_sfx(self, dt):
        s = self.state
        prev = self._prev_state

        # ── One-shot on state entry ──────────────────────────────────────
        if s != prev:
            if s == State.JUMP:
                sfx.play("jump", 0.7)
            elif s in (State.HURT,):
                sfx.play("hurt", 0.9)
            elif s == State.ROLL:               # <--- ADD THIS
                sfx.play("roll", 0.8)           # <--- ADD THIS
            elif s == State.RESTING:            # <--- ADD THIS
                sfx.play("resting", 0.8)
            elif s == State.STAND_UP:           # <--- ADD THIS
                sfx.play("stand_up", 0.8)   
            elif s == State.DEAD:
                sfx.play("death", 1.0)
            elif s in (State.BLOCK, State.DEFEND):
                sfx.play("block", 0.8)
            elif s == State.ELIXIR:             # <--- ADD THIS
                sfx.play("heal", 0.9) 
            # Sword swing fires when the attack animation starts
            elif s in (State.ATTACK_1, State.ATTACK_2, State.ATTACK_3,
                    State.RUN_ATTACK, State.JUMP_ATTACK,
                    State.POWER_ATK_1, State.POWER_ATK_2,
                    State.SHIELD_STRIKE):
                sfx.play("sword_swing", 0.75)

        # ── Land on ground ───────────────────────────────────────────────
        if self.on_ground and not self._was_grounded:
            sfx.play("land", 0.8)

        # ── Sword hit — fires the frame hitbox becomes active ────────────
        ATTACK_STATES = (State.ATTACK_1, State.ATTACK_2, State.ATTACK_3,
                        State.RUN_ATTACK, State.JUMP_ATTACK,
                        State.POWER_ATK_1, State.POWER_ATK_2,
                        State.SHIELD_STRIKE)
        if s in ATTACK_STATES and self.hitbox_active and not getattr(self, '_sword_hit_played', False):
            sfx.play("sword_hit", 0.6)
            self._sword_hit_played = True
        if not self.hitbox_active:
            self._sword_hit_played = False

        # ── Footsteps (walk & run, timed so they don't spam) ─────────────
        WALK_INTERVAL = 0.38   # seconds between steps when walking
        RUN_INTERVAL  = 0.22   # seconds between steps when running
        if self.on_ground and s in (State.WALK, State.RUN):
            interval = RUN_INTERVAL if s == State.RUN else WALK_INTERVAL
            self._walk_timer += dt
            if self._walk_timer >= interval:
                self._walk_timer = 0.0
                sfx.play("run" if s == State.RUN else "walk", 0.5)
        else:
            self._walk_timer = 0.0

        # ── Save state for next frame ─────────────────────────────────────
        self._prev_state   = s
        self._was_grounded = self.on_ground

    # ── draw ───────────────────────────────────────────────────────────────────
    def draw(self, surface, camera):
        frames = self.animations.get(self.state, [])
        if not frames:
            return

        idx = max(0, min(self.frame_idx, len(frames) - 1))
        img = frames[idx]

        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)

        # === FIXED FOOT ANCHORING ===
        world_foot_x = int(self.x) + PLAYER_WIDTH // 2
        world_foot_y = int(self.y) + PLAYER_HEIGHT + self.FOOT_OFFSET

        screen_x, screen_y = camera.apply_xy(world_foot_x, world_foot_y)

        img_rect = img.get_rect()
        img_rect.midbottom = (screen_x, screen_y)

        # Animation-specific offsets
        off_x, off_y = ANIM_OFFSETS.get(self.state, (0, 0))
        if not self.facing_right:
            off_x = -off_x

        img_rect.centerx += off_x
        img_rect.bottom  += off_y

        surface.blit(img, img_rect)