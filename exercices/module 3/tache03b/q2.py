def peut_entrer(age):
    return age >= 18

age = int(input("Entrez votre âge : "))

if peut_entrer(age):
    print("Vous pouvez entrer dans le club.")
else:
    print("Entrée refusée.")