import pygame
import random
import itertools
import math
############# Parametres
vitesse_du_jeu = 50
max_bombs = 10
penalite_bombe = 1
max_partie = 5000
WIDTH = 600
HEIGHT = 400
BLOCK_SIZE = 10 
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

def closest_bomb(pos, bombs):
    if not bombs:
        return None
    min_distance = math.inf
    closest_bomb = None
    for b in bombs:
        distance = abs(b[0] - pos[0]) + abs(b[1] - pos[1])
        if distance < min_distance:
            min_distance = distance
            closest_bomb = b
    return closest_bomb

class QValues:
    def __init__(self):
        sqs = [''.join(s) for s in list(itertools.product(*[['0','1']] * 4))]
        widths = ['0','1','NA']
        heights = ['2','3','NA']
        widths_b = ['0','1','NA',"no_bomb"]
        heights_b = ['2','3','NA',"no_bomb"]
        self.states = {}
        for i1 in widths:
            for j1 in heights:
                for i2 in widths_b:
                    for j2 in heights_b:
                        for k in sqs:
                            self.states[str((i1,j1,i2,j2,k))] = [0,0,0,0]
q_values = QValues()

class GameState:
    def __init__(self, distance_food, position_food, distance_bomb, position_bomb, surroundings, food, bomb):
        self.distance_food = distance_food
        self.position_food = position_food
        self.distance_bomb = distance_bomb
        self.position_bomb = position_bomb
        self.surroundings = surroundings
        self.food = food
        self.bomb = bomb

class Learner:
    def __init__(self, display_width, display_height, block_size):
        self.display_width = display_width
        self.display_height = display_height
        self.block_size = block_size
        self.epsilon = 0.3
        self.lr = 0.1
        self.discount = .05
        self.qvalues = q_values.states
        self.history = []
        self.actions = {0: 'LEFT', 1: 'RIGHT', 2: 'UP', 3: 'DOWN'}

    def reset(self):
        self.history = []

    def act(self, snake, food, bombs):
        state = self.get_state(snake, food, bombs)
        state_scores = self.qvalues[self.get_state_str(state)]
        action_key = state_scores.index(max(state_scores))
        action_val = self.actions[action_key]
        self.history.append({'state': state, 'action': action_key})
        return action_val
    
    def update_qvalues(self, partie_terminee, bombe_touchee):
        history = self.history[::-1]
        for i, h in enumerate(history[:-1]):
            if partie_terminee:
                sN = history[0]['state']
                aN = history[0]['action']
                state_str = self.get_state_str(sN)
                reward = -100
                self.qvalues[state_str][aN] = (1 - self.lr) * self.qvalues[state_str][aN] + self.lr * reward
            else:
                s1 = h['state']
                s0 = history[i + 1]['state']
                a0 = history[i + 1]['action']
                x1_food = s0.distance_food[0]
                y1_food = s0.distance_food[1]
                x2_food = s1.distance_food[0]
                y2_food = s1.distance_food[1]
                x1_bomb = s0.distance_bomb[0]
                y1_bomb = s0.distance_bomb[1]
                x2_bomb = s1.distance_bomb[0]
                y2_bomb = s1.distance_bomb[1]
                # si le serpent mange
                if s0.food != s1.food:
                    reward = 1
                # si le serpent touche une bombe
                elif bombe_touchee:
                    reward = -10
                # si le serpent se rapproche de la nourriture
                elif abs(x1_food) > abs(x2_food) or abs(y1_food) > abs(y2_food):
                    reward = 0.1
                # si le serpent s'éloigne des bombes
                elif (type(x1_bomb) == float or type(x1_bomb) == int) and (type(x2_bomb) == float or type(x2_bomb) == int):
                    if abs(x1_bomb) <= abs(x2_bomb) and abs(y1_bomb) <= abs(y2_bomb):
                        reward = 0.1
                    else:
                        reward = -0.01
                else:
                    reward = -0.01
                 

                state_str = self.get_state_str(s0)
                new_state_str = self.get_state_str(s1)
                self.qvalues[state_str][a0] = (1 - self.lr) * (self.qvalues[state_str][a0]) + self.lr * (
                        reward + self.discount * max(self.qvalues[new_state_str]))
                
    def get_state(self, snake, food, bombs):
        snake_head = snake[0]
        bomb = closest_bomb(snake_head,bombs)
        dist_x_food = food[0] - snake_head[0]
        dist_y_food = food[1] - snake_head[1]
        pos_x_food = '1' if dist_x_food > 0 else '0' if dist_x_food < 0 else 'NA'
        pos_y_food = '3' if dist_y_food > 0 else '2' if dist_y_food < 0 else 'NA'
        if bomb:
            dist_x_bomb = bomb[0] - snake_head[0]
            dist_y_bomb = bomb[1] - snake_head[1]
            pos_x_bomb = '1' if dist_x_bomb > 0 else '0' if dist_x_bomb < 0 else 'NA'
            pos_y_bomb = '3' if dist_y_bomb > 0 else '2' if dist_y_bomb < 0 else 'NA'
        else :
            dist_x_bomb = "no_bomb"
            dist_y_bomb = "no_bomb"
            pos_x_bomb = "no_bomb"
            pos_y_bomb = "no_bomb"
        sqs = [(snake_head[0] - self.block_size, snake_head[1]), (snake_head[0] + self.block_size, snake_head[1]),
               (snake_head[0], snake_head[1] - self.block_size), (snake_head[0], snake_head[1] + self.block_size)]
        surrounding_list = []
        for sq in sqs:
            if sq[0] < 0 or sq[1] < 0:
                surrounding_list.append('1')
            elif sq[0] >= self.display_width or sq[1] >= self.display_height:
                surrounding_list.append('1')
            elif sq in snake[1:]:
                surrounding_list.append('1')
            else:
                surrounding_list.append('0')
        surroundings = ''.join(surrounding_list)
        return GameState((dist_x_food, dist_y_food), (pos_x_food, pos_y_food),(dist_x_bomb, dist_y_bomb), (pos_x_bomb, pos_y_bomb), surroundings, food, bomb)

    def get_state_str(self, state):
        return str((state.position_food[0], state.position_food[1],state.position_bomb[0], state.position_bomb[1], state.surroundings))
    
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
    
def game_loop():
    game_over = False
    duree = 0
    # Configuration de la fenêtre
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

        show_score(1, WHITE, 'Consolas', 20, score)
        pygame.display.update()
        learner.update_qvalues(partie_terminee=game_over, bombe_touchee=bombe_touchee)
        clock.tick(vitesse_du_jeu)
    return score, reason


game_count = 1
learner = Learner(WIDTH, HEIGHT, BLOCK_SIZE)

while game_count <= max_partie:
    learner.reset()
    if game_count > max_partie / 2:
        learner.epsilon = 0  
    else:
        learner.epsilon = .2
    score, reason = game_loop()
    print(f"Games: {game_count}; Score: {score}; Reason: {reason}") 
    if game_count == max_partie:
        print("Q_values after the last game:")
        for state, values in q_values.states.items():
            print(f"State: {state}, Q-values: {values}") 
    game_count += 1




