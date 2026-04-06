
while True:
    nom = input("Entrez votre nom : ")

    if 8 <= len(nom) <= 12:
        print(f"Bonjour, {nom} !")
        break
    else:
        print("Le nom doit contenir entre 8 et 12 caractères. Réessayez.")