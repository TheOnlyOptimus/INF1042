pointes = int(input("Nombre total de pointes : "))
eleves = int(input("Nombre d'élèves : "))

par_eleve = pointes // eleves
reste = pointes % eleves

print("Chaque élève reçoit :", par_eleve, "pointes")
print("Pointes restantes :", reste)