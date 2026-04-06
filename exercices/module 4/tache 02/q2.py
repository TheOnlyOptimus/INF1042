valeurs = []

with open("valeurs.txt", "r") as fichier:
    for ligne in fichier:
        valeurs.append(int(ligne.strip()))

maximum = max(valeurs)
minimum = min(valeurs)
moyenne = sum(valeurs) / len(valeurs)

print("Maximum :", maximum)
print("Minimum :", minimum)
print("Moyenne :", moyenne)