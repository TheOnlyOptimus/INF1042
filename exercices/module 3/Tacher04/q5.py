code = input("Entrez un code postal (ex: L8P 1A1) : ")

valide = (
    len(code) == 7 and
    code[3] == " " and
    code[0].isalpha() and
    code[1].isdigit() and
    code[2].isalpha() and
    code[4].isdigit() and
    code[5].isalpha() and
    code[6].isdigit()
)

print(valide)