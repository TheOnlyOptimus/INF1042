import pandas as pd

df = pd.read_csv("nba_players.csv")

# Calculer moyenne, max et min du salaire par position
stats_salaire = df.groupby("Pos")["Salary"].agg(
    Moyenne="mean",
    Maximum="max",
    Minimum="min"
).round(2)

print("=== Salaire par position (Moyenne / Max / Min) ===")
print(stats_salaire.to_string())

# Affichage formaté
print("\n--- Détail lisible ---")
for pos, ligne in stats_salaire.iterrows():
    print(f"\nPosition : {pos}")
    print(f"  Moyenne : ${ligne['Moyenne']:>15,.2f}")
    print(f"  Maximum : ${ligne['Maximum']:>15,.2f}")
    print(f"  Minimum : ${ligne['Minimum']:>15,.2f}")
