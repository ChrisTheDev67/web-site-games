import pygame
import random
import asyncio
import os

# Initialize Pygame
pygame.init()
try:
    # Set frequency to 44100 for better browser compatibility
    pygame.mixer.pre_init(44100, -16, 2, 1024)
    pygame.mixer.init()
except:
    print("Audio not supported")

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
            self.image = pygame.image.load("TieFighter.png").convert_alpha()
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
            self.image = pygame.image.load("laser.png").convert_alpha()
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
            self.laser_sound = pygame.mixer.Sound("laser.wav")
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
            self.image = pygame.image.load("falcon.png").convert_alpha()
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
    # Set up the screen inside async main
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(SCREEN_TITLE)
    
    # Load Backgrounds
    print("Loading assets inside main...")
    try:
        bg = pygame.image.load("background.jpg").convert()
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception as e:
        print(f"BG Load Error: {e}")
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        bg.fill((50, 50, 50))

    try:
        lose_bg = pygame.image.load("lost.jpg").convert()
        lose_bg = pygame.transform.scale(lose_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        lose_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        lose_bg.fill((100, 0, 0))

    try:
        win_bg = pygame.image.load("win.png").convert_alpha()
        win_bg = pygame.transform.scale(win_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        win_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        win_bg.fill((0, 100, 0))

    # Sprites
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    lasers = pygame.sprite.Group()
    
    falcon = Millenium_falcon()
    all_sprites.add(falcon)

    # Setup Enemies
    def setup_enemies():
        enemies.empty()
        for i in range(50):
            t = TieFighter()
            t.rect.x = random.randint(0, SCREEN_WIDTH - t.rect.width)
            t.rect.y = - (i * ENEMY_DISTANCE + 100)
            enemies.add(t)
            all_sprites.add(t)

    setup_enemies()
    
    # Game State
    game_active = True
    win = False
    lose = False
    
    clock = pygame.time.Clock()
    print("Game Loop Starting")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pass # Browser handle exit?
            
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
            
            hits = pygame.sprite.groupcollide(lasers, enemies, True, True)
            
            for enemy in enemies:
                if enemy.rect.top > SCREEN_HEIGHT:
                    lose = True
                    game_active = False
                    break
            
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
        
        # Asyncio sleep is critical for browser event loop
        clock.tick(60)
        await asyncio.sleep(0)

if __name__ == '__main__':
    print("Launching Game...")
    try:
        loop = asyncio.get_running_loop()
        print("Event loop detected. Scheduling main() task.")
        asyncio.create_task(main())
    except RuntimeError:
        print("No event loop. Starting new one.")
        asyncio.run(main())
