while True:
    try:
        a = float(input("Entrez la première valeur : "))
        b = float(input("Entrez la deuxième valeur : "))
        break
    except:
        print("Veuillez entrer des nombres valides.")

produit = a * b
difference = a - b

print("Produit :", produit)
print("Différence :", difference)