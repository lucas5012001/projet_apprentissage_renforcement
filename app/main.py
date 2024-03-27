import pygame
import random

vitesse_du_jeu = 10
size = 1.5

# Initialisation de Pygame
import pygame
import random

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre du jeu
WIDTH, HEIGHT = 600*size, 400*size

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Chargement des images du serpent
head_image = pygame.image.load('snake_head.png')
body_image = pygame.image.load('snake_body.png')

# Redimensionnement des images pour correspondre à la taille du serpent
head_image = pygame.transform.scale(head_image, (10, 10))
body_image = pygame.transform.scale(body_image, (10, 10))

# Configuration de la fenêtre
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Horloge pour contrôler la vitesse du jeu
clock = pygame.time.Clock()

# Variables du jeu
snake_pos = [100, 50]
snake_body = [[100, 50], [90, 50], [80, 50]]
food_pos = [random.randrange(1, (WIDTH//10)) * 10, random.randrange(1, (HEIGHT//10)) * 10]
bomb_pos = [random.randrange(1, (WIDTH//10)) * 10, random.randrange(1, (HEIGHT//10)) * 10]
food_spawn = True
bomb_spawn = True
direction = 'RIGHT'
change_to = direction
score = 0

# Fonction pour afficher le score sur l'écran
def show_score(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    window.blit(score_surface, score_rect)

# Boucle principale du jeu
game_over = False
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                change_to = 'UP'
            if event.key == pygame.K_DOWN:
                change_to = 'DOWN'
            if event.key == pygame.K_LEFT:
                change_to = 'LEFT'
            if event.key == pygame.K_RIGHT:
                change_to = 'RIGHT'

    # Vérifier si la direction est valide
    if change_to == 'UP' and direction != 'DOWN':
        direction = 'UP'
    if change_to == 'DOWN' and direction != 'UP':
        direction = 'DOWN'
    if change_to == 'LEFT' and direction != 'RIGHT':
        direction = 'LEFT'
    if change_to == 'RIGHT' and direction != 'LEFT':
        direction = 'RIGHT'

    # Changer la position de la tête du serpent
    if direction == 'UP':
        snake_pos[1] -= 10
    if direction == 'DOWN':
        snake_pos[1] += 10
    if direction == 'LEFT':
        snake_pos[0] -= 10
    if direction == 'RIGHT':
        snake_pos[0] += 10

    # Faire avancer le serpent
    snake_body.insert(0, list(snake_pos))
    snake_body.pop()
    
    # Réapparition de la nourriture
    if not food_spawn:
        food_pos = [random.randrange(1, (WIDTH//10)) * 10, random.randrange(1, (HEIGHT//10)) * 10]
        food_spawn = True
    
    # Réapparition de la bombe
    if not bomb_spawn:
        bomb_pos = [random.randrange(1, (WIDTH//10)) * 10, random.randrange(1, (HEIGHT//10)) * 10]
        bomb_spawn = True

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
    pygame.draw.rect(window, RED, pygame.Rect(food_pos[0], food_pos[1], 10, 10))
    pygame.draw.rect(window, BLUE, pygame.Rect(bomb_pos[0], bomb_pos[1], 10, 10))

    # Gérer les collisions avec les bords de l'écran
    if snake_pos[0] < 0 or snake_pos[0] > WIDTH-10:
        game_over = True
    if snake_pos[1] < 0 or snake_pos[1] > HEIGHT-10:
        game_over = True

    # Gérer les collisions avec le serpent lui-même
    for block in snake_body[1:]:
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
            game_over = True

    # Gérer les collisions avec la nourriture
    if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
        snake_body.insert(0, list(snake_pos))
        score += 1
        food_spawn = False

    # Gérer les collisions avec la bombe
    if snake_pos[0] == bomb_pos[0] and snake_pos[1] == bomb_pos[1]:
        for _ in range(50):  # Ajouter 10 nouvelles positions de queue
            snake_body.append(list(snake_body[-1]))
        score -= 1
        bomb_spawn = False

    show_score(1, WHITE, 'Consolas', 20)

    pygame.display.update()
    clock.tick(vitesse_du_jeu)

pygame.quit()
