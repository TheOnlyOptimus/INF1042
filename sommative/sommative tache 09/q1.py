# QUESTION 1 — Liste de notes

notes = [78, 85, 92, 67, 85, 74]

print("Liste complète :", notes)

print("Première note :", notes[0])
print("Dernière note :", notes[-1])

notes.append(88)

notes.remove(85)

print("Liste mise à jour :", notes)

total   = sum(notes)
moyenne = total / len(notes)   
maximum = max(notes)
minimum = min(notes)

print(f"Total   : {total}")
print(f"Moyenne : {moyenne:.2f}")
print(f"Maximum : {maximum}")
print(f"Minimum : {minimum}")
