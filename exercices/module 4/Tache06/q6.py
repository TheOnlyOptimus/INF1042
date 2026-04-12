# Sélectionne les élèves au hasard sans répétition

import random

eleves = { "Maksym", "Léo", "Hayden", "Angel", "Ibrahim", "Josh", "Grant", "Maxime", "David" }

# Convertir en liste pour utiliser random
liste = list(eleves)

random.shuffle(liste)

for eleve in liste:
    print(eleve)