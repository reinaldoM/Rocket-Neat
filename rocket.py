import sys, pygame, random, threading, time
import numpy as np
from PIL import Image

#pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((600, 600))

class Wall(object):
    def __init__(self,x,y,name):        
        self.x = x
        self.y = y
        self.image = pygame.image.load(name)
        self.rect = self.image.get_rect()        
    def render(self):
        screen.blit(self.image, (self.x,self.y))
        
class Player(object):
    def __init__(self,x,y,name):
        self.x = x
        self.y = y
        self.stop = False
        self.velocity = [0,0]
        self.score = 0
        self.image = pygame.image.load(name)
        self.rect = self.image.get_rect()
    def handle_action(self,action):
        if action == 0:
            self.velocity[0] = 7
            self.velocity[1] = 0
        if action == 1:
            self.velocity[0] = 0
            self.velocity[1] = 7
        return 0, self.stop
    
    def render(self):
        screen.blit(self.image, (self.x,self.y))
     
class GameManager(object):
    def __init__(self):
        self.player = Player(15,300,"rocket.png")
        self.walls = []
        self.stopLoop = False
        self.dif = 0
        self.running = True
        self.time_counter = 0
    def createWall(self,x,y):
        self.walls.append(Wall(x,y,"wall.png"))
    def createPairWall(self):       
        n = random.randint(200,400)
        self.dif += 1
        top = n - (450 - self.dif)
        down = n + (150 - self.dif)
        self.createWall(650,top)
        self.createWall(650,down)    
    def get_state(self):
        string_image = pygame.image.tostring(screen, 'RGB')
        temp_surf = pygame.image.fromstring(string_image,(600, 600),'RGB' )
        window_to_array = pygame.surfarray.array3d(temp_surf)
        im = Image.fromarray(window_to_array)
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
        im = im.transpose(Image.ROTATE_90)
        im = im.resize((64,64))
        #im.save('image.jpeg')
        image_array = np.array(im)
        return image_array
    def start(self):
        self.player.x = 15
        self.player.y = 300
        self.player.stop = False
        self.player.velocity = [0,0]
        self.player.score = 0
        
        self.walls = []
        self.stopLoop = False
        self.dif = 0
        self.running = True
        self.time_counter = 0
        self.createPairWall()
        #self.play()
    def play(self):
        while self.running:
            self.time_counter += 1
            self.player.y += 2
            if self.player.velocity[0] > 0:
                self.player.y -= 3
                self.player.velocity[0] -= 1
            if self.player.velocity[1] > 0:
                self.player.y += 3
                self.player.velocity[1] -= 1
            if self.time_counter%77 == 0:
                self.createPairWall()
            if self.player.y > 580 or self.player.y < 0:
                self.player.stop = True
                self.player.score = -10
                self.running = False
                    
            if self.walls[1].x <= (self.player.x+40) <= (self.walls[1].x+83):#collision check
                if (self.walls[1].y-22) >= self.player.y >= (self.walls[0].y+402):
                    self.player.score = 30
                else:
                    self.player.stop = True
                    self.player.score = -10                   
                    self.running = False
                    
            for i in self.walls:        
                i.render()        
                if i.x < -50:
                    self.walls.remove(i)            
                i.x += -4

            
            
    def render(self):            
        self.player.render()
        pygame.display.update()
        screen.fill((255, 255, 255))
        clock.tick(70)
