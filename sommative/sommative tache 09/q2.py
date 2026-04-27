# QUESTION 2 — Tuple produit

produit1 = ("Clavier", 49.99, 12)

print("Nom     :", produit1[0])
print("Prix    :", produit1[1])
print("Quantité:", produit1[2])

nom, prix, quantite = produit1

print(f"Le produit {nom} coûte {prix} $ et il y en a {quantite} en stock.")

produit2 = ("Souris", 29.99, 25)

if produit1[1] > produit2[1]:
    print(f"Le produit le plus cher est : {produit1[0]} à {produit1[1]} $")
else:
    print(f"Le produit le plus cher est : {produit2[0]} à {produit2[1]} $")
