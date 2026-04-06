panier = ["pomme", "banane", "orange", "banane"]

panier.insert(1, "kiwi")
panier.remove("banane")  # enlève la première occurrence
dernier = panier.pop()

print("Panier :", panier)
print("Dernier élément retiré :", dernier)