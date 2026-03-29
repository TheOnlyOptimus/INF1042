heure = int(input("Entrez une heure (0 à 23) : "))

if heure == 0:
    print("12 AM")
elif heure < 12:
    print(f"{heure} AM")
elif heure == 12:
    print("12 PM")
else:
    print(f"{heure - 12} PM")