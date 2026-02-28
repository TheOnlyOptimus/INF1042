temperature = float(input("Température : "))
pluie = input("Pleut-il ? (oui/non) : ")

if temperature >= 15 and pluie.lower() == "non":
    print("Sortie permise")
else:
    print("On reste dedans")