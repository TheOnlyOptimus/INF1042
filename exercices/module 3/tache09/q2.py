import random
import time

# Demande du nombre de questions
nb_questions = int(input("Combien de questions voulez-vous ? "))

bonnes_reponses = 0
mauvaises_reponses = 0
temps_total = 0

operations = ["+", "-", "*", "/"]

for i in range(nb_questions):
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    op = random.choice(operations)

    # Évite division par 0 et résultats compliqués
    if op == "/":
        a = a * b  # assure un résultat entier

    question = f"{a} {op} {b} = ?"
    print("\nQuestion", i + 1, ":", question)

    # Début du temps
    debut = time.time()

    reponse = float(input("Votre réponse : "))

    # Fin du temps
    fin = time.time()
    duree = fin - debut
    temps_total += duree

    # Vérification
    if op == "+":
        correcte = a + b
    elif op == "-":
        correcte = a - b
    elif op == "*":
        correcte = a * b
    elif op == "/":
        correcte = a / b

    if reponse == correcte:
        print("Correct !")
        bonnes_reponses += 1
    else:
        print("Incorrect. Réponse :", correcte)
        mauvaises_reponses += 1

# Résultats finaux
print("\n--- Résultats ---")
print("Bonnes réponses :", bonnes_reponses)
print("Mauvaises réponses :", mauvaises_reponses)
print("Temps total :", round(temps_total, 2), "secondes")