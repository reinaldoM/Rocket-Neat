import random
import numpy as np
import pygame
import glob
import os
from keras import backend as K
from keras.models import Model
from keras.layers import Dense, Flatten, BatchNormalization,\
                        Conv2D, MaxPooling2D, Dropout, Input
from keras.optimizers import Adam
from rocket import GameManager, Player, Wall



pygame.init()
game = GameManager()



batch_size = 32
n_episodes = 6000
output_dir = 'model_output/RocketA2Cconv/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

class DQNAgent:
    def __init__(self, state_size=[64,64,3], action_size=2, alpha=0.00001, beta=0.00005):
        self.state_size = state_size
        self.action_size = action_size
        self.alpha = alpha
        self.beta = beta
        self.gamma = 0.96

        self.actor, self.critic, self.policy = self._build_model()
        self.action_space = [i for i in range(self.action_size)]
        
    def load_existing_weights(self, model_ ,path):
        print(path)
        if os.path.exists(path):
            
            files = glob.glob('{}*'.format(path))
            latest_file = max(files, key = os.path.getctime)
            model_.load_weights(latest_file)
            print("weights loaded")
    def _build_model(self):
        input = Input(shape=(self.state_size))
        delta = Input(shape=[1])
        conv1 = Conv2D(64, kernel_size = (6,6), activation='relu', padding = 'same')(input)
        conv2 = Conv2D(128, kernel_size = (3,3), activation='relu', padding = 'same')(conv1)
        maxpool1 = MaxPooling2D(pool_size = (2,2))(conv2)
        flatten = Flatten()(maxpool1)
        dense1 = Dense(16, activation = 'relu')(flatten)
        dense2 = Dense(32, activation = 'relu')(dense1)
        probs = Dense(self.action_size, activation='softmax')(dense2)
        values = Dense(1, activation='linear')(dense2)

        def custom_loss(y_true, y_pred):
            out = K.clip(y_pred, 1e-8, 1-1e-8)
            log_lik = y_true*K.log(out)
            return K.sum(-log_lik*delta)

        actor = Model(input=[input, delta], output=[probs])
        actor.compile(optimizer=Adam(lr=self.alpha), loss=custom_loss)

        critic = Model(input=[input],output=[values])
        critic.compile(optimizer=Adam(lr=self.beta),loss='mean_squared_error')

        policy = Model(input=[input],output=[probs])

        actor.summary()
        critic.summary()
        #self.load_existing_weights(actor, 'model_output/2048A2Cconv/actor/')
        #self.load_existing_weights(critic, 'model_output/2048A2Cconv/critic/')
        
        return actor, critic, policy
    
       
    def choose_action(self, state):
        
        probabilities = self.policy.predict(state)[0]
        action = np.random.choice(self.action_space, p=probabilities)

        return action
    
    def learn(self, state, action, reward, state_, done):

        critic_value = self.critic.predict(state)
        critic_value_ = self.critic.predict(state_)

        
        target = reward + self.gamma*critic_value_*(1-int(done))
        delta = target - critic_value

        actions = np.zeros([1, self.action_size])
        actions[np.arange(1), action] = 1.0

        self.actor.fit([state,delta],actions, verbose = 0)
        self.critic.fit(state,target, verbose = 0)

        


agent = DQNAgent()
score_hist = []
for e in range(n_episodes):
    game.start()
    state = game.get_state()
    state = np.reshape(state, [1,64,64,3])
    done = False
    score = 0
    
    while not done:
        
        game.time_counter += 1
        game.player.y += 2 #gravity
        game.player.score = 1
        if game.player.velocity[0] > 0:
            game.player.y -= 3
            game.player.velocity[0] -= 1
        if game.player.velocity[1] > 0:
            game.player.y += 3
            game.player.velocity[1] -= 1
        if game.time_counter%77 == 0:
            game.createPairWall()
        if game.player.y > 580 or game.player.y < 0:
            game.player.stop = True
            game.player.score = -10
            game.running = False
                    
        if game.walls[1].x <= (game.player.x+40) <= (game.walls[1].x+83):#collision check
            if (game.walls[1].y-22) >= game.player.y >= (game.walls[0].y+402):
                game.player.score = 30
            else:
                game.player.stop = True
                game.player.score = -10                   
                game.running = False
                    
        for i in game.walls:        
            i.render()        
            if i.x < -50:
                game.walls.remove(i)            
            i.x += -4

        game.render()
        
        action = agent.choose_action(state)

        game.player.handle_action(action)
        done = game.player.stop
        reward = game.player.score
        next_state = game.get_state()
        next_state = np.reshape(next_state, [1,64,64,3])
        agent.learn(state, action, reward, next_state, done)
        
        score += reward
        state = next_state
        if done:
            break
    score_hist.append(score)
    avg_score = np.mean(score_hist[-100:])
    print('episode : {}/{}, score: {}, avg_score: {:.2}'
                  .format(e, n_episodes-1, score, avg_score))
                        
    if e % 40 == 0:
        agent.actor.save_weights(output_dir + 'actor/weights_{}.hdf5'.format(e))
        agent.critic.save_weights(output_dir + 'critic/weights_{}.hdf5'.format(e))
