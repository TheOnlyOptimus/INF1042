import calcul
from affichage import bonjour

monVal = 9

def hello(): 
    print('Bienvenue !')

def separateur():
    for i in range(50):
        print('*', end='') 
        print()

def returnVal(val):
    return val * 10

def monFonc():
    # global monVal
    print(monVal)
    monVal = monVal + 1
    print(monVal)

def f1():
    print("Je suis la fonction 1")

def f2():
    print("Je suis la fonction 2") 

def f3():
    print("Je suis la fonction 3") 
    f1()
    f2()

# f3()

# separateur() 
# hello() 
# separateur()

# print(returnVal(2))

# monFonc()
# print(monVal)

bonjour()
print(calcul.addition(3,4))