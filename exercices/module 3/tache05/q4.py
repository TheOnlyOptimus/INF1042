def valider_mot_de_passe(mdp):
    contient_chiffre = False
    contient_lettre = False

    for caractere in mdp:
        if caractere.isdigit():
            contient_chiffre = True
        if caractere.isalpha():
            contient_lettre = True

    if len(mdp) >= 8 and contient_chiffre and contient_lettre:
        return True
    else:
        return False


# Test
mot_de_passe = input("Entrez un mot de passe : ")

print(valider_mot_de_passe(mot_de_passe))