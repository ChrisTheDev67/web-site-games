import arcade as ad
import random as rd
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "PYPCIKI PROTIV ABOBYCOB"
LASER_SPEED = 5
ENEMY_SPEED = 1
ENEMY_DISTANCE = 50

class TieFighter(ad.Sprite):
    def __init__(self):
        super().__init__("TieFighter.png", 0.2)
        self.angle = 90
        self.change_y = ENEMY_SPEED
    def update(self):
        self.center_y -= self.change_y

class Laser(ad.Sprite):
    def __init__(self, falcon):
        super().__init__("laser.png", 0.8)
        self.center_x = falcon.center_x
        self.bottom = falcon.top
        self.change_y = LASER_SPEED
        self.laser_sound = ad.load_sound("laser.wav")
    def update(self):
        self.center_y += self.change_y
        if self.bottom > SCREEN_HEIGHT:
            self.kill()

class Millenium_falcon(ad.Sprite):
    def __init__(self):
        super().__init__("falcon.png", 0.3)
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = 100
        self.change_x = 0
    def update(self):
        self.center_x += self.change_x
        self.center_x = max(0, min(SCREEN_WIDTH, self.center_x))
class Mygame(ad.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.lose = False
        self.win = False
        self.game = True
        self.bg = ad.load_texture("background.jpg")
        self.lose_bg = ad.load_texture("lost.jpg")
        self.win_bg = ad.load_texture("win.png")
        self.falcon = Millenium_falcon()
        self.set_mouse_visible(False)
        self.lasers = ad.SpriteList()
        self.enemies = ad.SpriteList()
        self.music = ad.load_sound("A New Hope.mp3",volume=0.5)
        self.setup()
    def setup(self):
        self.enemies.clear()
        self.lasers.clear()
        for i in range(50):
            tie_fighter = TieFighter()
            tie_fighter.center_x = rd.randint(0, SCREEN_WIDTH)
            tie_fighter.center_y = SCREEN_HEIGHT + i * ENEMY_DISTANCE
            self.enemies.append(tie_fighter)
        self.game = True
        ad.play_sound(Mygame.music, volume=0.5)
    def update(self, delta_time):
        if len(self.enemies) == 0:
            self.win_game()
            return
        if not self.game:
            return
        self.falcon.update()
        self.lasers.update()
        self.enemies.update()
        for laser in self.lasers:
            hit_list = ad.check_for_collision_with_list(laser, self.enemies)
            if hit_list:
                laser.kill()
                for enemy in hit_list:
                    enemy.kill()
        for enemy in self.enemies:
            if enemy.bottom <= 0:
                self.lose_game()
                break
    def win_game(self):
        self.game = False
        self.enemies.clear()
        self.lasers.clear()
        self.falcon.kill()
        self.win = True
    def lose_game(self):
        self.game = False
        self.enemies.clear()
        self.lasers.clear()
        self.falcon.kill()
        self.lose = True
    def on_draw(self):
        self.clear((255,255,255))
        if self.lose:
            self.clear((255,255,255))
            ad.draw_texture_rectangle(SCREEN_WIDTH / 2,SCREEN_HEIGHT / 2,SCREEN_WIDTH,SCREEN_HEIGHT,self.lose_bg)
        elif self.win:
            self.clear((255,255,255))
            ad.draw_texture_rectangle(SCREEN_WIDTH / 2,SCREEN_HEIGHT / 2,SCREEN_WIDTH,SCREEN_HEIGHT,self.win_bg)
        else:
            ad.draw_texture_rectangle(SCREEN_WIDTH / 2,SCREEN_HEIGHT / 2,SCREEN_WIDTH,SCREEN_HEIGHT,self.bg)
            self.falcon.draw()
            self.lasers.draw()
            self.enemies.draw()
    def on_mouse_motion(self, x, y, dx, dy):
        self.falcon.center_x = x
    def on_mouse_press(self, x, y, button, modifiers):
        if button == ad.MOUSE_BUTTON_LEFT and self.game:
            laser = Laser(self.falcon)
            self.lasers.append(laser)
            ad.play_sound(laser.laser_sound, volume=0.5)





window = Mygame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
ad.run()