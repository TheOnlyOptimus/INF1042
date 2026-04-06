grille = [[1,2,3],[4,5,6],[7,8,9]]

sommes = []

for ligne in grille:
    somme = sum(ligne)
    sommes.append(somme)

print("Sommes :", sommes)