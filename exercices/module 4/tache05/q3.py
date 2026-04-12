# Convertit un tuple en liste, modifie un élément, puis reconvertit en tuple

t = (1, 2, 3)

liste = list(t)

liste[1] = 99

t = tuple(liste)

print("Nouveau tuple :", t)