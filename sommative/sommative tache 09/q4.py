# QUESTION 4 — Dictionnaire inventaire

inventaire = {
    "stylos": 24,
    "cahiers": 15,
    "gommes": 10
}

print("Cahiers en stock :", inventaire["cahiers"])

inventaire["marqueurs"] = 18

inventaire["stylos"] = 30

del inventaire["gommes"]

print("\n--- Inventaire actuel ---")
for produit, quantite in inventaire.items():
    print(f"  {produit:<12} : {quantite} unités")

total = sum(inventaire.values())
print(f"\nTotal en stock : {total} articles")
