# Nom : Leo Charron
# Description :
# Ce programme calcule le coût du stationnement selon les règles données.

heures = int(input("Nombre d'heures stationnées : "))
electrique = input("Voiture électrique ? (oui/non) : ").lower()

# Calcul du coût
if heures >= 1:
    cout = 4
    if heures > 1:
        cout += (heures - 1) * 3
else:
    cout = 0

# Frais supplémentaire
if heures > 5:
    cout += 10

# Rabais électrique
if electrique == "oui":
    cout *= 0.8

print("Coût total du stationnement :", cout, "$")