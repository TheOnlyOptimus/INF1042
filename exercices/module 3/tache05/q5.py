notes = []

while True:
    print("\n--- MENU ---")
    print("1. Entrer plusieurs notes")
    print("2. Calculer la moyenne")
    print("3. Compter les notes de réussite (>= 50)")
    print("4. Compter les notes d’échec (< 50)")
    print("5. Quitter")

    choix = input("Choisissez une option : ")

    if choix == "1":
        nb = int(input("Combien de notes voulez-vous entrer ? "))
        
        for i in range(nb):
            note = float(input(f"Entrez la note {i+1} : "))
            notes.append(note)

    elif choix == "2":
        if len(notes) > 0:
            moyenne = sum(notes) / len(notes)
            print("Moyenne :", moyenne)
        else:
            print("Aucune note entrée.")

    elif choix == "3":
        reussites = 0
        for note in notes:
            if note >= 50:
                reussites += 1
        print("Nombre de réussites :", reussites)

    elif choix == "4":
        echecs = 0
        for note in notes:
            if note < 50:
                echecs += 1
        print("Nombre d’échecs :", echecs)

    elif choix == "5":
        print("Programme terminé.")
        break

    else:
        print("Choix invalide.")