with open("valeurs.txt", "r") as fichier, \
     open("bas.txt", "w") as bas, \
     open("haut.txt", "w") as haut:

    for ligne in fichier:
        valeur = int(ligne.strip())

        if valeur < 50000:
            bas.write(str(valeur) + "\n")
        else:
            haut.write(str(valeur) + "\n")

print("Fichiers bas.txt et haut.txt créés.")