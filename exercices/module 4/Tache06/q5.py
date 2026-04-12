# Affiche les élèves spécifiques entre deux groupes

eleves_A = {"Mia", "Noah", "Liam", "Zoe"}
eleves_B = {"Zoe", "Emma", "Liam", "Olivier"}

# Élèves seulement dans A
print("Seulement A :", eleves_A - eleves_B)

# Différence symétrique (éléments dans un seul des deux groupes)
print("Différence symétrique :", eleves_A ^ eleves_B)