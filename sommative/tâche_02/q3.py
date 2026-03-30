# Nom : Leo
# Description :
# Ce programme calcule une facture avec rabais selon le montant,
# puis ajoute une taxe (13%).

prix = float(input("Entrez le prix d'achat : "))

# Calcul du rabais
if prix < 50:
    rabais = 0
elif prix <= 100:
    rabais = 0.10
else:
    rabais = 0.15

montant_rabais = prix * rabais
sous_total = prix - montant_rabais

# Taxe (13%)
taxe = sous_total * 0.13
total = sous_total + taxe

# Affichage
print("Prix initial :", prix)
print("Rabais appliqué :", montant_rabais)
print("Sous-total :", sous_total)
print("Taxe :", taxe)
print("Total :", total)