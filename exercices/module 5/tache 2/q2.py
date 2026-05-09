# Question 2 — Calcul d'une moyenne

try:
    note1 = float(input("Note 1 : "))
    note2 = float(input("Note 2 : "))

    if note1 < 0 or note1 > 100 or note2 < 0 or note2 > 100:
        raise ValueError("Erreur : les notes doivent être entre 0 et 100.")

except ValueError as e:
    # Couvre à la fois float() invalide ET le raise ci-dessus
    if "could not convert" in str(e) or "invalid literal" in str(e):
        print("Erreur : les notes doivent être numériques.")
    else:
        print(e)

else:
    moyenne = (note1 + note2) / 2
    print(f"La moyenne est : {moyenne:.2f}")

finally:
    print("Fin du programme.")
