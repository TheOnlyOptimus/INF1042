n = int(input("Entrez un nombre entier : "))

if n % 3 == 0 and n % 5 == 0:
    print("Divisible par 3 et 5")
elif n % 3 == 0:
    print("Divisible par 3")
elif n % 5 == 0:
    print("Divisible par 5")
else:
    print("Non divisible par 3 ni 5")