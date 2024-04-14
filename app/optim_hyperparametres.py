import pygame
import random
import itertools
from itertools import product
import numpy as np
from multiprocessing import Pool, cpu_count
import json
import time

############# PARAMETRES DU JEU
vitesse_du_jeu = 50000
max_bombs = 10
penalite_bombe = 1
WIDTH = 600
HEIGHT = 400
BLOCK_SIZE = 10 
########################

############# HYPERPARAMETRES A TESTER
multi_coeur = True
##
list_Nreps=[100,150,200,250,300,400]
epsilon_list=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
lr_list=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
discount_list=[0]
rewards_game_over=[-10]
rewards_food=[1]
rewards_bomb=[-0.1]
rewards_good_move=[0.5]
rewards_bad_move=[-0.1]
Ntest = 300
########################

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Chargement des images du serpent
head_image = pygame.image.load('snake_head.png')
body_image = pygame.image.load('snake_body.png')

# Redimensionnement des images pour correspondre à la taille du serpent
head_image = pygame.transform.scale(head_image, (BLOCK_SIZE, BLOCK_SIZE))
body_image = pygame.transform.scale(body_image, (BLOCK_SIZE, BLOCK_SIZE))

pygame.init()

def vue_serpent(snake, food, bombs):
    head = snake[0]
    poss = ["food","bomb","death"]
    objs = ["death","death","death","death"]
    touche = ["0","0","0","0"]
    #droite
    food_bomb_snake = [WIDTH,WIDTH,WIDTH]
    if head[0] == WIDTH-BLOCK_SIZE:
        touche[0] = "1"
    else:
        if food[1] == head[1]:
            if food[0]-head[0] > 0:
                food_bomb_snake[0] = abs(food[0]-head[0])/BLOCK_SIZE
        for b in bombs:
            if b[1] == head[1]:
                if b[0] - head[0] > 0:
                    food_bomb_snake[1] = abs(b[0] - head[0])/BLOCK_SIZE
        for s in snake[1:]:
            if s[1] == head[1]:
                if s[0] - head[0] > 0:
                    food_bomb_snake[2] = abs(s[0] - head[0])/BLOCK_SIZE
        argm = np.argmin(food_bomb_snake)
        minim = food_bomb_snake[argm]
        if minim != WIDTH:
            objs[0] = poss[argm]
            if minim == 1:
                touche[0] = "1"
    #gauche
    food_bomb_snake = [WIDTH,WIDTH,WIDTH]
    if head[0] == 0:
        touche[3] = "1"
    else:
        if food[1] == head[1]:
            if food[0]-head[0] < 0:
                food_bomb_snake[0] = abs(food[0]-head[0])/BLOCK_SIZE
        for b in bombs:
            if b[1] == head[1]:
                if b[0] - head[0] < 0:
                    food_bomb_snake[1] = abs(b[0] - head[0])/BLOCK_SIZE
        for s in snake[1:]:
            if s[1] == head[1]:
                if s[0] - head[0] < 0:
                    food_bomb_snake[2] = abs(s[0] - head[0])/BLOCK_SIZE
        argm = np.argmin(food_bomb_snake)
        minim = food_bomb_snake[argm]
        if minim != WIDTH:
            objs[3] = poss[argm]
            if minim == 1:
                touche[3] = "1"
    #haut
    food_bomb_snake = [HEIGHT,HEIGHT,HEIGHT]
    if head[1] == HEIGHT - BLOCK_SIZE:
        touche[2] = "1"
    else:
        if food[0] == head[0]:
            if food[1]-head[1] > 0:
                food_bomb_snake[0] = abs(food[1]-head[1])/BLOCK_SIZE
        for b in bombs:
            if b[0] == head[0]:
                if b[1] - head[1] > 0:
                    food_bomb_snake[1] = abs(b[1] - head[1])/BLOCK_SIZE
        for s in snake[1:]:
            if s[0] == head[0]:
                if s[1] - head[1] > 0:
                    food_bomb_snake[2] = abs(s[1] - head[1])/BLOCK_SIZE
        argm = np.argmin(food_bomb_snake)
        minim = food_bomb_snake[argm]
        if minim != HEIGHT:
            objs[2] = poss[argm]
            if minim == 1:
                touche[2] = "1"
    #bas
    food_bomb_snake = [HEIGHT,HEIGHT,HEIGHT]
    if head[1] == 0:
        touche[1] = "1"
    else:
        if food[0] == head[0]:
            if food[1]-head[1] < 0:
                food_bomb_snake[0] = abs(food[1]-head[1])/BLOCK_SIZE
        for b in bombs:
            if b[0] == head[0]:
                if b[1] - head[1] < 0:
                    food_bomb_snake[1] = abs(b[1] - head[1])/BLOCK_SIZE
        for s in snake[1:]:
            if s[0] == head[0]:
                if s[1] - head[1] < 0:
                    food_bomb_snake[2] = abs(s[1] - head[1])/BLOCK_SIZE
        argm = np.argmin(food_bomb_snake)
        minim = food_bomb_snake[argm]
        if minim != HEIGHT:
            objs[1] = poss[argm]
            if minim == 1:
                touche[1] = "1"
    objs = "".join(objs)
    touche = "".join(touche)    
    return objs, touche   
    

class QValues:
    def __init__(self):
        sqs = [''.join(s) for s in list(itertools.product(*[['0','1']] * 4))]
        what = [''.join(s) for s in list(itertools.product(*[['food','bomb','death']] * 4))] 
        widths = ['0','1','NA']
        heights = ['2','3','NA']
        self.states = {}
        for i in widths:
            for j in heights:
                for k in sqs:
                    for l in what:
                        self.states[str((i,j,k,l))] = [0,0,0,0]

q_values = QValues()

class GameState:
    def __init__(self, distance_food, position_food, objs, touche, food):
        self.distance_food = distance_food
        self.position_food = position_food
        self.objs = objs
        self.touche = touche
        self.food = food

class Learner:
    def __init__(self, display_width, display_height, block_size):
        self.display_width = display_width
        self.display_height = display_height
        self.block_size = block_size
        self.epsilon = 0.1
        self.lr = 0.2
        self.discount = .5
        self.qvalues = q_values.states
        self.history = []
        self.actions = {0: 'LEFT', 1: 'RIGHT', 2: 'UP', 3: 'DOWN'}
        self.reward_game_over = -1000
        self.reward_food = 200
        self.reward_bomb = -200
        self.reward_good_move = 0.1
        self.reward_bad_move = -0.1

    def reset(self):
        self.history = []

    def act(self, snake, food, bombs):
        state = self.get_state(snake, food, bombs)
        state_str = self.get_state_str(state)
        state_scores = self.qvalues[state_str]

        # Choix de l'action selon epsilon-greedy
        if random.random() < self.epsilon:
            action_key = random.randint(0, len(self.actions) - 1)
        else:
            action_key = state_scores.index(max(state_scores))
        
        action_val = self.actions[action_key]
        self.history.append({'state': state, 'action': action_key})
        return action_val

    
    def update_qvalues(self, partie_terminee, bombe_touchee):
        history = self.history[::-1]
        if partie_terminee:
            sN = history[0]['state']
            aN = history[0]['action']
            state_str = self.get_state_str(sN)
            reward = self.reward_game_over
            self.qvalues[state_str][aN] = (1-self.lr)*self.qvalues[state_str][aN]+self.lr*reward
        else :
            if len(history)>1:
                s1 = history[0]['state']
                s0 = history[1]['state']
                a0 = history[1]['action']
                x1_food = s0.distance_food[0]
                y1_food = s0.distance_food[1]
                x2_food = s1.distance_food[0]
                y2_food = s1.distance_food[1]
                # si le serpent mange
                if s0.food != s1.food:
                    reward = self.reward_food
                # si le serpent touche une bombe
                elif bombe_touchee:
                    reward = self.reward_bomb
                # si le serpent se rapproche de la nourriture
                elif abs(x1_food) > abs(x2_food) or abs(y1_food) > abs(y2_food):
                    reward = self.reward_good_move
                else:
                    reward = self.reward_bad_move
                state_str = self.get_state_str(s0)
                new_state_str = self.get_state_str(s1)
                self.qvalues[state_str][a0] = (1 - self.lr) * (self.qvalues[state_str][a0]) + self.lr * (
                        reward + self.discount * max(self.qvalues[new_state_str]))
                
    def get_state(self, snake, food, bombs):
        snake_head = snake[0]
        objs, touche = vue_serpent(snake,food,bombs)
        dist_x_food = food[0] - snake_head[0]
        dist_y_food = food[1] - snake_head[1]
        pos_x_food = '1' if dist_x_food > 0 else '0' if dist_x_food < 0 else 'NA'
        pos_y_food = '3' if dist_y_food > 0 else '2' if dist_y_food < 0 else 'NA'
        return GameState((dist_x_food, dist_y_food), (pos_x_food, pos_y_food), objs, touche, food)

    def get_state_str(self, state):
        return str((state.position_food[0], state.position_food[1],state.touche,state.objs))
    
# Fonction pour afficher le score sur l'écran
def show_score(choice, color, font, size, score):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    window.blit(score_surface, score_rect)

# Fonction pour dessiner les bombes sur l'écran
def draw_bombs(bombs):
    for bomb in bombs:
        pygame.draw.rect(window, BLUE, pygame.Rect(bomb[0], bomb[1], BLOCK_SIZE, BLOCK_SIZE))
    
def game_loop(learner,display = False):
    game_over = False
    duree = 0
    # Configuration de la fenêtre
    if display:
        global window
        window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
    # Horloge pour contrôler la vitesse du jeu
    clock = pygame.time.Clock()
    # Variables du jeu
    snake_pos = [random.randrange(1, (WIDTH//BLOCK_SIZE)) * BLOCK_SIZE, random.randrange(1, (HEIGHT//BLOCK_SIZE)) * BLOCK_SIZE]
    snake_body = [snake_pos]
    food_pos = [random.randrange(1, (WIDTH//BLOCK_SIZE)) * BLOCK_SIZE, random.randrange(1, (HEIGHT//BLOCK_SIZE)) * BLOCK_SIZE]
    bombs = []
    food_spawn = True
    direction = 'RIGHT'
    score = 0
    while not game_over:
        duree +=1
        if display:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
        action = learner.act(snake_body,food_pos,bombs)

        # Vérifier si la direction est valide
        if action == 'UP' and direction != 'DOWN':
            direction = 'UP'
        if action == 'DOWN' and direction != 'UP':
            direction = 'DOWN'
        if action == 'LEFT' and direction != 'RIGHT':
            direction = 'LEFT'
        if action == 'RIGHT' and direction != 'LEFT':
            direction = 'RIGHT'

        # Changer la position de la tête du serpent
        if direction == 'UP':
            snake_pos[1] -= BLOCK_SIZE
        if direction == 'DOWN':
            snake_pos[1] += BLOCK_SIZE
        if direction == 'LEFT':
            snake_pos[0] -= BLOCK_SIZE
        if direction == 'RIGHT':
            snake_pos[0] += BLOCK_SIZE

        # Faire avancer le serpent
        snake_body.insert(0, list(snake_pos))
        if snake_pos != food_pos:
            snake_body.pop()
        
        # Réapparition de la nourriture
        if not food_spawn:
            food_pos = [random.randrange(1, (WIDTH//BLOCK_SIZE)) * BLOCK_SIZE, random.randrange(1, (HEIGHT//BLOCK_SIZE)) * BLOCK_SIZE]
            food_spawn = True
            ok = False
            if len(bombs) < max_bombs: 
                while not ok:
                    new_b = [random.randrange(1, (WIDTH//BLOCK_SIZE)) * BLOCK_SIZE, random.randrange(1, (HEIGHT//BLOCK_SIZE)) * BLOCK_SIZE]
                    ok = True
                    if new_b[0] == food_pos[0] and new_b[1] == food_pos[1]:
                        ok = False
                    if ok:
                        for b in bombs:
                            if b[0] == new_b[0] and b[1] == new_b[1]:
                                ok = False
                                break
                bombs.append(new_b) 

        # Dessiner les éléments du jeu sur l'écran
        if display:
            window.fill(BLACK)
            for index, pos in enumerate(snake_body):
                if pos == snake_pos:  # Dessiner la tête du serpent
                    if direction == 'UP':
                        rotated_head = pygame.transform.rotate(head_image, 0)
                    elif direction == 'DOWN':
                        rotated_head = pygame.transform.rotate(head_image, 180)
                    elif direction == 'LEFT':
                        rotated_head = pygame.transform.rotate(head_image, 90)
                    elif direction == 'RIGHT':
                        rotated_head = pygame.transform.rotate(head_image, 270)
                    window.blit(rotated_head, (pos[0], pos[1]))
                else:  # Dessiner le corps du serpent
                    window.blit(body_image, (pos[0], pos[1]))
            pygame.draw.rect(window, RED, pygame.Rect(food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE))
            draw_bombs(bombs)

        # Gérer les collisions avec les bords de l'écran
        if snake_pos[0] < 0 or snake_pos[0] > WIDTH-BLOCK_SIZE:
            game_over = True
            reason = "Sortie d\'ecran"
        if snake_pos[1] < 0 or snake_pos[1] > HEIGHT-BLOCK_SIZE:
            game_over = True
            reason = "Sortie d\'ecran"

        # Gérer les collisions avec le serpent lui-même
        for block in snake_body[1:]:
            if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
                game_over = True
                reason = "Autodétruit"

        # Gérer les collisions avec la nourriture
        if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
            duree = 0
            snake_body.insert(0, list(snake_pos))
            score += 1
            food_spawn = False

        # Gérer les collisions avec les bombes
        bombe_touchee = False
        for bomb in bombs:
            if snake_pos[0] == bomb[0] and snake_pos[1] == bomb[1]:
                bombs.remove(bomb)
                for i in range(penalite_bombe):
                    snake_body.insert(0, list(snake_pos))
                score -= 1
                bombe_touchee = True
                break
            
        if duree > ((WIDTH + HEIGHT)/BLOCK_SIZE)*2:
            game_over = True
            reason = "temps écoulé"
            
        if display:
            show_score(1, WHITE, 'Consolas', 20, score)
            pygame.display.update()
        learner.update_qvalues(partie_terminee=game_over, bombe_touchee=bombe_touchee)
        clock.tick(vitesse_du_jeu)
    return score, reason

def experience(list_Nreps, epsilon_list, lr_list, discount_list, rewards_game_over, rewards_food, rewards_bomb, rewards_good_move, rewards_bad_move, Ntest = 200):
    results = {}
    print((Ntest + np.sum(list_Nreps))*len(epsilon_list)*len(lr_list)*len(discount_list)*len(rewards_game_over)*len(rewards_food)*len(rewards_bomb)*len(rewards_good_move)*len(rewards_bad_move))
    for Nreps,epsilon, lr, discount,reward_game_over,reward_food, reward_bomb,reward_good_move,reward_bad_move in product(list_Nreps,epsilon_list, lr_list, discount_list,rewards_game_over, rewards_food, rewards_bomb, rewards_good_move, rewards_bad_move):
        result = run_experiment(Nreps, epsilon, lr, discount,reward_game_over,reward_food,reward_bomb,reward_good_move,reward_bad_move,Ntest)
        results[str((Nreps,epsilon, lr, discount,reward_game_over,reward_food,reward_bomb,reward_good_move,reward_bad_move))] = result
    return results

def experience_multi(list_Nreps, epsilon_list, lr_list, discount_list, rewards_game_over, rewards_food, rewards_bomb, rewards_good_move, rewards_bad_move, Ntest = 200):
    results = {}
    print(cpu_count()-1)
    print((Ntest+np.sum(list_Nreps))*len(epsilon_list)*len(lr_list)*len(discount_list)*len(rewards_game_over)*len(rewards_food)*len(rewards_bomb)*len(rewards_good_move)*len(rewards_bad_move))
    pool = Pool(processes=(cpu_count()-1))
    hyperparams_combinations = product(list_Nreps, epsilon_list, lr_list, discount_list, rewards_game_over, rewards_food, rewards_bomb, rewards_good_move, rewards_bad_move)
    for Nreps, epsilon, lr, discount, reward_game_over, reward_food, reward_bomb, reward_good_move, reward_bad_move in hyperparams_combinations:
        result = pool.apply_async(run_experiment, args=(Nreps, epsilon, lr, discount, reward_game_over, reward_food, reward_bomb, reward_good_move, reward_bad_move, Ntest))
        results[str((Nreps, epsilon, lr, discount, reward_game_over, reward_food, reward_bomb, reward_good_move, reward_bad_move))] = result
    pool.close()
    pool.join()
    results = {key: result.get() for key, result in results.items()}
    return results

def run_experiment(Nreps, epsilon, lr, discount,reward_game_over,reward_food,reward_bomb,reward_good_move,reward_bad_move,Ntest = 200):
    game_count = 1
    learner = Learner(WIDTH, HEIGHT, BLOCK_SIZE)
    learner.lr = lr
    learner.discount = discount
    learner.reward_game_over = reward_game_over
    learner.reward_food = reward_food
    learner.reward_bomb = reward_bomb
    learner.reward_good_move = reward_good_move
    learner.reward_bad_move = reward_bad_move
    scores = []
    learner.reset()
    learner.epsilon = epsilon
    while game_count <= Nreps:
        score, reason = game_loop(learner)
        game_count += 1
    learner.epsilon = 0
    learner.lr = 0
    learner.discount = 0
    game_count = 1
    while game_count <= Ntest:
        score, reason = game_loop(learner)     
        scores.append(score)
        game_count += 1
    return np.mean(scores)

if __name__ == "__main__":
    start_time = time.time()
    if multi_coeur:
        res = experience_multi(list_Nreps=list_Nreps,
                    epsilon_list=epsilon_list,
                    lr_list=lr_list,
                    discount_list=discount_list,
                    rewards_game_over=rewards_game_over,
                    rewards_food=rewards_food,
                    rewards_bomb=rewards_bomb,
                    rewards_good_move=rewards_good_move,
                    rewards_bad_move=rewards_bad_move,
                    Ntest=Ntest)
    else:
        res = experience(list_Nreps=list_Nreps,
                    epsilon_list=epsilon_list,
                    lr_list=lr_list,
                    discount_list=discount_list,
                    rewards_game_over=rewards_game_over,
                    rewards_food=rewards_food,
                    rewards_bomb=rewards_bomb,
                    rewards_good_move=rewards_good_move,
                    rewards_bad_move=rewards_bad_move,
                    Ntest=Ntest)
    end_time = time.time()

    # Calcul du temps écoulé en secondes
    elapsed_time = end_time - start_time

    key_max = max(res, key=res.get)
    print("Clé associée au meilleur score moyen:", key_max)
    print("Score associé:", res[key_max])
    print("Temps d'exécution:", elapsed_time, "secondes")
    filename = "data.json"
    # Enregistrer le dictionnaire dans un fichier JSON
    with open(filename, 'w') as file:
        json.dump(res, file)
