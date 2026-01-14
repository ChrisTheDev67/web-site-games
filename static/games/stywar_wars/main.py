import pygame
import random
import asyncio
import os

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "PYPCIKI PROTIV ABOBYCOB"
LASER_SPEED = 5
ENEMY_SPEED = 1
ENEMY_DISTANCE = 50

# Global screen variable (will be initialized in main)
screen = None

class TieFighter(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load image
        try:
            self.image = pygame.image.load("TieFighter.png")
            # Scale logic
            w = int(self.image.get_width() * 0.2)
            h = int(self.image.get_height() * 0.2)
            self.image = pygame.transform.scale(self.image, (w, h))
        except:
             # Fallback surface
            self.image = pygame.Surface((30, 30))
            self.image.fill((255, 0, 0))
            
        self.rect = self.image.get_rect()
        self.angle = 90
        self.change_y = ENEMY_SPEED

    def update(self):
        # Move down
        self.rect.y += self.change_y

class Laser(pygame.sprite.Sprite):
    def __init__(self, falcon_rect):
        super().__init__()
        try:
            self.image = pygame.image.load("laser.png")
            w = int(self.image.get_width() * 0.8)
            h = int(self.image.get_height() * 0.8)
            self.image = pygame.transform.scale(self.image, (w, h))
        except:
            self.image = pygame.Surface((5, 15))
            self.image.fill((0, 255, 0))
            
        self.rect = self.image.get_rect()
        self.rect.centerx = falcon_rect.centerx
        self.rect.bottom = falcon_rect.top
        self.change_y = LASER_SPEED
        # Load sound
        try:
            # First try the default, then fallbacks
            if os.path.exists("laser.wav"):
                self.laser_sound = pygame.mixer.Sound("laser.wav")
            else:
                 self.laser_sound = None
        except:
            self.laser_sound = None

    def update(self):
        self.rect.y -= self.change_y
        if self.rect.bottom < 0:
            self.kill()

class Millenium_falcon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load("falcon.png")
            w = int(self.image.get_width() * 0.3)
            h = int(self.image.get_height() * 0.3)
            self.image = pygame.transform.scale(self.image, (w, h))
        except:
            self.image = pygame.Surface((50, 50))
            self.image.fill((0, 0, 255))
            
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.centery = SCREEN_HEIGHT - 100
        self.change_x = 0

    def update(self):
        self.rect.x += self.change_x
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH

async def main():
    global screen
    
    print("Game Startup Sequence Initiated")
    
    # NOTE: Do NOT set SDL_WINDOWID or SDL_VIDEODRIVER
    # pygame-ce in the browser uses Emscripten/SDL which automatically
    # creates and manages the canvas element
    
    try:
        pygame.init()
        print("Pygame base initialized")
        
        # Safe mixer setup
        try:
            pygame.mixer.pre_init(44100, -16, 2, 1024)
            pygame.mixer.init()
            print("Mixer initialized")
        except Exception as e:
            print(f"Mixer warning: {e}")

        # Yield to browser event loop before creating display
        await asyncio.sleep(0.1)
        
        # Screen setup - pygame-ce handles canvas creation automatically
        print(f"Opening window: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(SCREEN_TITLE)
        print("Display ready")
        
    except Exception as e:
        print(f"Critical Init Error: {e}")
        import traceback
        traceback.print_exc()
        return

    # Yield again after display creation
    await asyncio.sleep(0.1)

    # Load Backgrounds
    print("Loading textures...")
    try:
        bg = pygame.image.load("background.jpg")
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        lose_bg = pygame.image.load("lost.jpg")
        lose_bg = pygame.transform.scale(lose_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

        win_bg = pygame.image.load("win.png")
        win_bg = pygame.transform.scale(win_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        print("Textures loaded")
    except Exception as e:
        print(f"Texture Error: {e}")
        # Fallbacks
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        bg.fill((30, 30, 30))
        lose_bg = bg.copy()
        win_bg = bg.copy()

    # Sprites initialization
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    lasers = pygame.sprite.Group()
    
    falcon = Millenium_falcon()
    all_sprites.add(falcon)

    def setup_enemies():
        enemies.empty()
        for i in range(50):
            t = TieFighter()
            t.rect.x = random.randint(0, SCREEN_WIDTH - t.rect.width)
            t.rect.y = - (i * ENEMY_DISTANCE + 100)
            enemies.add(t)
            all_sprites.add(t)

    setup_enemies()
    
    game_active = True
    win = False
    lose = False
    
    clock = pygame.time.Clock()
    print("Starting Game Loop")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.MOUSEMOTION:
                 if game_active:
                     falcon.rect.centerx = event.pos[0]
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and game_active:
                    l = Laser(falcon.rect)
                    lasers.add(l)
                    all_sprites.add(l)
                    if l.laser_sound:
                        l.laser_sound.play()

        if game_active:
            all_sprites.update()
            pygame.sprite.groupcollide(lasers, enemies, True, True)
            
            for enemy in enemies:
                if enemy.rect.top > SCREEN_HEIGHT:
                    lose = True
                    game_active = False
            
            if len(enemies) == 0:
                win = True
                game_active = False

        # Draw
        if lose:
            screen.blit(lose_bg, (0,0))
        elif win:
            screen.blit(win_bg, (0,0))
        else:
            screen.blit(bg, (0,0))
            all_sprites.draw(screen)

        pygame.display.flip()
        
        # CRITICAL: YIELD TO BROWSER
        await asyncio.sleep(0)
        clock.tick(60)

if __name__ == '__main__':
    # Standard PyScript/Pyodide async startup
    asyncio.ensure_future(main())
