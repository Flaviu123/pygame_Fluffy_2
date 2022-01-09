#Imports
from typing import Set
import pygame
from pygame import mouse
from pygame import cursors
from pygame.rect import Rect
from pygame.version import PygameVersion
from pygame import mixer_music
import os
import random
pygame.font.init()

#Klasse Settings speicherung von verschiedenen Globalen Variabeln
class Settings:
    (window_width, window_height) = (900, 650)
    path_file = os.path.dirname(os.path.abspath(__file__))
    path_image = os.path.join(path_file, "Images")
    sound_path = os.path.join(path_file, "Sounds") 
    fps = 60
    max_balls = 14
    spawn = 0
    resize_time = 0
    score = 0
    delay_spawn = 0.5
    delay_resize = 0.5
    ball_size = 5
    ball_size_original = 5
    cursor_size_v = 15
    cursor_size_h = 10
    color_blue = (0,0,255)   
    font = pygame.font.SysFont('', 30)
    game_font = pygame.font.SysFont('', 90)
    

#Klasse Background
class Background(object):
#Hier wird der Hintergrund eingeladen und scaliert
    def __init__(self, filename="Halle.png"):
        super().__init__()
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename)).convert()
        self.image = pygame.transform.scale(self.image, (Settings.window_width, Settings.window_height))
        
#Hier wird der Hintergrund gezeichnet.
    def draw(self, screen):
        screen.blit(self.image, (0, 0))

#Klasse Ball 
class Ball(pygame.sprite.Sprite):
#Hier wird das bitmap für den Ball eingeladen scaliert und die position für den spawn wird bestimmt
    def __init__(self):
        super().__init__()
        self.image_original = pygame.image.load(os.path.join(Settings.path_image, "Ball.png")).convert_alpha()
        self.radius = Settings.ball_size_original
        self.image = pygame.transform.scale(self.image_original, (self.radius * 2, self.radius * 2))
        self.rect = self.image.get_rect()
        self.rect.left = random.randint(0, Settings.window_width - 25)
        self.rect.top = random.randint(0, Settings.window_height - 25)
        
#Hier wird das ganze gezeichnet 
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        
#Hier wird geregelt das die bälle nicht nach unten rechts wachsen die Spawn-Zeit festgelegt, neu scaliert, wachstums geschwindigkeit und border für die bälle        
    def update(self):
        old_center = self.rect.center
        self.image = pygame.transform.scale(self.image_original, (self.radius * 2, self.radius * 2))
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        Settings.resize_time += 0.0166666666
        if Settings.resize_time >= Settings.delay_resize:
            self.radius += random.randint(1, 4)         
            Settings.resize_time = 0
        if self.rect.top < 0:
            self.kill()
            Settings.score += 1
        if self.rect.bottom > Settings.window_height:
            self.kill()
            Settings.score += 1
        if self.rect.right > Settings.window_width:
            self.kill()
            Settings.score += 1
        if self.rect.left < 0:
            self.kill()
            Settings.score += 1
            
       
#Klasse Maus     
class Mouse(pygame.sprite.Sprite):
#Hier wird das bitmap für den curser eingeladen passent scaliert und an die Maus angehängt
    def __init__(self):
        super().__init__()
        self.image_original = pygame.image.load(os.path.join(Settings.path_image, "Hand.png")).convert_alpha()
        self.scale_v = Settings.cursor_size_v
        self.scale_h = Settings.cursor_size_h
        self.image = pygame.transform.scale(self.image_original, (self.scale_h, self.scale_v))
        self.rect = pygame.Rect(0, 0, 8, 15) 

    def update(self):
        self.rect.center = pygame.mouse.get_pos()
        

#Klasse Game
class Game(object):
#Hier wirde die größe für das Fenster festgelegt, ein timer wird eingestellt und balls und mouse werden in sprite Groups abgelegt
    def __init__(self):
        super().__init__()
        pygame.init()
        self.screen = pygame.display.set_mode((Settings.window_width,Settings.window_height))
        self.clock = pygame.time.Clock()
        self.running = False
        self.balls = pygame.sprite.Group()
        self.ball = Ball()
        self.mouse = pygame.sprite.Group()
        
#Hier werden die verschiedenen Methoden aufgerufen zum starten
    def run(self):
        self.start()
        self.gametext = Settings.game_font.render(f'', False, Settings.color_blue)
        self.running = True
        while self.running:
            self.clock.tick(Settings.fps)
            self.update()
            self.watch_for_events()
            self.draw()
                
        pygame.quit()
        
#Hier wird dafür gesorgt das man den Hintergrund die Bälle die maus und den Score sieht
    def draw(self):
        self.background.draw(self.screen)
        self.balls.draw(self.screen)
        self.mouse.draw(self.screen)
        self.screen.blit(self.pointtext,(0, 0))
        self.screen.blit(self.gametext,( Settings.window_width//2-240 ,Settings.window_height//2))
        pygame.display.flip()
        
#Hier wird gesorgt das alles auf dem neusten stand ist und nichts was wichtig ist nur einmal aufgerufen wird
    def update(self):
        self.balls.update()
        self.mouse.update()
        self.collison()
        Settings.spawn += 0.0166666666
        if Settings.spawn >= Settings.delay_spawn and len(self.balls.sprites()) <= Settings.max_balls:
            self.new_ball()
            Settings.spawn = 0
        self.pointtext = Settings.font.render(f'Points = {Settings.score}', False, Settings.color_blue)
        
#Hier kommt die erste funktion wenn man p drückt pausiert das Game          
    def break_time(self):
        paused = True 
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = False
                        
#diese Funktion wird aufgerufen wenn ein neuer ball spawnen soll hier wird dafür gesorgt das die blasen nicht direkt über einander spawnen und es wird ein Sound eingeladen und abgespielt                        
    def new_ball(self):
        new_ball_var = Ball()
        if not pygame.sprite.spritecollideany(new_ball_var, self.balls, pygame.sprite.collide_circle):
            self.balls.add(new_ball_var)
            pygame.mixer.music.load(os.path.join(Settings.sound_path, "Bubble.mp3"))
            pygame.mixer.music.play(0, 0.0) 
            
#Hier wird überprüft ob eine kollision zwischen zwei bällen vorliegt        
    def collison(self):
        balls = self.balls.sprites()
        for i, ball1 in enumerate(balls):
            for ball2 in balls[i+1:]:
                if pygame.sprite.collide_circle(ball1, ball2):
                    self.gameover()

#Hier wird die kollision zwischen Cursor und Ball überprüft der Score wird angepasst und ein Sound wird eingeladen und abgespielt                                    
    def click(self):
        if pygame.sprite.groupcollide(self.mouse, self.balls, False, True):
            Settings.score += 3
            pygame.mixer.music.load(os.path.join(Settings.sound_path, "Clap.mp3"))
            pygame.mixer.music.play(0, 0.0)  
              
#Wenn sich zwei Bälle berühren wird Game Over angezeigt        
    def gameover(self):
        self.gametext = Settings.game_font.render(f'GAME OVER', False, Settings.color_blue)

#Hier wird auf Eingaben vom spieler gewartet     
    def watch_for_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN: 
                match event.key:
                    case pygame.K_ESCAPE:
                        self.running = False

                    case pygame.K_p:
                        self.break_time()
                    case _:
                        print("Keine Bekannte Taste!")
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.click()

#Diese Funktion wird einmal am anfang ausgeführt und stellt einige konstanten auf
    def start(self):
        self.background = Background()
        self.new_ball()
        self.mouse.add(Mouse())
        pygame.mouse.set_visible(False)
        pygame.mixer.music.set_volume(0.1)
        print("Start")
        


if __name__ == "__main__":

    game = Game()
    game.run()
