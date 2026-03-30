# Nom : Leo Charron
# Description :
# Ce programme convertit une température en Celsius
# en Fahrenheit et en Kelvin.

celsius = float(input("Entrez une température en Celsius : "))

fahrenheit = (celsius * 9 / 5) + 32
kelvin = celsius + 273.15

print("Fahrenheit :", fahrenheit)
print("Kelvin :", kelvin)