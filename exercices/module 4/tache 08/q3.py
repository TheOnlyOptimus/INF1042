import pandas as pd

df = pd.read_csv("nba_players.csv")

# Filtrer les joueurs avec moins de 5 points par match
low_scorers = df[df["PPG"] < 5]

print("=== Joueurs avec PPG < 5 ===")
print(low_scorers[["Player", "Pos", "Team", "PPG"]])
print(f"\nNombre de joueurs concernés : {len(low_scorers)}")

# Exporter vers un nouveau fichier CSV
low_scorers.to_csv("low_scorers.csv", index=False)
print("\n✅ Fichier 'low_scorers.csv' exporté avec succès.")
