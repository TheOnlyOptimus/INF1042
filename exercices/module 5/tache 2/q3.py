# Question 3 — Retrait bancaire

solde = 250.00
print(f"Solde actuel : {solde:.2f} $")

try:
    valeur = input("Montant à retirer : ")
    montant = float(valeur)

    if montant <= 0:
        raise ValueError("Erreur : le montant doit être supérieur à zéro.")

    if montant > solde:
        raise ValueError("Erreur : fonds insuffisants.")

except ValueError as e:
    if "could not convert" in str(e) or "invalid literal" in str(e):
        print("Erreur : le montant doit être un nombre décimal.")
    else:
        print(e)

else:
    solde -= montant
    print("Retrait accepté.")
    print(f"Nouveau solde : {solde:.2f} $")

finally:
    print("Fin de la transaction.")
