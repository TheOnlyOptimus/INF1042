import pandas as pd

df = pd.read_csv("nba_players.csv")

# Trier par salaire décroissant et garder les 10 premiers
top10_salaires = df.nlargest(10, "Salary")[["Player", "Team", "Salary"]]

# Réinitialiser l'index pour un affichage propre
top10_salaires = top10_salaires.reset_index(drop=True)
top10_salaires.index += 1  # Commencer à 1

print("=== Top 10 des plus hauts salaires ===")
print(f"{'#':<4} {'Joueur':<25} {'Équipe':<6} {'Salaire ($)'}")
print("-" * 50)

for rang, ligne in top10_salaires.iterrows():
    salaire_fmt = f"{ligne['Salary']:,.0f}"
    print(f"{rang:<4} {ligne['Player']:<25} {ligne['Team']:<6} ${salaire_fmt}")
