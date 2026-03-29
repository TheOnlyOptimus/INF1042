import random
import string

# Entrées utilisateur
prenom = input("Entrez votre prénom : ").lower()
nom = input("Entrez votre nom : ").lower()
annee_naissance = int(input("Entrez votre année de naissance : "))
ville = input("Entrez votre ville : ").lower()

# Création du nom d'utilisateur
nom_utilisateur = f"{prenom}.{nom}"

# Création de l'identifiant complet
identifiant = f"{prenom}.{nom}@{ville}.ca"

# Vérification de l'âge (approximation)
age = 2026 - annee_naissance
majeur = age >= 18

# Génération de 4 caractères alphanumériques aléatoires
caracteres = string.ascii_letters + string.digits
random_part = ""
for i in range(4):
    random_part += random.choice(caracteres)

# Création du mot de passe
mot_de_passe = prenom[:2] + nom[-2:] + str(annee_naissance) + random_part

# Affichage
print("\n--- Résultats ---")
print("Nom d'utilisateur :", nom_utilisateur)
print("Identifiant :", identifiant)
print("Âge :", age)
print("Majeur :", majeur)
print("Mot de passe :", mot_de_passe)