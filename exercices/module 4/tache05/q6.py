# Analyse des résultats de matchs et statistiques des équipes

matchs = (
    ("Tigres", "Lynx", 25, 18),
    ("Aigles", "Panthères", 22, 25),
    ("Tigres", "Panthères", 25, 23),
    ("Lynx", "Aigles", 19, 25),
    ("Tigres", "Aigles", 21, 25),
    ("Lynx", "Panthères", 25, 20)
)

victoires = {}
defaites = {}
points = {}

# Initialiser les équipes
for match in matchs:
    eq1, eq2, _, _ = match
    for eq in (eq1, eq2):
        if eq not in victoires:
            victoires[eq] = 0
            defaites[eq] = 0
            points[eq] = 0

# Analyse des matchs
for eq1, eq2, s1, s2 in matchs:
    
    # Ajouter les points
    points[eq1] += s1
    points[eq2] += s2

    # Déterminer le gagnant
    if s1 > s2:
        print(f"Les {eq1} ont battu les {eq2} par {s1} à {s2}.")
        victoires[eq1] += 1
        defaites[eq2] += 1
    else:
        print(f"Les {eq2} ont battu les {eq1} par {s2} à {s1}.")
        victoires[eq2] += 1
        defaites[eq1] += 1

# Victoires par équipe
print("\nVictoires :")
for eq in victoires:
    print(eq, ":", victoires[eq])

# Équipe avec le plus de victoires
max_v = max(victoires.values())
for eq in victoires:
    if victoires[eq] == max_v:
        print("Équipe avec le plus de victoires :", eq)

# Points totaux
print("\nPoints totaux :")
for eq in points:
    print(eq, ":", points[eq])

# Équipe avec le plus de points
max_p = max(points.values())
for eq in points:
    if points[eq] == max_p:
        print("Équipe avec le plus de points :", eq)

# Analyse victoires vs défaites
print("\nAnalyse finale :")
for eq in victoires:
    if victoires[eq] > defaites[eq]:
        print(eq, ": plus de victoires que de défaites")
    elif victoires[eq] == defaites[eq]:
        print(eq, ": autant de victoires que de défaites")
    else:
        print(eq, ": plus de défaites que de victoires")