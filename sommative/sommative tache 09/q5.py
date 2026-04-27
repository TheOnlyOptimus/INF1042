# QUESTION 5 — Club scolaire

eleves = [
    {"nom": "Ava",   "niveau": 12, "activites": ["programmation", "robotique", "mathématiques"]},
    {"nom": "Noah",  "niveau": 11, "activites": ["robotique", "arts"]},
    {"nom": "Liam",  "niveau": 12, "activites": ["programmation", "robotique", "échecs", "mathématiques"]},
    {"nom": "Sofia", "niveau": 10, "activites": ["arts", "mathématiques"]}
]

print("--- Élèves ---")
for eleve in eleves:
    print(f"  {eleve['nom']}")

print("\n--- Élèves de 12e année ---")
for eleve in eleves:
    if eleve["niveau"] == 12:
        print(f"  {eleve['nom']}")

activites_uniques = set()
for eleve in eleves:
    activites_uniques.update(eleve["activites"])
print("\nActivités offertes :", activites_uniques)

top_eleve = max(eleves, key=lambda e: len(e["activites"]))
print(f"\nÉlève le plus actif : {top_eleve['nom']} ({len(top_eleve['activites'])} activités)")

nb_robotique = sum(1 for e in eleves if "robotique" in e["activites"])
print(f"Élèves en robotique : {nb_robotique}")
