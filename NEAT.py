import numpy as np
import pygame
import glob
import os
import neat
from sklearn.model_selection import train_test_split
from rocketNeat import GameManager, Player, Wall



pygame.init()
game = GameManager()

output_dir = 'model_output/rocketNEAT/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

#the state is rocket y coordinate, next wall y coordinate, and next wall x coordinate
state_size = 3
#the actions are go up, do nothing, and go down.
action_size = 3

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)

def load_checkpoint(path, config):
    if os.path.exists(path):            
        files = glob.glob('{}*'.format(path))
        if len(files) == 0:
            return neat.Population(config)
        latest_file = max(files, key = os.path.getctime)
        print("weights loaded")
        return neat.Checkpointer.restore_checkpoint(latest_file)
        


def getState(index):
        states = game.get_states()
        state = states[index]
        state = np.array(state)/100
        def scale(X, x_min, x_max):
            nom = (X-X.min(axis=0))*(x_max-x_min)
            denom = X.max(axis=0) - X.min(axis=0)
            return x_min + nom/denom
        return state
    
def eval_genomes(genomes, config):   
    nets = []
    
    for genome_id, genome in genomes:
        genome.fitness = 0.0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        
    done = False
    scores = []
    game.start(len(genomes))
    while not done:
        actions = []
        for index, rocket in enumerate(game.population):
            action_dist = nets[index].activate(getState(index))
            action_dist = softmax(action_dist)
            action = np.argmax(action_dist)
            actions.append(action)

        game.step(actions)
        game.render()
        done = game.stopLoop
        if done:
            for index, rocket in enumerate(game.population):
                scores.append(rocket.score)

    for genome_id, genome in genomes:
        genome.fitness = scores[0]
        scores.pop(0)

        
def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = load_checkpoint(output_dir, config)

    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))
    
    winner = p.run(eval_genomes, 200)
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)


        
        


