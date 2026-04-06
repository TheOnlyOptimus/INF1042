import random

liste = [random.randint(1, 20) for _ in range(100)]

print("Liste originale :", liste)

# Enlever doublons
liste_unique = list(set(liste))

# Trier
liste_triee = sorted(liste_unique)

print("Liste sans doublons triée :", liste_triee)