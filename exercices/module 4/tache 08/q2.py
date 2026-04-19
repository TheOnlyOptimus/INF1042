import pandas as pd

df = pd.read_csv("nba_players.csv")

# Compter le nombre de joueurs par position
print("=== Nombre de joueurs par position ===")
compte_positions = df["Pos"].value_counts()
print(compte_positions)

# Affichage formaté
print("\n--- Détail ---")
for position, nombre in compte_positions.items():
    print(f"  {position} : {nombre} joueur(s)")
