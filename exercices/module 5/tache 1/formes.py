import math

# =============================================================
# CLASSE DE BASE — Forme
# =============================================================
# C'est la classe "parent". Toutes les formes héritent d'elle.
# Elle accepte un paramètre : longueur (le côté ou le rayon).
# Les méthodes aire() et périmètre() sont définies ici mais
# laissées vides avec pass — chaque sous-classe les redéfinira.
# =============================================================

class Forme:
    def __init__(self, longueur):
        self.longueur = longueur  # longueur du côté (ou rayon pour le cercle)

    def aire(self):
        pass  # redéfini dans chaque sous-classe

    def perimetre(self):
        pass  # redéfini dans chaque sous-classe

    def __str__(self):
        # Affichage automatique quand on fait print(forme)
        # self.__class__.__name__ donne le nom de la sous-classe (ex: "Cercle")
        return (f"{self.__class__.__name__} (longueur={self.longueur})\n"
                f"  Aire      : {self.aire():.4f}\n"
                f"  Périmètre : {self.perimetre():.4f}")


# =============================================================
# CERCLE  —  longueur = rayon (r)
# Périmètre : C = 2 * π * r
# Aire      : A = π * r²
# =============================================================

class Cercle(Forme):
    def aire(self):
        return math.pi * self.longueur ** 2

    def perimetre(self):
        return 2 * math.pi * self.longueur


# =============================================================
# TRIANGLE ÉQUILATÉRAL  —  longueur = côté (c)
# Périmètre : P = 3c
# Aire      : A = (√3 / 4) * c²
# =============================================================

class Triangle(Forme):
    def aire(self):
        return (math.sqrt(3) / 4) * self.longueur ** 2

    def perimetre(self):
        return 3 * self.longueur


# =============================================================
# RECTANGLE RÉGULIER (CARRÉ)  —  longueur = côté (c)
# Périmètre : P = 4c
# Aire      : A = c²
# =============================================================

class Rectangle(Forme):
    def aire(self):
        return self.longueur ** 2

    def perimetre(self):
        return 4 * self.longueur


# =============================================================
# PENTAGONE RÉGULIER  —  longueur = côté (c)
# Périmètre : P = 5c
# Aire      : A = 5c² / (4 * tan(π/5))
# =============================================================

class Pentagon(Forme):
    def aire(self):
        return (5 * self.longueur ** 2) / (4 * math.tan(math.pi / 5))

    def perimetre(self):
        return 5 * self.longueur


# =============================================================
# HEXAGONE RÉGULIER  —  longueur = côté (c)
# Périmètre : P = 6c
# Aire      : A = (3√3 / 2) * c²
# =============================================================

class Hexagon(Forme):
    def aire(self):
        return (3 * math.sqrt(3) / 2) * self.longueur ** 2

    def perimetre(self):
        return 6 * self.longueur


# =============================================================
# HEPTAGONE RÉGULIER  —  longueur = côté (c)
# Périmètre : P = 7c
# Aire      : A = 7c² / (4 * tan(π/7))
# =============================================================

class Heptagon(Forme):
    def aire(self):
        return (7 * self.longueur ** 2) / (4 * math.tan(math.pi / 7))

    def perimetre(self):
        return 7 * self.longueur


# =============================================================
# OCTOGONE RÉGULIER  —  longueur = côté (c)
# Périmètre : P = 8c
# Aire      : A = 2(1 + √2) * c²
# =============================================================

class Octagon(Forme):
    def aire(self):
        return 2 * (1 + math.sqrt(2)) * self.longueur ** 2

    def perimetre(self):
        return 8 * self.longueur


# =============================================================
# TEST — créer une instance de chaque forme avec longueur = 5
# et afficher les résultats
# =============================================================

formes = [
    Cercle(5),
    Triangle(5),
    Rectangle(5),
    Pentagon(5),
    Hexagon(5),
    Heptagon(5),
    Octagon(5),
]

print("=" * 45)
print("   RÉSULTATS — toutes les formes (côté = 5)")
print("=" * 45)

for forme in formes:
    print(forme)
    print("-" * 45)
