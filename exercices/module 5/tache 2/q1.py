# Question 1 — Âge valide

try:
    valeur = input("Entrez votre âge : ")
    age = int(valeur)           # lève ValueError si non convertible
except ValueError:
    raise ValueError("Erreur : l'âge doit être un nombre entier.")
else:
    print(f"Vous avez {age} ans.")
