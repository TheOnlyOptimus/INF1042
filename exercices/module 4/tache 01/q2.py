nom = input("Entrez votre nom : ")

while True:
    age_input = input("Entrez votre âge : ")

    if age_input.isdigit():
        age = int(age_input)
        break
    else:
        print("Veuillez entrer un âge valide (nombre entier).")

print(f"{nom}, dans 5 ans, tu auras {age + 5} ans.")