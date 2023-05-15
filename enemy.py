import pygame as py


class Enemy(py.sprite.Sprite):
    def __init__(self, health, animation_list, x, y, speed):
        py.sprite.Sprite.__init__(self)
        self.alive = True
        self.speed = speed
        self.health = health
        self.last_attack = py.time.get_ticks()
        self.attack_cooldown = 1000
        self.animation_list = animation_list
        self.frame_index = 0
        self.action = 0  #action matches our folders name and order of dictionary list
        self.update_time = py.time.get_ticks()

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = py.Rect(0,0,25,40)
        #self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, surface, target, bullet_group):
        if self.alive:
            #check for collision
            if py.sprite.spritecollide(self, bullet_group, True):
                self.health -= 25
            #check if health zero
            if self.health <= 0:
                target.money += 100
                target.score += 1000
                print(target.score)
                self.alive =  False
                
                self.update_action(2)
                
            #check if enemy has reached the castle
            if self.rect.right > target.rect.left:
                self.update_action(1)

            #move enemy
            if self.action == 0:
                self.rect.x += self.speed

            #attack
            if self.action == 1:
                #check cooldown
                if py.time.get_ticks() - self.last_attack > self.attack_cooldown:
                    target.health -= 25
                    if target.health < 0:
                        target.health = 0
                    self.last_attack = py.time.get_ticks()

        
        
        
        self.update_animation()
        #draw image
        #py.draw.rect(surface, (255,255,255), self.rect, 1)
        surface.blit(self.image, (self.rect.x -10, self.rect.y -15))

    def update_animation(self):
        #update animation cooldown
        ANIMATION_COOLDOWN = 50 #higher number equals slower animation loop
        #update image depending on action
        self.image = self.animation_list[self.action][self.frame_index]
        if py.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = py.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 2:
                self.frame_index = (len(self.animation_list[self.action]) -1)
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        #check if new action
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_date = py.time.get_ticks()




