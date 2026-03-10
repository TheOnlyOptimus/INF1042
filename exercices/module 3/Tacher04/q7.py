a = float(input("Longueur 1 : "))
b = float(input("Longueur 2 : "))
c = float(input("Longueur 3 : "))

triangle = (a + b > c) and (a + c > b) and (b + c > a)

print(triangle)