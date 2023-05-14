import pygame as py
from button import Button
#from enemy import Enemy

py.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = py.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
py.display.set_caption('KnotZ_Castle_Attack')

clock = py.time.Clock()
FPS= 60


#load images
bg = py.image.load('img/bg.png').convert_alpha()
#castle
castle__img_100 = py.image.load('img/castle/castle_100.png').convert_alpha()

class Castle():
    def __init__(self, image100, x, y, scale):
        self.health = 1000
        self.max_health = self.health
        
        width = image100.get_width()
        height = image100.get_height()

        self.image100 = py.transform.scale(image100, (int(width * scale), int(height *scale)))
        self.rect = self.image100.get_rect()
        self.rect.x = x
        self.rect.y = y
    

    def shoot(self):
        pos = py.mouse.get_pos()
        


    def draw(self):
        self.image = self.image100

        screen.blit(self.image, self.rect)

#create castle
castle = Castle(castle__img_100, SCREEN_WIDTH - 250, SCREEN_HEIGHT - 300, 0.2)




#main loop
run = True
while run:

    clock.tick(FPS)
    #event handle
    for event in py.event.get():
        if event.type == py.QUIT:
            run = False


    screen.blit(bg, (0,0))
    castle.draw()
    py.display.update()

py.quit()