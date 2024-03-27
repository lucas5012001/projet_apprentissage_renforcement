import pygame
import random
import json
import itertools

pygame.init()

YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)

BLOCK_SIZE = 10 
DIS_WIDTH = 600
DIS_HEIGHT = 400

QVALUES_N = 100
FRAMESPEED = 50000

class QValues:
    def __init__(self):
        sqs = [''.join(s) for s in list(itertools.product(*[['0','1']] * 4))]
        widths = ['0','1','NA']
        heights = ['2','3','NA']

        self.states = {}
        for i in widths:
            for j in heights:
                for k in sqs:
                    self.states[str((i,j,k))] = [0,0,0,0]

q_values = QValues()

class GameState:
    def __init__(self, distance, position, surroundings, food):
        self.distance = distance
        self.position = position
        self.surroundings = surroundings
        self.food = food

class Learner:
    def __init__(self, display_width, display_height, block_size):
        self.display_width = display_width
        self.display_height = display_height
        self.block_size = block_size
        self.epsilon = 0.1
        self.lr = 0.7
        self.discount = .5
        self.qvalues = q_values.states
        self.history = []
        self.actions = {0: 'left', 1: 'right', 2: 'up', 3: 'down'}

    def reset(self):
        self.history = []


    def act(self, snake, food):
        state = self.get_state(snake, food)
        state_scores = self.qvalues[self.get_state_str(state)]
        action_key = state_scores.index(max(state_scores))
        action_val = self.actions[action_key]
        self.history.append({'state': state, 'action': action_key})
        return action_val

    def update_qvalues(self, reason):
        history = self.history[::-1]
        for i, h in enumerate(history[:-1]):
            if reason:
                sN = history[0]['state']
                aN = history[0]['action']
                state_str = self.get_state_str(sN)
                reward = -1
                self.qvalues[state_str][aN] = (1 - self.lr) * self.qvalues[state_str][aN] + self.lr * reward
                reason = None
            else:
                s1 = h['state']
                s0 = history[i + 1]['state']
                a0 = history[i + 1]['action']
                x1 = s0.distance[0]
                y1 = s0.distance[1]
                x2 = s1.distance[0]
                y2 = s1.distance[1]
                if s0.food != s1.food:
                    reward = 1
                elif abs(x1) > abs(x2) or abs(y1) > abs(y2):
                    reward = 1
                else:
                    reward = -1
                state_str = self.get_state_str(s0)
                new_state_str = self.get_state_str(s1)
                self.qvalues[state_str][a0] = (1 - self.lr) * (self.qvalues[state_str][a0]) + self.lr * (
                        reward + self.discount * max(self.qvalues[new_state_str]))

    def get_state(self, snake, food):
        snake_head = snake[-1]
        dist_x = food[0] - snake_head[0]
        dist_y = food[1] - snake_head[1]
        pos_x = '1' if dist_x > 0 else '0' if dist_x < 0 else 'NA'
        pos_y = '3' if dist_y > 0 else '2' if dist_y < 0 else 'NA'
        sqs = [(snake_head[0] - self.block_size, snake_head[1]), (snake_head[0] + self.block_size, snake_head[1]),
               (snake_head[0], snake_head[1] - self.block_size), (snake_head[0], snake_head[1] + self.block_size)]
        surrounding_list = []
        for sq in sqs:
            if sq[0] < 0 or sq[1] < 0:
                surrounding_list.append('1')
            elif sq[0] >= self.display_width or sq[1] >= self.display_height:
                surrounding_list.append('1')
            elif sq in snake[:-1]:
                surrounding_list.append('1')
            else:
                surrounding_list.append('0')
        surroundings = ''.join(surrounding_list)
        return GameState((dist_x, dist_y), (pos_x, pos_y), surroundings, food)

    def get_state_str(self, state):
        return str((state.position[0], state.position[1], state.surroundings))

def game_loop():
    global dis
    dis = pygame.display.set_mode((DIS_WIDTH, DIS_HEIGHT))
    pygame.display.set_caption('Snake')
    clock = pygame.time.Clock()
    x1 = DIS_WIDTH / 2
    y1 = DIS_HEIGHT / 2
    x1_change = 0
    y1_change = 0
    snake_list = [(x1, y1)]
    length_of_snake = 1
    foodx = round(random.randrange(0, DIS_WIDTH - BLOCK_SIZE) / 10.0) * 10.0
    foody = round(random.randrange(0, DIS_HEIGHT - BLOCK_SIZE) / 10.0) * 10.0
    dead = False
    reason = None

    while not dead:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        action = learner.act(snake_list, (foodx, foody))

        if action == "left":
            x1_change = -BLOCK_SIZE
            y1_change = 0
        elif action == "right":
            x1_change = BLOCK_SIZE
            y1_change = 0
        elif action == "up":
            y1_change = -BLOCK_SIZE
            x1_change = 0
        elif action == "down":
            y1_change = BLOCK_SIZE
            x1_change = 0

        x1 += x1_change
        y1 += y1_change
        snake_head = (x1, y1)
        snake_list.append(snake_head)

        if x1 >= DIS_WIDTH or x1 < 0 or y1 >= DIS_HEIGHT or y1 < 0:
            reason = 'Screen'
            dead = True

        if snake_head in snake_list[:-1]:
            reason = 'Tail'
            dead = True

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, DIS_WIDTH - BLOCK_SIZE) / 10.0) * 10.0
            foody = round(random.randrange(0, DIS_HEIGHT - BLOCK_SIZE) / 10.0) * 10.0
            length_of_snake += 1

        if len(snake_list) > length_of_snake:
            del snake_list[0]

        dis.fill(BLUE)
        draw_food(foodx, foody)
        draw_snake(snake_list)
        draw_score(length_of_snake - 1)
        pygame.display.update()

        learner.update_qvalues(reason)

        clock.tick(FRAMESPEED)

    return length_of_snake - 1, reason


def draw_food(foodx, foody):
    pygame.draw.rect(dis, GREEN, [foodx, foody, BLOCK_SIZE, BLOCK_SIZE])   


def draw_score(score):
    font = pygame.font.SysFont("comicsansms", 35)
    value = font.render(f"Score: {score}", True, YELLOW)
    dis.blit(value, [0, 0])


def draw_snake(snake_list):
    for x in snake_list:
        pygame.draw.rect(dis, BLACK, [x[0], x[1], BLOCK_SIZE, BLOCK_SIZE])


game_count = 1
max_partie = 20
learner = Learner(DIS_WIDTH, DIS_HEIGHT, BLOCK_SIZE)

while game_count <= max_partie:
    learner.reset()
    if game_count > max_partie / 2:
        learner.epsilon = 0  # Arrêt de l'exploration
    else:
        learner.epsilon = .1
    score, reason = game_loop()
    print(f"Games: {game_count}; Score: {score}; Reason: {reason}") 
    if game_count == max_partie:
        print("Q_values after the last game:")
        for state, values in q_values.states.items():
            print(f"State: {state}, Q-values: {values}") 
    game_count += 1
