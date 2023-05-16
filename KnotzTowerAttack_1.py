import pygame as py
import math
import button
from enemy import Enemy
import random
import os
import pymunk

py.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
screen = py.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
py.display.set_caption('KnotZ_Castle_Attack')

clock = py.time.Clock()
FPS= 60
WHITE = (255,255,255)
GREY = (100,100,100)

#game variables
high_score = 0
level = 1
level_difficulty = 0
target_difficulty = 1000
DIFFICULTY_MULTIPLIER = 1.1
game_over = False
next_level = False
ENEMY_TIMER = 1000
last_enemy = py.time.get_ticks()
enemy_alive = 0

max_towers = 4
TOWER_COST = 5000
tower_positions = [
    [SCREEN_WIDTH - 260, SCREEN_HEIGHT - 200], 
    [SCREEN_WIDTH - 210, SCREEN_HEIGHT - 150],
    [SCREEN_WIDTH - 150, SCREEN_HEIGHT - 150],
    [SCREEN_WIDTH - 100, SCREEN_HEIGHT - 150],
]

#load high score
if os.path.exists('score.txt'):
    with open('score.txt', 'r') as file:
        high_score = int(file.read())

font = py.font.SysFont('Futura', 30)
font_60 = py.font.SysFont('Futura', 60)

#load images
bg = py.image.load('img/bg.png').convert_alpha()
#castle
castle__img_100 = py.image.load('img/castle/castle_100.png').convert_alpha()
castle__img_50 = py.image.load('img/castle/castle_50.png').convert_alpha()
castle__img_25 = py.image.load('img/castle/castle_25.png').convert_alpha()
#Tower
tower_img_100 = py.image.load('img/tower/tower_100.png').convert_alpha()
tower_img_50 = py.image.load('img/tower/tower_50.png').convert_alpha()
tower_img_25 = py.image.load('img/tower/tower_25.png').convert_alpha()

bullet_img = py.image.load('img/bullet.png').convert_alpha()
b_w = bullet_img.get_width()
b_h = bullet_img.get_height()
bullet_img = py.transform.scale(bullet_img, (int(b_w *.075), int(b_h * .07)))

#enemies
enemy_animation = []
enemy_types = ['knight', 'goblin', 'purple_goblin', 'red_goblin'] #add new enemies to this dict
enemy_health = [75, 100, 125, 150] #listing the enemies health 1 to 1 from above

animation_types = ['walk', 'attack', 'death'] #add new animations actions here
for enemy in enemy_types:
    #load animations
    animation_list = []
    for animation in animation_types:
        temp_list = []
        #define number of frames
        num_of_frames = 20  #need to update this to be a variable number so we can have different animations
        for i in range(num_of_frames):
            img = py.image.load(f'img/enemies/{enemy}/{animation}/{i}.png').convert_alpha()
            e_w = img.get_width()
            e_h = img.get_height()
            img = py.transform.scale(img, (int(e_w * .2), int(e_h * 0.2)))
            temp_list.append(img)
        animation_list.append(temp_list)
    enemy_animation.append(animation_list)

#button img
repair_img = py.image.load('img/repair.png').convert_alpha()
armor_img = py.image.load('img/armour.png').convert_alpha()

#output text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))
#display status
def show_info():
    draw_text('Money: ' + str(castle.money), font, GREY, 10, 10)
    draw_text('Score: ' + str(castle.score), font, GREY, 180, 10)
    draw_text('High Score: ' + str(high_score), font, GREY, 180, 30)
    draw_text('Level: ' + str(level), font, GREY, SCREEN_WIDTH // 2, 10)
    draw_text('Health: ' + str(castle.health) + " / " + str(castle.max_health), font, GREY, SCREEN_WIDTH -230, SCREEN_HEIGHT - 50)
    draw_text('1000', font, GREY, SCREEN_WIDTH - 220, 60)
    draw_text(str(TOWER_COST), font, GREY, SCREEN_WIDTH - 85, 60)
    draw_text('500', font, GREY, SCREEN_WIDTH - 145, 60)

class Castle():
    def __init__(self, image100, image50, image25, x, y, scale):
        self.health = 1000
        self.max_health = self.health
        self.fired = False
        self.money = 25000
        self.score = 0

        
        width = image100.get_width()
        height = image100.get_height()
        

        self.image100 = py.transform.scale(image100, (int(width * scale), int(height *scale)))
        self.image50 = py.transform.scale(image50, (int(width * scale), int(height *scale)))
        self.image25 = py.transform.scale(image25, (int(width * scale), int(height *scale)))
        self.rect = self.image100.get_rect()
        self.rect.x = x
        self.rect.y = y

    def shoot(self):
        pos = py.mouse.get_pos()
        x_dist = pos[0] - self.rect.midleft[0]
        y_dist = -(pos[1] - self.rect.midleft[1])
        self.angle = math.degrees(math.atan2(y_dist, x_dist))

        if py.mouse.get_pressed()[0] and self.fired == False and pos[1] > 70:
            # Only allow shooting if there are less than 5 bullets on screen
            if len(bullet_group) < 3 + len(tower_group):
                self.fired =True
                bullet = Bullet(bullet_img, self.rect.midleft[0], self.rect.midleft[1], self.angle)
                bullet_group.add(bullet)
        if py.mouse.get_pressed()[0] == False:
            self.fired = False

    def draw(self):
        #check health
        if self.health <= self.health * .75:
            self.image = self.image25
        elif self.health <= self.health* .50:
            self.image = self.image50
        else:
            self.image = self.image100
        screen.blit(self.image, self.rect)

    def repair(self):
        if self.money >= 1000 and self.health < self.max_health:
            self.health += 500
            self.money -= 1000
            if castle.health >  castle.max_health:
                castle.health = castle.max_health
    def armor(self):
        if self.money >= 500:
            self.max_health += 250
            self.money -= 500
            if castle.health >  castle.max_health:
                castle.health = castle.max_health

class Tower(py.sprite.Sprite):
    def __init__(self, image100, image50, image25, x, y, scale):
        py.sprite.Sprite.__init__(self)

        self.got_target  = False
        self.angle = 0
        self.last_shot = py.time.get_ticks()

        width = image100.get_width()
        height = image100.get_height()

        self.image100 = py.transform.scale(image100, (int(width * scale), int(height *scale)))
        self.image50 = py.transform.scale(image50, (int(width * scale), int(height *scale)))
        self.image25 = py.transform.scale(image25, (int(width * scale), int(height *scale)))
        self.image = self.image100
        self.rect = self.image100.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, enemy_group):
        self.got_target = False
        for e in enemy_group:
            if e.alive:
                target_x, target_y = e.rect.bottomleft
                self.got_target = True
                break
        if self.got_target:
            x_dist = target_x - self.rect.midleft[0]
            y_dist = -(target_y - self.rect.midleft[1])
            self.angle = math.degrees(math.atan2(y_dist, x_dist))  -33#controls arc for bullet

            shot_cooldown = 1000
            #fire bullets
            if py.time.get_ticks() - self.last_shot > shot_cooldown:
                self.last_shot = py.time.get_ticks()
                bullet = Bullet(bullet_img, self.rect.midleft[0], self.rect.midleft[1], self.angle)
                bullet_group.add(bullet)

        #check health
        if castle.health <= castle.health * .75:
            self.image = self.image25
        elif castle.health <= castle.health* .50:
            self.image = self.image50
        else:
            self.image = self.image100

class Bullet(py.sprite.Sprite):
    def __init__(self, image, x, y, angle):
        py.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.angle = math.radians(angle) #convert input into radians from degrees
        self.speed = 600
        


        # Create a pymunk Body for this bullet
        self.body = pymunk.Body(mass=1, moment=10)  # mass and moment are parameters you can tweak
        # Set its position to the current Pygame position
        self.body.position = pymunk.Vec2d(self.rect.x, self.rect.y)
        # Create a pymunk Circle for this bullet
        self.shape = pymunk.Circle(self.body, 10)  # 10 is the radius of the circle, you can tweak this
        # Add the body and shape to the space
        space.add(self.body, self.shape)

        #calculate speed of angle
        # in the __init__ method
        vx = self.speed * math.cos(self.angle)
        vy = -self.speed * math.sin(self.angle)  # upwards is negative in Pygame
        self.body.velocity = pymunk.Vec2d(vx, vy)

    def update(self):
        # Move bullet
        
        self.rect.x = self.body.position.x
        self.rect.y = SCREEN_HEIGHT - self.body.position.y  # Convert from Pymunk's coordinates to Pygame's

        # Check if offscreen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0:
            self.kill()
        self.rect.x = self.body.position.x
        self.rect.y = self.body.position.y

class Crosshair():
    def __init__(self,scale):
        image = py.image.load('img/crosshair.png').convert_alpha()
        width = image.get_width()
        height = image.get_height()
        self.image = py.transform.scale(image, (int(width *scale), int(height *scale)))
        self.rect = self.image.get_rect()

        #hide mouse
        py.mouse.set_visible(False)

    def draw(self):
        mx, my = py.mouse.get_pos()
        self.rect.center = (mx,my)
        screen.blit(self.image, self.rect)

#create castle 
castle = Castle(castle__img_100, castle__img_50, castle__img_25, (SCREEN_WIDTH - 250), SCREEN_HEIGHT - 300, 0.2)
crosshair = Crosshair(0.025)
#create buttons
repair_button = button.Button(SCREEN_WIDTH - 220, 10, repair_img, .5)
armor_button = button.Button(SCREEN_WIDTH - 150, 10, armor_img, 1.25)
tower_button = button.Button(SCREEN_WIDTH - 80, 10, tower_img_100, 0.1)

#groups
tower_group = py.sprite.Group()
bullet_group = py.sprite.Group()
enemy_group = py.sprite.Group()



# Create a space for the physics simulation
space = pymunk.Space()
# Set its gravity
space.gravity = (0, 500)  # (0, 900) is a downward force (since y coordinates increase downwards in Pygame)



#main loop
run = True
while run:
    clock.tick(FPS)
    # Step the pymunk Space forward in time
    space.step(1/60)  # 1/60 is the time step in seconds, which should match your FPS


    if game_over == False:
        #Draw_everything in order of appearance
        screen.blit(bg, (0,0))
        castle.draw()
        castle.shoot()

        tower_group.draw(screen)
        tower_group.update(enemy_group)

        crosshair.draw()

        bullet_group.update()
        bullet_group.draw(screen)

        enemy_group.update(screen, castle, bullet_group)

        #show stats
        show_info()
        #upgrade buttons
        if repair_button.draw(screen):
            castle.repair()
        if armor_button.draw(screen):
            castle.armor()
        if tower_button.draw(screen):
            if castle.money >= TOWER_COST and len(tower_group) < max_towers:
                tower = Tower(tower_img_100, tower_img_50,tower_img_25, 
                tower_positions[len(tower_group)][0], tower_positions[len(tower_group)][1], 0.2)
                tower_group.add(tower)
                castle.money -= TOWER_COST

        #create enemies
        #check max number per level
        if level_difficulty < target_difficulty:
            if py.time.get_ticks() - last_enemy > ENEMY_TIMER:

                #create enemies
                e = random.randint(0, len(enemy_types)-1)
                enemy = Enemy(enemy_health[e], enemy_animation[e], -100, SCREEN_HEIGHT -100, 1)
                enemy_group.add(enemy)
                last_enemy = py.time.get_ticks()
                #increase difficulty
                level_difficulty += enemy_health[e]

        #check if all enemines have been spawned
        if level_difficulty >= target_difficulty:
            #check enemies alive
            enemies_alive = 0
            for e in enemy_group:
                if e.alive == True:
                    enemies_alive += 1
            #if all dead level complete
            if enemies_alive == 0 and next_level == False:
                next_level = True
                level_reset_time = py.time.get_ticks()

        #move onto the next level
        if next_level == True:
            draw_text('LEVEL COMPLETE!', font_60, WHITE, 200, 300)
            #update high score
            if castle.score > high_score:
                high_score = castle.score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))
            if py.time.get_ticks() - level_reset_time > 1500:
                next_level = False
                level += 1
                last_enemy = py.time.get_ticks()
                target_difficulty *= DIFFICULTY_MULTIPLIER
                level_difficulty = 0
                enemy_group.empty()

        #check game over
        if castle.health <= 0:
            game_over = True
    else:
        draw_text('GAME_OVER!!', font_60, GREY, SCREEN_WIDTH //2 -150,SCREEN_HEIGHT //2)
        draw_text('PRESS "A" TO PLAY 1 MO AGAIN', font, GREY, SCREEN_WIDTH //2 -150,SCREEN_HEIGHT //2 +80)
        py.mouse.set_visible(True)
        key = py.key.get_pressed()
        if key[py.K_a]:
            #reset
            game_over = False
            level = 1
            target_difficulty = 1000
            level_difficulty = 0
            last_enemy = py.time.get_ticks()
            enemy_group.empty()
            tower_group.empty()
            castle.score = 0
            castle.health = 1000
            castle.max_health = castle.health
            castle.money = 0
            py.mouse.set_visible(False)
        
    #event handle
    for event in py.event.get():
        if event.type == py.QUIT:
            run = False


    
    
    py.display.update()

py.quit()