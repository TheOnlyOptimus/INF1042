notes = [12, 15, 9, 18, 15, 12]

# Moyenne
moyenne = sum(notes) / len(notes)
print("Moyenne :", moyenne)

# Valeur la plus fréquente (sans set)
frequence_max = 0
valeur_frequente = None

for n in notes:
    compteur = 0
    for x in notes:
        if x == n:
            compteur += 1
    
    if compteur > frequence_max:
        frequence_max = compteur
        valeur_frequente = n

print("Valeur la plus fréquente :", valeur_frequente)