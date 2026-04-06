import random

with open("valeurs.txt", "w") as fichier:
    for i in range(1000):
        nombre = random.randint(0, 100000)
        fichier.write(str(nombre) + "\n")

print("Fichier valeurs.txt créé avec 1000 valeurs.")