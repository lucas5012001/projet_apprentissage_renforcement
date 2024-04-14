Projet snake

Julien, Eric, Maxence, Lucas, Lucas

Règles du jeu :
###############

- Si le serpent mange un carré rouge, il gagne un point, sa taille augmente de 1 et une bombe apparait, 
dans la limite de 10 bombes.

- Si le serpent mange un carré bleu, il perd un point et sa taille augmente de 1

- Si le serpent se mange lui même ou sort de l'écran, la partie est terminée


UTILISATION :
#############

Dans le dossier app :

- Pour jouer, lancer jeu_humain.py
- Pour tester le modèle déja entrainé, utiliser jeu_Qlearning_pretrain.py (poids déja entrainés)
- Pour voir l'algorithme de Q-learning progresser, lancer jeu_Qlearning.py
- Pour entrainer le modèle, lancer train.py
- Pour optimiser les hyperparamètres, lancer optim_hyperparametres.py avec les valeurs à tester souhaitées. (déjà optimisé)