import pygame  # Importe le module Pygame pour la création de jeux
import random  # Importe le module Random pour la génération de nombres aléatoires
import json  # Importe le module JSON pour la manipulation de données JSON
import itertools  # Importe le module Itertools pour la manipulation d'itérateurs

pygame.init()  # Initialise Pygame

JAUNE = (255, 255, 102)  # Définit la couleur jaune en RGB
NOIR = (0, 0, 0)  # Définit la couleur noire en RGB
VERT = (0, 255, 0)  # Définit la couleur verte en RGB
BLEU = (50, 153, 213)  # Définit la couleur bleue en RGB

TAILLE_BLOC = 10  # Définit la taille d'un bloc
LARGEUR_ECRAN = 600  # Définit la largeur de l'écran
HAUTEUR_ECRAN = 400  # Définit la hauteur de l'écran

VITESSE_FPS = 50000  # Définit la vitesse de rafraîchissement de l'écran en FPS

class QValeurs:  # Définit la classe pour stocker les Q-valeurs
    def __init__(self):  # Initialisation de la classe
        cases = [''.join(c) for c in list(itertools.product(*[['0','1']] * 4))]  # Génère toutes les combinaisons possibles de cases
        largeurs = ['0','1','NA']  # Définit les valeurs possibles pour la largeur
        hauteurs = ['2','3','NA']  # Définit les valeurs possibles pour la hauteur

        self.etats = {}  # Initialise le dictionnaire pour stocker les Q-valeurs des états
        for i in largeurs:  # Boucle sur les valeurs de largeur
            for j in hauteurs:  # Boucle sur les valeurs de hauteur
                for k in cases:  # Boucle sur les combinaisons de cases
                    self.etats[str((i,j,k))] = [0,0,0,0]  # Initialise les Q-valeurs pour chaque état

q_valeurs = QValeurs()  # Initialise les Q-valeurs

class EtatJeu:  # Définit la classe pour représenter un état du jeu
    def __init__(self, distance, position, environnement, nourriture):  # Initialisation de la classe
        self.distance = distance  # Initialise la distance
        self.position = position  # Initialise la position
        self.environnement = environnement  # Initialise l'environnement
        self.nourriture = nourriture  # Initialise la nourriture

class Apprenti:  # Définit la classe de l'apprenant
    def __init__(self, largeur_ecran, hauteur_ecran, taille_bloc):  # Initialisation de la classe
        self.largeur_ecran = largeur_ecran  # Initialise la largeur de l'écran
        self.hauteur_ecran = hauteur_ecran  # Initialise la hauteur de l'écran
        self.taille_bloc = taille_bloc  # Initialise la taille du bloc
        self.epsilon = 0.1  # Initialise le paramètre d'exploration
        self.lr = 0.7  # Initialise le taux d'apprentissage
        self.discount = .5  # Initialise le facteur de remise
        self.qvaleurs = q_valeurs.etats  # Initialise les Q-valeurs
        self.historique = []  # Initialise l'historique des actions
        self.actions = {0: 'gauche', 1: 'droite', 2: 'haut', 3: 'bas'}  # Initialise les actions possibles

    def reset(self):  # Méthode pour réinitialiser l'historique
        self.historique = []

    def agir(self, serpent, nourriture):  # Méthode pour choisir une action
        etat = self.get_etat(serpent, nourriture)  # Obtient l'état actuel
        scores_etat = self.qvaleurs[self.get_str_etat(etat)]  # Obtient les Q-valeurs de l'état
        cle_action = scores_etat.index(max(scores_etat))  # Choix de l'action avec la plus grande Q-valeur
        action = self.actions[cle_action]  # Obtient l'action correspondante
        self.historique.append({'etat': etat, 'action': cle_action})  # Ajoute l'action à l'historique
        return action

    def mise_a_jour_qvaleurs(self, raison):  # Méthode pour mettre à jour les Q-valeurs
        historique = self.historique[::-1]  # Inverse l'historique
        for i, h in enumerate(historique[:-1]):  # Boucle sur l'historique
            if raison:  # Vérifie si une raison a été donnée
                sN = historique[0]['etat']  # Obtient l'état actuel
                aN = historique[0]['action']  # Obtient l'action choisie
                etat_str = self.get_str_etat(sN)  # Convertit l'état en chaîne de caractères
                recompense = -1  # Définit la récompense
                self.qvaleurs[etat_str][aN] = (1 - self.lr) * self.qvaleurs[etat_str][aN] + self.lr * recompense  # Met à jour les Q-valeurs
                raison = None  # Réinitialise la raison
            else:  # Si aucune raison n'a été donnée
                s1 = h['etat']  # Obtient l'état actuel
                s0 = historique[i + 1]['etat']  # Obtient l'état précédent
                a0 = historique[i + 1]['action']  # Obtient l'action choisie
                x1 = s0.distance[0]  # Obtient la distance en x de l'état précédent
                y1 = s0.distance[1]  # Obtient la distance en y de l'état précédent
                x2 = s1.distance[0]  # Obtient la distance en x de l'état actuel
                y2 = s1.distance[1]  # Obtient la distance en y de l'état actuel
                if s0.nourriture != s1.nourriture:  # Vérifie si la nourriture a changé
                    recompense = 1  # Donne une récompense positive
                elif abs(x1) > abs(x2) or abs(y1) > abs(y2):  # Vérifie si le serpent se rapproche de la nourriture
                    recompense = 1  # Donne une récompense positive
                else:  # Si aucune des conditions précédentes n'est remplie
                    recompense = -1  # Donne une récompense négative
                etat_str = self.get_str_etat(s0)  # Convertit l'état précédent en chaîne de caractères
                nouvel_etat_str = self.get_str_etat(s1)  # Convertit l'état actuel en chaîne de caractères
                self.qvaleurs[etat_str][a0] = (1 - self.lr) * (self.qvaleurs[etat_str][a0]) + self.lr * (
                        recompense + self.discount * max(self.qvaleurs[nouvel_etat_str]))  # Met à jour les Q-valeurs
                
                
    def get_etat(self, serpent, nourriture):  # Méthode pour obtenir l'état actuel
        tete_serpent = serpent[-1]  # Obtient la position de la tête du serpent
        dist_x = nourriture[0] - tete_serpent[0]  # Calcule la distance en x entre la nourriture et la tête du serpent
        dist_y = nourriture[1] - tete_serpent[1]  # Calcule la distance en y entre la nourriture et la tête du serpent
        pos_x = '1' if dist_x > 0 else '0' if dist_x < 0 else 'NA'  # Détermine la position relative en x de la nourriture par rapport à la tête du serpent
        pos_y = '3' if dist_y > 0 else '2' if dist_y < 0 else 'NA'  # Détermine la position relative en y de la nourriture par rapport à la tête du serpent
        cases = [(tete_serpent[0] - self.taille_bloc, tete_serpent[1]),  # Définit les cases environnantes
                 (tete_serpent[0] + self.taille_bloc, tete_serpent[1]),
                 (tete_serpent[0], tete_serpent[1] - self.taille_bloc),
                 (tete_serpent[0], tete_serpent[1] + self.taille_bloc)]
        liste_environs = []  # Initialise la liste des environnements
        for case in cases:  # Boucle sur les cases environnantes
            if case[0] < 0 or case[1] < 0:  # Vérifie si la case est en dehors de l'écran
                liste_environs.append('1')  # Ajoute '1' à la liste des environnements
            elif case[0] >= self.largeur_ecran or case[1] >= self.hauteur_ecran:  # Vérifie si la case est en dehors de l'écran
                liste_environs.append('1')  # Ajoute '1' à la liste des environnements
            elif case in serpent[:-1]:  # Vérifie si la case est occupée par le corps du serpent
                liste_environs.append('1')  # Ajoute '1' à la liste des environnements
            else:  # Si aucune des conditions précédentes n'est remplie
                liste_environs.append('0')  # Ajoute '0' à la liste des environnements
        environnements = ''.join(liste_environs)  # Convertit la liste des environnements en une chaîne de caractères
        return EtatJeu((dist_x, dist_y), (pos_x, pos_y), environnements, nourriture)  # Retourne l'état actuel du jeu

    def get_str_etat(self, etat):  # Méthode pour obtenir la chaîne de caractères de l'état
        return str((etat.position[0], etat.position[1], etat.environnement))  # Retourne la chaîne de caractères représentant l'état

def boucle_jeu():  # Fonction pour exécuter la boucle principale du jeu
    global dis  # Définit la surface d'affichage comme globale
    dis = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN))  # Initialise la fenêtre du jeu avec la taille définie
    pygame.display.set_caption('Serpent')  # Définit le titre de la fenêtre du jeu
    clock = pygame.time.Clock()  # Initialise une horloge pour contrôler la vitesse du jeu
    x1 = LARGEUR_ECRAN / 2  # Position initiale en x de la tête du serpent
    y1 = HAUTEUR_ECRAN / 2  # Position initiale en y de la tête du serpent
    x1_change = 0  # Changement initial en x de la tête du serpent
    y1_change = 0  # Changement initial en y de la tête du serpent
    liste_serpent = [(x1, y1)]  # Liste contenant les positions du serpent
    longueur_serpent = 1  # Longueur initiale du serpent
    foodx = round(random.randrange(0, LARGEUR_ECRAN - TAILLE_BLOC) / 10.0) * 10.0  # Position initiale en x de la nourriture
    foody = round(random.randrange(0, HAUTEUR_ECRAN - TAILLE_BLOC) / 10.0) * 10.0  # Position initiale en y de la nourriture
    mort = False  # Indicateur de fin de jeu
    raison = None  # Raison de la fin de jeu

    while not mort:  # Boucle principale du jeu
        for event in pygame.event.get():  # Boucle sur les événements Pygame
            if event.type == pygame.QUIT:  # Si l'utilisateur quitte le jeu
                pygame.quit()  # Quitte Pygame
                quit()  # Quitte le programme

        action = apprenti.agir(liste_serpent, (foodx, foody))  # Obtenir l'action à effectuer

        if action == "gauche":  # Si l'action est de tourner à gauche
            x1_change = -TAILLE_BLOC  # Déplacement horizontal vers la gauche
            y1_change = 0  # Pas de déplacement vertical
        elif action == "droite":  # Si l'action est de tourner à droite
            x1_change = TAILLE_BLOC  # Déplacement horizontal vers la droite
            y1_change = 0  # Pas de déplacement vertical
        elif action == "haut":  # Si l'action est de monter
            y1_change = -TAILLE_BLOC  # Déplacement vertical vers le haut
            x1_change = 0  # Pas de déplacement horizontal
        elif action == "bas":  # Si l'action est de descendre
            y1_change = TAILLE_BLOC  # Déplacement vertical vers le bas
            x1_change = 0  # Pas de déplacement horizontal

        x1 += x1_change  # Met à jour la position en x de la tête du serpent
        y1 += y1_change  # Met à jour la position en y de la tête du serpent
        tete_serpent = (x1, y1)  # Nouvelle position de la tête du serpent
        liste_serpent.append(tete_serpent)  # Ajoute la nouvelle position à la liste du serpent

        if x1 >= LARGEUR_ECRAN or x1 < 0 or y1 >= HAUTEUR_ECRAN or y1 < 0:  # Si le serpent touche les bords de l'écran
            raison = 'Écran'  # La raison de la fin du jeu est le dépassement de l'écran
            mort = True  # Met fin au jeu

        if tete_serpent in liste_serpent[:-1]:  # Si la tête du serpent entre en collision avec son corps
            raison = 'Queue'  # La raison de la fin du jeu est la collision avec la queue
            mort = True  # Met fin au jeu

        if x1 == foodx and y1 == foody:  # Si la tête du serpent mange la nourriture
            foodx = round(random.randrange(0, LARGEUR_ECRAN - TAILLE_BLOC) / 10.0) * 10.0  # Génère une nouvelle position x pour la nourriture
            foody = round(random.randrange(0, HAUTEUR_ECRAN - TAILLE_BLOC) / 10.0) * 10.0  # Génère une nouvelle position y pour la nourriture
            longueur_serpent += 1  # Augmente la longueur du serpent

        if len(liste_serpent) > longueur_serpent:  # Si la longueur du serpent dépasse celle requise
            del liste_serpent[0]  # Supprime la dernière position du serpent pour garder sa longueur constante

        dis.fill(BLEU)  # Remplit l'écran avec la couleur bleue
        dessiner_nourriture(foodx, foody)  # Dessine la nourriture sur l'écran
        dessiner_serpent(liste_serpent)  # Dessine le serpent sur l'écran
        dessiner_score(longueur_serpent - 1)  # Affiche le score sur l'écran
        pygame.display.update()  # Met à jour l'affichage

        apprenti.mise_a_jour_qvaleurs(raison)  # Met à jour les Q-valeurs selon la raison

        clock.tick(VITESSE_FPS)  # Limite le jeu à un certain nombre de FPS

    return longueur_serpent - 1, raison  # Retourne le score final et la raison de la fin du jeu

def dessiner_nourriture(foodx, foody):  # Fonction pour dessiner la nourriture
    pygame.draw.rect(dis, VERT, [foodx, foody, TAILLE_BLOC, TAILLE_BLOC])  # Dessine un rectangle vert pour représenter la nourriture

def dessiner_score(score):  # Fonction pour afficher le score
    font = pygame.font.SysFont("comicsansms", 35)  # Charge une police pour le texte
    valeur = font.render(f"Score: {score}", True, JAUNE)  # Crée une surface avec le texte du score
    dis.blit(valeur, [0, 0])  # Affiche la surface du score à l'angle supérieur gauche de l'écran

def dessiner_serpent(liste_serpent):  # Fonction pour dessiner le serpent
    for x in liste_serpent:  # Boucle sur les positions du serpent
        pygame.draw.rect(dis, NOIR, [x[0], x[1], TAILLE_BLOC, TAILLE_BLOC])  # Dessine un rectangle noir pour chaque partie du serpent

nombre_parties = 1  # Initialise le nombre de parties à 1
max_parties = 20  # Définit le nombre maximal de parties
apprenti = Apprenti(LARGEUR_ECRAN, HAUTEUR_ECRAN, TAILLE_BLOC)  # Initialise l'apprenant

while nombre_parties <= max_parties:  # Boucle tant que le nombre de parties est inférieur ou égal au maximum
    apprenti.reset()  # Réinitialise l'apprenant pour une nouvelle partie
    if nombre_parties > max_parties / 2:  # Si la moitié des parties ont été jouées
        apprenti.epsilon = 0  # Arrête l'exploration
    else:  # Sinon
        apprenti.epsilon = .1  # Continue l'exploration avec un certain taux
    score, raison = boucle_jeu()  # Joue une partie et obtient le score final et la raison de la fin du jeu
    print(f"Parties: {nombre_parties}; Score: {score}; Raison: {raison}")  # Affiche le score et la raison de la partie
    nombre_parties += 1  # Incrémente le nombre de parties pour la prochaine itération

