import pygame
from enums import State
from utils import load_animation
from settings import (
    WIDTH, SPRITE_SCALE, GROUND_Y, ANIM_MANIFEST, ANIM_SPEEDS, 
    LIGHT_COMBO, HEAVY_COMBO, COMBO_BUFFER, PLAYER_HEIGHT, PLAYER_WIDTH, ANIM_OFFSETS
)

class Player:
    GRAVITY       = 0.7
    JUMP_FORCE    = -14
    SPEED         = 5
    RUN_SPEED     = 9
    COYOTE_TIME   = 0.10

    MAX_HP        = 100
    MAX_STAMINA   = 100
    MAX_FLASKS    = 5
    FLASK_HEAL    = 40

    IFRAMES_HIT   = 0.7
    HIT_KNOCKBACK = 10

    ROLL_DURATION = 0.45
    ROLL_SPEED    = 11

    STAMINA_REGEN         = 15
    STAMINA_ROLL          = 25
    STAMINA_ATTACK        = 20
    STAMINA_HEAVY         = 30
    STAMINA_SHIELD_STRIKE = 20
    STAMINA_BLOCK_DRAIN   = 10
    STAMINA_RUN           = 10
    FOOT_OFFSET           = -7

    def __init__(self):
        self.x     = WIDTH // 2.0
        self.y     = float(GROUND_Y - PLAYER_HEIGHT + self.FOOT_OFFSET)
        self.spawn_x = self.x
        self.spawn_y = self.y

        self.vy            = 0.0
        self.facing_right  = True
        self.on_ground     = False
        self.coyote_timer  = 0.0

        self.hp            = self.MAX_HP
        self.stamina       = float(self.MAX_STAMINA)
        self.flasks        = self.MAX_FLASKS
        self.is_dead       = False
        self.death_finished = False

        self.invulnerable  = False
        self.iframe_timer  = 0.0

        self.roll_timer    = 0.0

        self.combo_chain   =[]
        self.combo_idx     = -1
        self.combo_queued  = False
        self.combo_buffer_timer = 0.0
        self.is_heavy      = False

        self.hitbox_active  = False
        self.attack_damage  = 0

        self.state       = State.IDLE
        self.frame_idx   = 0
        self.frame_timer = 0.0

        self.animations = {}
        for state, (folder_name, frame_count) in ANIM_MANIFEST.items():
            self.animations[state] = load_animation(folder_name, frame_count, SPRITE_SCALE)

    def _set_state(self, s):
        if self.state != s:
            self.state       = s
            self.frame_idx   = 0
            self.frame_timer = 0.0

    def _is_locked(self):
        return self.state in (
            State.ROLL, State.HURT, State.DEAD,
            State.ATTACK_1, State.ATTACK_2, State.ATTACK_3,
            State.RUN_ATTACK, State.JUMP_ATTACK,
            State.POWER_ATK_1, State.POWER_ATK_2,
            State.SHIELD_STRIKE,
            State.PULL_UP, State.ELIXIR, State.PICK_UP,
            State.INVOCATION, 
        )

    def _use_stamina(self, amount):
        if self.stamina < amount:
            return False
        self.stamina -= amount
        return True

    def _get_attack_hitbox(self):
        if not self.hitbox_active:
            return None
        hw, hh = PLAYER_WIDTH // 2, PLAYER_HEIGHT // 4
        if self.facing_right:
            hx = int(self.x) + PLAYER_WIDTH - 20
        else:
            hx = int(self.x) - hw + 20
        hy = int(self.y) + PLAYER_HEIGHT // 3
        return pygame.Rect(hx, hy, hw, hh)

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
        self.combo_chain        =[]
        self.combo_idx          = -1
        self.combo_queued       = False
        self.combo_buffer_timer = 0.0
        self.hitbox_active      = False
        self._set_state(State.IDLE)

    def _in_combo(self):
        return self.combo_idx >= 0 and self.combo_chain

    def take_damage(self, amount, knockback_right=True):
        if self.invulnerable or self.is_dead:
            return

        if self.state in (State.BLOCK, State.DEFEND):
            self._use_stamina(self.STAMINA_BLOCK_DRAIN)

        self.hp -= amount
        self._cancel_actions()

        if self.hp <= 0:
            self.hp    = 0
            self.is_dead = True
            self._set_state(State.DEAD)
        else:
            self._set_state(State.HURT)
            self.x += self.HIT_KNOCKBACK * (1 if knockback_right else -1)

        self.invulnerable = True
        self.iframe_timer = self.IFRAMES_HIT

    def _cancel_actions(self):
        self.roll_timer         = 0.0
        self.combo_chain        =[]
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

    def _resolve_ground(self):
        self.y += self.vy
        on_ground = False
        if self.y + PLAYER_HEIGHT - self.FOOT_OFFSET >= GROUND_Y:
            if self.vy >= 0:
                self.y    = float(GROUND_Y - PLAYER_HEIGHT + self.FOOT_OFFSET)
                self.vy   = 0.0
                on_ground = True
        return on_ground

    def handle_event(self, event, keys):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_r and self.is_dead and self.death_finished:
            self.respawn()
            return

        if self.is_dead:
            return

        if event.key == pygame.K_SPACE:
            if (self.on_ground or self.coyote_timer > 0) and not self._is_locked():
                self.vy           = self.JUMP_FORCE
                self.on_ground    = False
                self.coyote_timer = 0.0

        if event.key == pygame.K_q:
            if self.on_ground and not self._is_locked():
                if self._use_stamina(self.STAMINA_ROLL):
                    self._cancel_actions()
                    self._set_state(State.ROLL)
                    self.roll_timer   = self.ROLL_DURATION
                    self.invulnerable = True

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

        if event.key == pygame.K_l:
            if self.state in (State.BLOCK, State.DEFEND):
                self._use_stamina(self.STAMINA_BLOCK_DRAIN)

        if event.key == pygame.K_w:
            self._set_state(State.SHIELD_STRIKE)
        if self.state == State.SHIELD_STRIKE:
            self._use_stamina(self.STAMINA_SHIELD_STRIKE)

        if event.key == pygame.K_f:
            if self.flasks > 0 and not self._is_locked() and self.on_ground:
                self.flasks -= 1
                self._set_state(State.ELIXIR)

        if event.key == pygame.K_t:
            if not self._is_locked() and self.on_ground:
                self._set_state(State.INVOCATION)

        if event.key == pygame.K_e:
            if not self._is_locked() and self.on_ground:
                self._set_state(State.PICK_UP)

    def update(self, dt, keys):
        if self.iframe_timer > 0:
            self.iframe_timer -= dt
            if self.iframe_timer <= 0:
                self.iframe_timer = 0.0
                if self.roll_timer <= 0:
                    self.invulnerable = False

        blocking = keys[pygame.K_l] and not self._is_locked()
        if not blocking and self.state not in (State.BLOCK, State.DEFEND):
            self.stamina = min(self.MAX_STAMINA, self.stamina + self.STAMINA_REGEN * dt)

        if self.is_dead:
            self.vy       += self.GRAVITY
            self.on_ground = self._resolve_ground()
            self._tick_anim(dt)
            return

        if blocking and self.on_ground and not self._is_locked():
            self._set_state(State.DEFEND if self.state == State.DEFEND else State.BLOCK)
        elif self.state in (State.BLOCK, State.DEFEND) and not blocking:
            self._set_state(State.IDLE)

        if self.roll_timer > 0:
            self.x         += self.ROLL_SPEED * (1 if self.facing_right else -1)
            self.roll_timer -= dt
            if self.roll_timer <= 0:
                self.roll_timer   = 0.0
                self.invulnerable = False
                self._set_state(State.IDLE)
                
        if self.state == State.RUN_ATTACK:
            self.x += (self.RUN_SPEED * 0.7) * (1 if self.facing_right else -1)
            
        if self.state == State.JUMP_ATTACK:
            self.x += (self.SPEED * 0.7) * (1 if self.facing_right else -1)

        if self.combo_buffer_timer > 0:
            self.combo_buffer_timer -= dt
            if self.combo_buffer_timer <= 0:
                if not self.combo_queued:
                    self._advance_combo()

        is_moving = False
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
            if self.state == State.RUN:
                self._use_stamina(self.STAMINA_RUN * 0.07)

        if self._in_combo():
            _, seg_end = self.combo_chain[self.combo_idx]
            mid_start  = max(0, seg_end // 3)
            mid_end    = seg_end * 2 // 3
            self.hitbox_active = mid_start <= self.frame_idx <= mid_end
            self.attack_damage = 20 if self.is_heavy else 10
        elif self.state in (State.RUN_ATTACK, State.JUMP_ATTACK, State.SHIELD_STRIKE):
            frames     = self.animations[self.state]
            mid        = len(frames) // 2
            self.hitbox_active = abs(self.frame_idx - mid) <= 1
            self.attack_damage = 15
        else:
            self.hitbox_active = False

        self.vy       += self.GRAVITY
        was_grounded   = self.on_ground
        self.on_ground = self._resolve_ground()

        if was_grounded and not self.on_ground:
            self.coyote_timer = self.COYOTE_TIME
        if self.coyote_timer > 0:
            self.coyote_timer -= dt

        # Prevent jumping out of attack animations prematurely
        if not self._is_locked() and self.state not in (State.BLOCK, State.DEFEND):
            if self.state == State.JUMP_ATTACK and not self.on_ground:
                pass  # let it finish naturally
            elif not self.on_ground:
                self._set_state(State.JUMP)
            elif is_running:
                self._set_state(State.RUN)
            elif is_moving:
                self._set_state(State.WALK)
            else:
                self._set_state(State.IDLE)

        self._tick_anim(dt)
        self.x = round(self.x)
        self.y = round(self.y)
        

    def _tick_anim(self, dt):
        self.frame_timer += dt
        speed = ANIM_SPEEDS.get(self.state, 0.10)
        frames = self.animations[self.state]

        if self.frame_timer < speed:
            return

        self.frame_timer -= speed
        next_idx = self.frame_idx + 1

        # === DEAD ===
        if self.state == State.DEAD:
            if next_idx >= len(frames):
                self.frame_idx = len(frames) - 1
                self.death_finished = True
            else:
                self.frame_idx = next_idx
            return

        # === ONE-SHOT ATTACKS THAT SHOULD RETURN TO IDLE / JUMP ===
        if self.state in (State.RUN_ATTACK, State.JUMP_ATTACK, State.SHIELD_STRIKE):
            if next_idx >= len(frames):
                if self.state == State.JUMP_ATTACK and not self.on_ground:
                    self._set_state(State.JUMP)
                else:
                    self._set_state(State.IDLE)
                return
            else:
                self.frame_idx = next_idx
                return

        # === OTHER ONE-SHOT ANIMATIONS ===
        if self.state in (State.HURT, State.PULL_UP, State.ELIXIR,
                          State.PICK_UP, State.INVOCATION):
            if next_idx >= len(frames):
                self._set_state(State.IDLE)
            else:
                self.frame_idx = next_idx
            return

        # === COMBO SYSTEM ===
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

        # === ROLL ===
        if self.state == State.ROLL:
            self.frame_idx = min(next_idx, len(frames) - 1)
            return

        # === LOOPING ANIMATIONS (Idle, Walk, Run, etc.) ===
        self.frame_idx = next_idx % len(frames)

    def draw(self, surface, camera):
        frames = self.animations.get(self.state, [])
        if not frames:
            return

        idx = max(0, min(self.frame_idx, len(frames) - 1))
        img = frames[idx]
    
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)

        foot_x = int(self.x) + (PLAYER_WIDTH // 2) - int(camera.x)
        foot_y = int(self.y) + PLAYER_HEIGHT - int(camera.y)

        img_rect = img.get_rect()
        img_rect.midbottom = (foot_x, foot_y)

        off_x, off_y = ANIM_OFFSETS.get(self.state, (0, 0))
        if not self.facing_right:
            off_x = -off_x
            
        img_rect.centerx += off_x
        img_rect.bottom  += off_y

        surface.blit(img, img_rect)