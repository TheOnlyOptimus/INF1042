import pygame
import io  # <--- NEW: Python's Memory Streamer

pygame.mixer.pre_init(44100, -16, 2, 4096)
pygame.init()

from settings import (
    WIDTH, HEIGHT, BG_COLOR, LEVEL_W, LEVEL_H,
    PLAYER_WIDTH, PLAYER_HEIGHT, ANIM_MANIFEST,
    FULLSCREEN as FULLSCREEN_SETTING,
    BASE_PATH,
)
import os
from utils    import get_path
from player   import Player
from camera   import Camera
from hud      import HUD, AreaPopup, VictoryPopup
from level    import Area1
from enums    import State
from effects  import EffectManager
from level_up import LevelUpMenu
import sfx
from boss import HoodedKnight

# ── RAM MUSIC CACHE TO DESTROY STUTTERS ──────────────────────────────────────────
_MUSIC_CACHE = {}

def _try_load_music(filename):
    for ext in ("ogg", "mp3", "wav"):
        path = os.path.join(BASE_PATH, "assets", f"{filename}.{ext}")
        if os.path.exists(path):
            return path
    return None

def _get_music_stream(filename):
    """Loads music into RAM exactly once so playback is instant."""
    if filename not in _MUSIC_CACHE:
        path = _try_load_music(filename)
        if path:
            try:
                with open(path, "rb") as f:
                    _MUSIC_CACHE[filename] = f.read()
            except Exception as e:
                print(f"[WARN] Failed to read {filename} to RAM: {e}")
                _MUSIC_CACHE[filename] = None
        else:
            _MUSIC_CACHE[filename] = None
            
    data = _MUSIC_CACHE[filename]
    if data:
        return io.BytesIO(data) # Returns a clean memory stream
    return None

# ── INSTANT AUDIO FUNCTIONS ──────────────────────────────────────────────────
def _start_boss_music():
    stream = _get_music_stream("boss_music")
    if stream:
        try:
            pygame.mixer.music.load(stream)
            pygame.mixer.music.set_volume(0.65)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"[WARN] Could not play boss music: {e}")
    else:
        print("[INFO] No boss_music file found in assets/ — skipping music.")

def _start_phase2_music():
    stream = _get_music_stream("boss_music_phase2")
    if stream:
        try:
            pygame.mixer.music.load(stream)
            pygame.mixer.music.set_volume(0.75)
            pygame.mixer.music.play(-1, fade_ms=1500)
        except Exception as e:
            print(f"[WARN] Could not play phase 2 music: {e}")
    else:
        print("[INFO] No boss_music_phase2 file found — keeping phase 1 music.")

def _start_bonfire_music():
    stream = _get_music_stream("bonfire_music")
    if stream:
        try:
            pygame.mixer.music.load(stream)
            pygame.mixer.music.set_volume(0.50)  
            pygame.mixer.music.play(-1, fade_ms=1000)
        except Exception as e:
            print(f"[WARN] Could not play bonfire music: {e}")
    else:
        print("[INFO] No bonfire_music file found in assets/ — skipping music.")

def _start_ambient_music():
    stream = _get_music_stream("ambient_music")
    if stream:
        try:
            pygame.mixer.music.load(stream)
            pygame.mixer.music.set_volume(0.40)  
            pygame.mixer.music.play(-1, fade_ms=1500)
        except Exception as e:
            print(f"[WARN] Could not play ambient music: {e}")
    else:
        print("[INFO] No ambient_music file found in assets/ — skipping music.")

def _stop_music():
    try:
        pygame.mixer.music.fadeout(1500)
    except Exception:
        pass


class LockOn:
    INDICATOR_RADIUS = 20
    INDICATOR_COLOR  = (255, 255, 255)
    INDICATOR_WIDTH  = 2

    BASE_OFFSET_X = 0  
    BASE_OFFSET_Y = 0

    ANIM_OFFSETS = {
        "attack_1": (60, 0),  
        "attack_2": (40, 0),
        "walk":     (15, 0),
        "phase_transition": (0, 0),
    }

    def __init__(self):
        self.active      = False
        self._pulse      = 0.0   

    def update(self, dt, boss_fight_active, boss_dead):
        if boss_fight_active and not boss_dead:
            self.active   = True
            self._pulse  += dt * 3.0
        else:
            self.active   = False
            self._pulse   = 0.0

    def camera_target(self, player, boss):
        if not self.active:
            return player.rect.centerx, player.rect.centery

        px = player.rect.centerx
        py = player.rect.centery
        bx = boss.rect.centerx
        by = boss.rect.centery
        return int(px * 0.6 + bx * 0.4), int(py * 0.6 + by * 0.4)

    def draw(self, surface, camera, boss):
        if not self.active:
            return
            
        bx = boss.rect.centerx
        by = boss.rect.centery
        
        off_x = self.BASE_OFFSET_X
        off_y = self.BASE_OFFSET_Y

        anim_x, anim_y = self.ANIM_OFFSETS.get(boss.state, (0, 0))
        off_x += anim_x
        off_y += anim_y

        if not boss.facing_right:
            off_x = -off_x

        sx, sy = camera.apply_xy(bx + off_x, by + off_y)

        r = self.INDICATOR_RADIUS + int(3 * abs(pygame.math.Vector2(0, 1).rotate(self._pulse * 30).y))

        pts = [
            (sx,     sy - r),
            (sx + r, sy    ),
            (sx,     sy + r),
            (sx - r, sy    ),
        ]
        


def main():
    info = pygame.display.Info()
    monitor_w, monitor_h = info.current_w, info.current_h
    fullscreen = FULLSCREEN_SETTING

    if fullscreen:
        screen = pygame.display.set_mode((monitor_w, monitor_h), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))

    pygame.display.set_caption("Pixel Souls")
    clock           = pygame.time.Clock()
    virtual_surface = pygame.Surface((WIDTH, HEIGHT))

    area      = Area1()
    platforms = area.get_platforms()
    enemies   = area.get_enemies()
    boss      = area.get_boss()
    fog_gate  = area.get_fog_gate()
    effects   = EffectManager()
    lock_on   = LockOn()
    lvl_menu = LevelUpMenu()

    floor  = platforms[0]
    player = Player(platforms, spawn_x=300, spawn_y=floor.top - PLAYER_HEIGHT)

    camera = Camera()
    hud    = HUD()
    area_popup    = AreaPopup()
    victory_popup = VictoryPopup()
    debug_hitboxes = False
    _start_ambient_music()
    area_popup.show("Ashen Ruins")   # shown on first load

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if lvl_menu.open:
                # If the menu is open, it eats the inputs (blocks jumping, attacking, etc.)
                if lvl_menu.handle_event(event, player.souls_mgr, player):
                    continue
            else:
                # If closed, check if they are pressing L while resting
                if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                    if player.state == State.RESTING:
                        lvl_menu.toggle()
                        continue
                        

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((monitor_w, monitor_h), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))

            player.handle_event(event, pygame.key.get_pressed())

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                if player.is_dead and player.death_finished:
                    player.respawn()
                    camera.x = player.x + PLAYER_WIDTH // 2 - WIDTH // 2
                    camera.y = player.y + PLAYER_HEIGHT // 2 - HEIGHT // 2
                    
                    area._build_enemies()
                    enemies = area.get_enemies()
                    if not boss.death_done:
                        area._build_boss()
                        area._build_fog_gate()
                        fog_gate = area.get_fog_gate()
                    boss = area.get_boss()
                    effects.reset()
                    victory_popup.reset()
                    area_popup.show("Ashen Ruins")
                    _start_ambient_music()

                elif player.state == State.RESTING:
                    player._set_state(State.STAND_UP)
                    _start_ambient_music()  

                elif not player.is_dead and not player._is_locked():
                    if fog_gate.try_traverse(player.rect):
                        pass   
                    else:
                        bf = area.check_bonfire(
                            player.x + PLAYER_WIDTH  // 2,
                            player.y + PLAYER_HEIGHT // 2,
                        )
                        if bf:
                            area.activate_bonfire(bf, player)
                            player._set_state(State.RESTING)
                            sfx.play("bonfire", volume=0.75)
                            _start_bonfire_music()  
                            
                            area._build_enemies()
                            enemies = area.get_enemies()
                            if not boss.death_done:
                                area._build_boss()
                                boss = area.get_boss()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                debug_hitboxes = not debug_hitboxes

        keys = pygame.key.get_pressed()
        player.update(dt, keys)

        # ── SOLID ENEMY & BOSS COLLISION ──
        if player.state != State.ROLL:
            for enemy in enemies:
                if not enemy.is_dead:
                    if player.rect.colliderect(enemy.rect):
                        if player.rect.centerx < enemy.rect.centerx:
                            overlap = player.rect.right - enemy.rect.left
                            player.x -= overlap * 0.5   
                            enemy.x  += overlap * 0.1   
                        else:
                            overlap = enemy.rect.right - player.rect.left
                            player.x += overlap * 0.5
                            enemy.x  -= overlap * 0.1

            if boss.fight_active and not boss.is_dead:
                if player.rect.colliderect(boss.rect):
                    if player.rect.centerx < boss.rect.centerx:
                        overlap = player.rect.right - boss.rect.left
                        player.x -= overlap
                    else:
                        overlap = boss.rect.right - player.rect.left
                        player.x += overlap

        # ── FOG GATE ──────────────────────────────────────────────────────────
        fog_gate.push_player(player)

        if fog_gate.check_player_entered(player.rect):
            boss.fight_active = True
            sfx.play("fog_gate", volume=0.85)
            _start_boss_music()

        fog_gate.update(dt, boss_dead=boss.death_done)
        lock_on.update(dt, boss.fight_active, boss.death_done)

        player_hitbox = player._get_attack_hitbox()
        
        # Normal enemies
        for enemy in enemies:
            if enemy.death_done:
                continue
            enemy.update(dt, player)
            if player_hitbox and player.hitbox_active and player_hitbox.colliderect(enemy.rect):
                enemy.take_damage(player.attack_damage, knockback_right=player.facing_right)

            # ── Soul drop ──────────────────────────────────────────────────
            if enemy._pending_soul_drop:
                enemy._pending_soul_drop = False
                player.souls_mgr.add_souls(enemy.SOUL_DROP)
                

        # Boss
        if not boss.death_done and effects.death_effect is None:
            boss.update(dt, player)
            
            if getattr(boss, '_start_fadeout', False):
                boss._start_fadeout = False
                pygame.mixer.music.fadeout(1200)
                
            if getattr(boss, '_phase2_music_needed', False):
                boss._phase2_music_needed = False
                _start_phase2_music()
                
            if player_hitbox and player.hitbox_active:
                if player_hitbox.colliderect(boss.rect):
                    was_alive = not boss.is_dead
                    boss.take_damage(player.attack_damage, knockback_right=player.facing_right)
                    effects.spawn_hit(boss.rect.centerx, boss.rect.centery)
                    
                    if was_alive and boss.is_dead:
                        effects.spawn_boss_death(boss)
                        sfx.play("boss_death", volume=1.0)
                        _stop_music()

            # ── Boss soul drop ─────────────────────────────────────────────
            if boss._pending_soul_drop:
                boss._pending_soul_drop = False
                player.souls_mgr.add_souls(boss.SOUL_DROP)

        effects.update(dt)
        lvl_menu.update(dt)
        area_popup.update(dt)
        victory_popup.update(dt)

        # ── Victory popup — fires once when the death explosion finishes ──
        if effects.boss_death_done:
            victory_popup.trigger()

        # ── Return Ambiance after Boss Explosion ──
        if effects.boss_death_done and not getattr(boss, '_ambient_restored', False):
            boss._ambient_restored = True
            _start_ambient_music()

        # ── Spawn victory bonfire once the victory popup has fully faded ──
        if (effects.boss_death_done
                and not getattr(boss, '_bonfire_spawned', False)
                and not victory_popup.active):
            boss._bonfire_spawned = True
            area.spawn_victory_bonfire()

        for bf in area.get_bonfires():
            if hasattr(bf, 'update'):
                bf.update(dt)

        cam_cx, cam_cy = lock_on.camera_target(player, boss)
        camera.update(cam_cx, cam_cy)

        virtual_surface.fill(BG_COLOR)

        area.draw_background(virtual_surface, camera)
        area.draw_decorations(virtual_surface, camera)
        area.draw_platforms(virtual_surface, camera)
        area.draw_bonfires(virtual_surface, camera)

        area.draw_fog_gate(virtual_surface, camera, player.rect)
        fog_gate.draw_prompt(virtual_surface, camera, player.rect)

        for enemy in enemies:
            enemy.draw(virtual_surface, camera)

        if effects.death_effect is None and not boss.death_done:
            area.draw_boss(virtual_surface, camera)

        player.draw(virtual_surface, camera)

        bf_near = area.check_bonfire(
            player.x + PLAYER_WIDTH  // 2,
            player.y + PLAYER_HEIGHT // 2,
        )
        if bf_near and not player.is_dead:
            bf_near.draw_prompt(virtual_surface, player)

        effects.draw(virtual_surface, camera)

        # ── Soul drop orb (world-space, drawn before HUD) ─────────────────
        hud.draw_soul_orb(virtual_surface, camera, player)

        # ── Collect dropped souls on contact ─────────────────────────────
        if not player.is_dead and player.souls_mgr.has_dropped_souls and player._soul_drop_x is not None:
            orb_rect = pygame.Rect(player._soul_drop_x - 30, player._soul_drop_y - 30, 60, 60)
            if player.rect.colliderect(orb_rect):
                player.souls_mgr.try_collect_dropped(player.rect, orb_rect)
                player._soul_drop_x = None
                player._soul_drop_y = None

        if not boss.death_done:
            lock_on.draw(virtual_surface, camera, boss)

        hud.draw(virtual_surface, player)
        boss.draw_hud(virtual_surface)
        effects.draw_flash(virtual_surface)
        lvl_menu.draw(virtual_surface, player.souls_mgr)
        area_popup.draw(virtual_surface)
        victory_popup.draw(virtual_surface)

        if debug_hitboxes:
            def _draw_rect_world(rect, color, label=""):
                sr = camera.apply(rect)
                pygame.draw.rect(virtual_surface, color, sr, 2)
                if label:
                    lbl = pygame.font.SysFont("Arial", 11).render(label, True, color)
                    virtual_surface.blit(lbl, (sr.x, sr.y - 13))

            _draw_rect_world(player.rect, (0, 255, 0), "P.body")

            ph = player._get_attack_hitbox()
            if ph:
                _draw_rect_world(ph, (255, 255, 0), "P.sword")

            _draw_rect_world(boss.rect, (255, 80, 80), "B.body")

            bh = boss.attack_hitbox
            if bh:
                _draw_rect_world(bh, (255, 140, 0), "B.melee")

            for en in enemies:
                if not en.death_done:
                    _draw_rect_world(en.rect, (180, 0, 255), "E")

            _draw_rect_world(fog_gate.rect,
                             (0, 200, 255) if not fog_gate.is_wall else (255, 60, 60),
                             "Gate")

        if fullscreen:
            scale_x = monitor_w / WIDTH
            scale_y = monitor_h / HEIGHT
            scale   = min(scale_x, scale_y)
            new_w   = int(WIDTH  * scale)
            new_h   = int(HEIGHT * scale)
            scaled  = pygame.transform.smoothscale(virtual_surface, (new_w, new_h))
            off_x   = (monitor_w - new_w) // 2
            off_y   = (monitor_h - new_h) // 2
            screen.fill((0, 0, 0))
            screen.blit(scaled, (off_x, off_y))
        else:
            screen.blit(virtual_surface, (0, 0))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()