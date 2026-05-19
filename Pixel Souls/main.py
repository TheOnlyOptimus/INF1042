import pygame

# Initialize Pygame first so other modules can load fonts/images
pygame.init()
from settings import WIDTH, HEIGHT, BG_COLOR, PLAT_COL, GROUND_Y, SPRITE_SCALE, PLAYER_HEIGHT, PLAYER_WIDTH
from utils import get_path
from player import Player
from camera import Camera
from hud import HUD

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pixel Souls - Animation Tester")
    clock = pygame.time.Clock()

    camera = Camera()
    player = Player()
    hud = HUD()

    # Load Background
    bg_path = get_path("city.webp")
    try:
        bg_image = pygame.transform.scale(
            pygame.image.load(bg_path).convert(),
            (WIDTH, HEIGHT)
        )
    except pygame.error:
        print(f"[WARN] Could not load background {bg_path} — using solid colour")
        bg_image = None

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            player.handle_event(event, pygame.key.get_pressed())

        keys = pygame.key.get_pressed()
        player.update(dt, keys)

        camera.update(
            player.x + PLAYER_WIDTH // 2,
            player.y + PLAYER_HEIGHT // 2,
        )

        # ── RENDER ────────────────────────────────────────────────────────────
        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill(BG_COLOR)

        # Calculate where the floor should be drawn relative to the camera
        floor_screen_y = GROUND_Y - int(camera.y)


        player.draw(screen, camera)
        hud.draw(screen, player)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()