mots = ["chat", "chien", "chat", "oiseau", "chien", "chat"]

compte = {}

for mot in mots:
    if mot in compte:
        compte[mot] += 1
    else:
        compte[mot] = 1

print(compte)
