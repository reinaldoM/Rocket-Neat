
import sys, pygame, random, threading, time
import numpy as np
from PIL import Image

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((600, 600))
font = pygame.font.Font('freesansbold.ttf', 16)

black = (0, 0, 0)
white = (255, 255, 255)


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
            pass
        if action == 2:
            self.velocity[0] = 0
            self.velocity[1] = 7
        return 0, self.stop
    
    def render(self):
        screen.blit(self.image, (self.x,self.y))
        

            
class GameManager(object):
    def __init__(self):
        #self.player = Player(15,300,"rocket.png")
        self.popSize = 0
        self.generation = 0
        self.population = []
        self.bestdistance = 0
        self.walls = []
        self.stopLoop = False
        self.dif = 0
        self.running = True
        self.time_counter = 0
    def createPopulation(self, size):
        populationList = []
        for x in range(size):
            populationList.append(Player(15,300,"rocket.png"))
        return populationList
    def getPlayer(self, index):
        return self.population[index]
    def createWall(self,x,y):
        self.walls.append(Wall(x,y,"wall.png"))
    def createPairWall(self):       
        n = random.randint(200,400)
        self.dif += 1
        top = n - (450 - self.dif)
        down = n + (150 - self.dif)
        self.createWall(650,top)
        self.createWall(650,down)    
    def get_states(self):
        #states = [self.player.y, self.walls[1].y - 100, self.walls[1].x]
        states = []
        for i in self.population:
            state = [i.y, self.walls[1].y - 100, self.walls[1].x]
            states.append(state)
        return states
    def start(self, popSize):
        self.popSize = popSize
        self.population = self.createPopulation(self.popSize)
        for i in self.population:
            i.x = 15
            i.y = 300
            i.stop = False
            i.velocity = [0,0]
            i.score = 0
            
        #self.player.x = 15
        #self.player.y = 300
        #self.player.stop = False
        #self.player.velocity = [0,0]
        #self.player.score = 0
        
        self.bestdistance = 0
        
        self.walls = []
        self.generation += 1
        self.stopLoop = False
        self.dif = 0
        self.running = True
        self.time_counter = 0
        self.createPairWall()
        #self.play()
    def text_show(self, value, offset):
        t = font.render(value, True, black)
        textRect = t.get_rect()
        textRect.center = (80, offset)
        screen.blit(t, textRect)
    def step(self, actions):

        #self.text_show(self.walls[1].y,40)
        alive = []
        alive = [alive.append(x) for x in self.population if x.stop == False]
        self.text_show("Generation: {}".format(self.generation),20)
        self.text_show("Population: {}/{}".format(len(alive),len(self.population)),40)
        self.text_show("Distance: {}".format(self.bestdistance),60)

        n_of_dead = 0
        for index, i in enumerate(self.population):
            if i.stop:
                n_of_dead += 1
                if n_of_dead == self.popSize:
                    self.stopLoop = True
            if not i.stop:
                i.handle_action(actions[index])
                i.y += 2
                i.score = 0
                if i.velocity[0] > 0:
                    i.y -= 5
                    i.velocity[0] -= 1
                if i.velocity[1] > 0:
                    i.y += 3
                    i.velocity[1] -= 1
                
                if i.y > 580 or i.y < 0:
                    i.stop = True
                    i.score = -50
                    #self.running = False
                if self.walls[1].x <= (i.x+40) <= (self.walls[1].x+83):#collision check
                    if (self.walls[1].y-22) >= i.y >= (self.walls[0].y+402):
                        i.score = 200
                        pass
                    else:
                        i.stop = True
                        i.score = -50 
                        #self.running = False
                i.score = self.bestdistance - (1 * abs(self.walls[1].y - 100 - i.y))            
                
        self.time_counter += 1
        self.bestdistance += 1
        if self.time_counter%77 == 0:
                self.createPairWall()
        #self.player.score = 1.0 + ((-10.0-1.0)/(600.0-0.0))*(abs((self.walls[1].y+100.0)-self.player.y))            
        
        for i in self.walls:        
            i.render()        
            if i.x < -50:
                self.walls.remove(i)            
            i.x += -4

            
            
    def render(self):
        for i in self.population:
            if not i.stop:
                i.render()
        pygame.display.update()
        screen.fill((255, 255, 255))
        clock.tick(70)

