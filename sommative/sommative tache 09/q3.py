# QUESTION 3 — Ensembles (sets)

liste_a = ["Batterie", "Basse", "Piano", "Basse", "Guitare", "Batterie"]
liste_b = ["Piano", "Voix", "Guitare", "Synthé", "Piano"]

ensemble_a = set(liste_a)
ensemble_b = set(liste_b)

print("Uniques dans A :", ensemble_a)
print("Uniques dans B :", ensemble_b)

communes = ensemble_a & ensemble_b
print("Dans les deux listes :", communes)

une_seule = ensemble_a ^ ensemble_b
print("Dans une seule liste :", une_seule)

toutes = ensemble_a | ensemble_b
print("Toutes les chansons uniques :", toutes)
