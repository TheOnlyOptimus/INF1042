# Nom : Leo Charron
# Description :
# Jeu pierre-papier-ciseaux contre l’ordinateur avec score.

import random

victoires = 0
defaites = 0

while True:
    choix_user = input("Choisissez pierre, papier ou ciseaux : ").lower()
    
    choix_ordi = random.choice(["pierre", "papier", "ciseaux"])
    
    print("Ordinateur :", choix_ordi)

    if choix_user == choix_ordi:
        print("Égalité")
    elif (choix_user == "pierre" and choix_ordi == "ciseaux") or \
         (choix_user == "papier" and choix_ordi == "pierre") or \
         (choix_user == "ciseaux" and choix_ordi == "papier"):
        print("Gagné")
        victoires += 1
    else:
        print("Perdu")
        defaites += 1

    print("Score - Victoires :", victoires, "| Défaites :", defaites)

    continuer = input("Continuer ? (oui/non) : ").lower()
    if continuer != "oui":
        break