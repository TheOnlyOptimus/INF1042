"""
level.py — Area 1: Ashen Ruins

Tile files expected in:  assets/tiles/
    sprite-1-1.png  (94×128  large wall block)
    sprite-1-2.png  (30×32   small corner)
    sprite-1-3.png  (62×32   medium platform top)
    sprite-1-4.png  (126×32  wide platform top)
    sprite-1-5.png  (30×32   small edge)
    sprite-1-6.png  (30×64   tall pillar)
    sprite-1-7.png  (64×64   square block)
    sprite-2-1.png  (94×32   wide flat)
    sprite-2-2.png  (64×32   medium flat)
    sprite-3-1.png  (32×44   decoration)

Background layers expected in:  assets/
    Background.png, Sun.png, Clouds.png,
    Forest01.png … Forest05.png,
    Castle.png, Giants.png,
    Tree01.png … Tree04.png,
    Grass01.png, Grass02.png,
    bonfire.png
"""

import pygame
import os
from settings import (
    WIDTH, HEIGHT, LEVEL_W, LEVEL_H,
    SPRITE_SCALE, BASE_PATH,
)
from camera import Camera
from utils import load_animation
from enums import State
from enemies import SkeletonSword, SkeletonKnight, Archer
from boss import HoodedKnight
import math  # kept for any future use
import random


ASSETS      = os.path.join(BASE_PATH, "assets")
TILES_DIR   = os.path.join(ASSETS, "tiles")

# ── TILE SCALE ────────────────────────────────────────────────────────────────
TILE_SCALE  = SPRITE_SCALE   # 4×
SPR_H = 128 * SPRITE_SCALE   # 512px — enemy sprite height, same as player


def _load(rel_path, scale_to=None):
    full = os.path.join(ASSETS, rel_path)
    try:
        img = pygame.image.load(full).convert_alpha()
        if scale_to:
            img = pygame.transform.scale(img, scale_to)
        return img
    except pygame.error:
        print(f"[WARN] missing asset: {full}")
        w, h = scale_to if scale_to else (64, 64)
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill((200, 0, 200, 120))
        return s


def _load_tile(filename):
    full = os.path.join(TILES_DIR, filename)
    try:
        img = pygame.image.load(full).convert_alpha()
        w   = img.get_width()  * TILE_SCALE
        h   = img.get_height() * TILE_SCALE
        return pygame.transform.scale(img, (w, h))
    except pygame.error:
        print(f"[WARN] missing tile: {full}")
        s = pygame.Surface((128, 32), pygame.SRCALPHA)
        s.fill((100, 80, 60, 200))
        return s


# ── BONFIRE ───────────────────────────────────────────────────────────────────
class Bonfire:
    INTERACT_DIST = 160

    def __init__(self, world_x, floor_y):
        self.world_x = world_x
        self.world_y = floor_y - 210
        self.rect = pygame.Rect(self.world_x - 30, self.world_y, 180, 200)

        try:
            self.frames = load_animation("Bonfire", 9, scale=1)
        except Exception as e:
            self.frames = []
            print(f"[WARN] Could not load Bonfire animation: {e}")

        self.frame_idx = 0
        self.frame_timer = 0.0

        self.prompt_font = pygame.font.SysFont("Georgia", 18, bold=True)

    def update(self, dt):
        if self.frames:
            self.frame_timer += dt
            if self.frame_timer > 0.10:
                self.frame_timer = 0
                self.frame_idx = (self.frame_idx + 1) % len(self.frames)

    def near_player(self, player_x, player_y):
        cx = self.world_x + 60
        cy = self.world_y + 100
        return abs(player_x - cx) < self.INTERACT_DIST and abs(player_y - cy) < self.INTERACT_DIST

    def draw(self, surface, camera):
        sx, sy = camera.apply_xy(self.world_x, self.world_y)
        if self.frames:
            img = self.frames[self.frame_idx]
            surface.blit(img, (sx, sy))
        else:
            pygame.draw.rect(surface, (255, 140, 0), (sx, sy, 120, 160))

    def draw_prompt(self, surface, player):
        if player.state == State.RESTING:
            txt1 = self.prompt_font.render("Press  R  to  Stand  Up", True, (220, 200, 100))
            txt2 = self.prompt_font.render("Press  L  to  Level  Up", True, (180, 220, 100))
            
            # Stack the texts on top of each other
            surface.blit(txt1, (WIDTH // 2 - txt1.get_width() // 2, HEIGHT - 170))
            surface.blit(txt2, (WIDTH // 2 - txt2.get_width() // 2, HEIGHT - 140))
        else:
            txt = self.prompt_font.render("Press  R  to  Rest", True, (220, 180, 80))
            surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT - 140))

class FogGate:
    GATE_W        = 60
    GATE_H        = 900        # taller than the level — nothing can jump over
    PROMPT_DIST   = 260        # px — show prompt within this distance
    OPEN_DURATION = 1.8        # seconds the gate stays passable after R press

    _N_PARTICLES  = 80
    _COLORS_WALL  = [(100, 160, 255), (130, 190, 255), (80, 130, 220)]
    _COLORS_OPEN  = [(200, 240, 255), (220, 255, 255), (180, 220, 255)]
    _COLORS_SEAL  = [(200, 60, 20),   (220, 90, 0),    (180, 30, 10)]

    def __init__(self, world_x, floor_y, gate_height=None):
        self.world_x  = world_x
        self.floor_y  = floor_y

        # Three states: "wall" → "open" → "sealed"
        self._state      = "wall"
        self._open_timer = 0.0

        # Collision rect — always the same size regardless of state
        self.rect = pygame.Rect(
            world_x,
            floor_y - self.GATE_H,
            self.GATE_W,
            self.GATE_H,
        )
        # Keep trigger as alias for rect so existing main.py refs still work
        self.trigger = self.rect

        # Particles
        rng = random.Random(42)
        self._particles = [
            [
                rng.randint(0, self.GATE_W),          # x offset
                rng.uniform(floor_y - self.GATE_H, floor_y),  # y
                rng.uniform(40, 160),                 # speed
                rng.randint(0, 2),                    # color index
                rng.randint(2, 5),                    # size
            ]
            for _ in range(self._N_PARTICLES)
        ]

        self._font = pygame.font.SysFont("Georgia", 20, bold=True)

    # ── state helpers ─────────────────────────────────────────────────────────
    @property
    def is_wall(self):
        return self._state in ("wall", "sealed")

    def push_player(self, player):
        """
        Solid wall collision — push player back on both sides.
        Call every frame. No-op when gate is open.
        """
        if not self.is_wall:
            return

    @property
    def crossed(self):
        """Backwards-compat alias — True once the fight has started."""
        return self._state == "sealed"

    # ── public actions ────────────────────────────────────────────────────────
    def try_traverse(self, player_rect):
        """
        Called when the player presses R.
        Opens the gate if they are close enough and it is currently a wall.
        Returns True if the gate opened.
        """
        if self._state != "wall":
            return False
        dist = abs(player_rect.centerx - (self.world_x + self.GATE_W // 2))
        if dist > self.PROMPT_DIST:
            return False
        self._state      = "open"
        self._open_timer = self.OPEN_DURATION
        return True

    def check_player_entered(self, player_rect):
        """
        Returns True the frame the player walks through while open.
        Seals the gate immediately.
        """
        if self._state != "open":
            return False
        if player_rect.centerx > self.rect.right:
            self._state = "sealed"
            return True
        return False

    def push_player(self, player):
        """
        Solid wall collision — push player back on both sides.
        Call every frame. No-op when gate is open.
        """
        if not self.is_wall:
            return
        if not player.rect.colliderect(self.rect):
            return
        if player.rect.centerx < self.rect.centerx:
            overlap   = player.rect.right - self.rect.left
            player.x -= overlap
        else:
            overlap   = self.rect.right - player.rect.left
            player.x += overlap

    def is_near(self, player_rect):
        return (self._state == "wall" and
                abs(player_rect.centerx - (self.world_x + self.GATE_W // 2)) < self.PROMPT_DIST)

    def unlock(self):
        self._state = "gone"

    # ── update ────────────────────────────────────────────────────────────────
    def update(self, dt, boss_dead=False):
        # Tick particles
        for p in self._particles:
            p[1] -= p[2] * dt
            if p[1] < self.floor_y - self.GATE_H:
                p[1] = float(self.floor_y)

        # Unlock permanently when boss is dead
        if boss_dead and self._state in ("sealed", "open", "wall", "gone"):
            self.unlock()

        # Count down open timer
        if self._state == "open":
            self._open_timer -= dt
            if self._open_timer <= 0:
                self._state = "wall"   # timed out — reseal

    # ── draw ─────────────────────────────────────────────────────────────────
    def draw(self, surface, camera):
        sx, _ = camera.apply_xy(self.world_x, 0)
        cam_y = int(camera.y)
        if self._state == "gone":
            return
        # Choose color palette based on state
        if self._state == "sealed":
            colors = self._COLORS_SEAL
        elif self._state == "open":
            colors = self._COLORS_OPEN
        else:
            colors = self._COLORS_WALL

        gate_surf = pygame.Surface((self.GATE_W, HEIGHT), pygame.SRCALPHA)

        # Background tint
        tint = (60, 0, 0, 50) if self._state == "sealed" else (0, 20, 60, 45)
        gate_surf.fill(tint)

        # Particles
        for p in self._particles:
            py = int(p[1]) - cam_y
            if 0 <= py < HEIGHT:
                color = colors[p[3] % len(colors)]
                pygame.draw.circle(gate_surf, (*color, 180), (int(p[0]), py), p[4])

        surface.blit(gate_surf, (sx, 0))

        # Edge lines
        edge_c = (80, 20, 20) if self._state == "sealed" else (80, 120, 200)
        pygame.draw.line(surface, edge_c, (sx, 0), (sx, HEIGHT), 2)
        pygame.draw.line(surface, edge_c, (sx + self.GATE_W, 0),
                         (sx + self.GATE_W, HEIGHT), 2)

    def draw_prompt(self, surface, camera, player_rect):
        """Show traverse prompt when player is close and gate is a wall."""
        if self._state == "gone":
            return
        if not self.is_near(player_rect):
            return
        txt = self._font.render(
            "Traverse The Fog  ( R )", True, (220, 185, 100)
        )
        surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT - 140))


# ── AREA / PLATFORM / DECORATION ─────────────────────────────────────────────
class Platform:
    def __init__(self, world_x, world_y, tile_img, tile_count=1):
        tw          = tile_img.get_width()
        th          = tile_img.get_height()
        self.rect   = pygame.Rect(world_x, world_y, tw * tile_count, th)
        self.img    = tile_img
        self.count  = tile_count

    def draw(self, surface, camera):
        tw  = self.img.get_width()
        sy  = self.rect.y - int(camera.y)
        for i in range(self.count):
            sx = self.rect.x + i * tw - int(camera.x)
            if sx + tw < 0 or sx > WIDTH:
                continue
            surface.blit(self.img, (sx, sy))


class Decoration:
    def __init__(self, world_x, world_y, img):
        self.world_x = world_x
        self.world_y = world_y
        self.img     = img

    def draw(self, surface, camera):
        sx = self.world_x - int(camera.x)
        sy = self.world_y - int(camera.y)
        if sx + self.img.get_width() < 0 or sx > WIDTH:
            return
        surface.blit(self.img, (sx, sy))


class ParallaxLayer:
    def __init__(self, img, speed_x, speed_y=0.0, y_offset=0):
        self.img      = img
        self.speed_x  = speed_x   
        self.speed_y  = speed_y
        self.y_offset = y_offset

    def draw(self, surface, camera):
        ox  = int(camera.x * self.speed_x)
        oy  = int(camera.y * self.speed_y)
        iw  = self.img.get_width()
        ih  = self.img.get_height()
        start_x = -(ox % iw)
        x = start_x
        while x < WIDTH:
            surface.blit(self.img, (x, self.y_offset - oy))
            x += iw


# ── AREA 1 ────────────────────────────────────────────────────────────────────
class Area1:
    FLOOR_Y = LEVEL_H - 100
    FOG_GATE_X = 9235

    def __init__(self):
        self._load_tiles()
        self._load_backgrounds()
        self._build_platforms()
        self._build_decorations()
        self._build_bonfires()
        self._build_enemies()
        self._build_boss()  
        self._build_fog_gate()

    def _load_tiles(self):
        self.t = {
            "wide":   _load_tile("sprite-1-4.png"),   
            "medium": _load_tile("sprite-1-3.png"),   
            "small":  _load_tile("sprite-2-2.png"),   
            "flat":   _load_tile("sprite-2-1.png"),   
            "wall":   _load_tile("sprite-1-1.png"),   
            "sq":     _load_tile("sprite-1-7.png"),   
            "pillar": _load_tile("sprite-1-6.png"),   
            "cL":     _load_tile("sprite-1-2.png"),   
            "cR":     _load_tile("sprite-1-5.png"),   
            "deco":   _load_tile("sprite-3-1.png"),   
        }

    def _load_backgrounds(self):
        W, H = WIDTH, HEIGHT
        def bg(name, w=W, h=H):
            return _load(name, scale_to=(w, h))

        self.bg_layers = [
            ParallaxLayer(bg("Background.png"),      0.01, 0.0, 0),
            ParallaxLayer(bg("Castle.png"),          0.00, 0.0, 0),
            ParallaxLayer(bg("Clouds.png"),          0.01, 0.0, 0),
            ParallaxLayer(bg("Sun.png"),             0.00, 0.0, 0),
            ParallaxLayer(bg("Forest05.png"),        0.00, 0.0, 0),
            ParallaxLayer(bg("Forest04.png"),        0.00, 0.0, 0),
            ParallaxLayer(bg("Forest03.png"),        0, 0.0, 0),
            ParallaxLayer(bg("Forest02.png"),        0.0, 0.0, 0),
            ParallaxLayer(bg("Forest01.png"),        0.00, 0.0, 0),
            ParallaxLayer(bg("Giants.png"),          0.00, 0.0, 0),
        ]

        self._tree_imgs = {
            "t1": _load("Tree01.png", scale_to=(600, 640)),
            "t2": _load("Tree02.png", scale_to=(360, 400)),
            "t3": _load("Tree03.png", scale_to=(480, 520)),
            "t4": _load("Tree04.png", scale_to=(300, 340)),
        }
        self._grass_imgs = {
            "g1": _load("Grass01.png", scale_to=(200, 100)),
            "g2": _load("Grass02.png", scale_to=(200, 100)),
        }

    def _build_platforms(self):
        t  = self.t
        FY = self.FLOOR_Y
        self.platforms = []
        P = self.platforms

        floor_count = LEVEL_W // t["medium"].get_width() + 2
        P.append(Platform(0, FY, t["medium"], floor_count))

        P.append(Platform(1400, FY - 128, t["small"], 2))
        P.append(Platform(1900, FY - 128, t["cL"],   1))
        P.append(Platform(1900 + 120, FY - 128, t["flat"], 1))
        P.append(Platform(1900 + 120 + 376, FY - 128, t["cR"], 1))
        P.append(Platform(2400, FY - 256, t["wide"], 2))
        P.append(Platform(2800, FY - 512, t["wall"], 1))

        P.append(Platform(3100, FY - 128, t["small"], 1))
        P.append(Platform(3450, FY - 256, t["small"], 1))
        P.append(Platform(3800, FY - 384, t["small"], 1))
        P.append(Platform(4100, FY - 384, t["wide"], 3))
        P.append(Platform(4100, FY - 384, t["pillar"], 1))
        P.append(Platform(4100 + 1512 - 120, FY - 384, t["pillar"], 1))
        P.append(Platform(4600, FY - 384 - 256, t["sq"], 1))

        P.append(Platform(5100, FY - 256, t["small"], 1))
        P.append(Platform(5450, FY - 384, t["small"], 1))
        P.append(Platform(5750, FY - 256, t["small"], 1))
        P.append(Platform(6000, FY - 384, t["cL"],   1))
        P.append(Platform(6000 + 120, FY - 384, t["wide"], 4))
        P.append(Platform(6000 + 120 + 2016, FY - 384, t["cR"], 1))
        P.append(Platform(6800, FY - 512, t["wall"], 2))

        P.append(Platform(7100, FY - 384, t["small"], 1))
        P.append(Platform(7450, FY - 256, t["small"], 1))
        P.append(Platform(7800, FY - 128, t["flat"],  1))

        P.append(Platform(9200, FY - 760, t["pillar"], 1))
        P.append(Platform(8700, FY - 128, t["cL"],1))
        P.append(Platform(8700, FY - 128, t["wide"], 1))
        P.append(Platform(9000, FY - 128, t["wide"], 1))
        P.append(Platform(9300, FY - 128, t["wide"], 1))
        P.append(Platform(9600, FY - 128, t["wide"], 1))
        P.append(Platform(9900, FY - 128, t["wide"], 1))
        P.append(Platform(10200, FY - 128, t["wide"], 1))
        P.append(Platform(10500, FY - 128, t["wide"], 1))

    def _build_decorations(self):
        FY = self.FLOOR_Y
        self.decorations = []
        D = self.decorations
        ti = self._tree_imgs
        gi = self._grass_imgs

        for x in range(0, LEVEL_W, 180):
            key = "g1" if x % 360 == 0 else "g2"
            D.append(Decoration(x, FY - gi[key].get_height(), gi[key]))

        tree_positions = [
            (100,  "t1"), (400,  "t2"), (650,  "t3"), (950,  "t1"),
            (1300, "t4"), (1700, "t2"), (2100, "t3"), (2600, "t4"),
            (3000, "t1"), (3900, "t2"),
            (5200, "t4"), (6200, "t3"),
            (7500, "t2"), (8200, "t1"),
        ]
        for wx, key in tree_positions:
            img = ti[key]
            D.append(Decoration(wx, FY - img.get_height(), img))

        for x in [1600, 2200, 3300, 4400, 5600, 6500, 7200,]:
            D.append(Decoration(x, FY - self.t["deco"].get_height(), self.t["deco"]))
    
    def _build_bonfires(self):
        FY = self.FLOOR_Y
        self.bonfires = [
            Bonfire(300,  FY),   
            Bonfire(8000, FY),   
        ]
        
    def _build_enemies(self):
        FY    = self.FLOOR_Y
        plats = self.get_platforms()
        floor = FY - SPR_H           

        self.enemies = [
            SkeletonSword(  1600, FY - 128 - SPR_H, plats),
            Archer(         2100, FY - 128 - SPR_H, plats, facing_right=False),
            SkeletonKnight( 2600, FY - 128 - SPR_H,plats),
            SkeletonSword(  3500, FY - 256 - SPR_H, plats, facing_right=False),
            SkeletonKnight( 4300, FY - 384 - SPR_H, plats),
            Archer(         4750, FY - 384 - 256 - SPR_H, plats, facing_right=False),
            Archer(         5500, FY - 384 - SPR_H, plats, facing_right=False),
            SkeletonKnight( 6400, FY - 384 - SPR_H, plats),
            SkeletonSword(  6950, FY - 384 - SPR_H, plats, facing_right=False),
            SkeletonSword(  7150, FY - 384 - SPR_H, plats),
        ]
        
        if hasattr(self, 'boss'):
            self._build_boss()

    def get_enemies(self):
        return self.enemies
    
    def _build_boss(self):
        FY         = self.FLOOR_Y
        plats      = self.get_platforms()
        
        # FIX: The boss is exactly 640 pixels tall (128 * 5).
        # We spawn him perfectly so his feet touch the raised platform at FY - 128!
        boss_floor = FY - 128 - 640  
        
        self.boss  = HoodedKnight(10000, boss_floor, plats)

    def _build_fog_gate(self):
        self.fog_gate = FogGate(
            world_x     = self.FOG_GATE_X,
            floor_y     = self.FLOOR_Y,
            gate_height = LEVEL_H,
        )

    def spawn_victory_bonfire(self):
        """Spawns a bonfire in the centre of the boss arena after the boss dies."""
        if not any(bf.world_x > 9500 for bf in self.bonfires):
            FY = self.FLOOR_Y
            # Boss arena floor is FY - 128; centre of arena ~x=10200
            self.bonfires.append(Bonfire(10200, FY - 128))

    def get_boss(self):
        return self.boss
    
    def get_fog_gate(self):
        return self.fog_gate

    def get_platforms(self):
        return [p.rect for p in self.platforms]

    def get_bonfires(self):
        return self.bonfires

    def check_bonfire(self, player_x, player_y):
        for bf in self.bonfires:
            if bf.near_player(player_x, player_y):
                return bf
        return None

    def activate_bonfire(self, bonfire, player):
        player.hp      = player.MAX_HP
        player.stamina = float(player.MAX_STAMINA)
        player.flasks  = player.MAX_FLASKS
        player.spawn_x = bonfire.world_x + bonfire.rect.w // 2
        
        floor_level = bonfire.world_y + bonfire.rect.h
        player.spawn_y = floor_level - (128 * SPRITE_SCALE) + player.FOOT_OFFSET

    def draw_background(self, surface, camera):
        for layer in self.bg_layers:
            layer.draw(surface, camera)

    def draw_decorations(self, surface, camera):
        for d in self.decorations:
            d.draw(surface, camera)

    def draw_platforms(self, surface, camera):
        for p in self.platforms:
            p.draw(surface, camera)

    def draw_bonfires(self, surface, camera):
        for bf in self.bonfires:
            bf.draw(surface, camera)
    
    def draw_fog_gate(self, surface, camera, player_rect=None):
        self.fog_gate.draw(surface, camera)
        # draw_prompt is called directly by main.py after this

    def draw_boss(self, surface, camera):
        if self.boss:
            self.boss.draw(surface, camera)