import pandas as pd

df = pd.read_csv("nba_players.csv")

# -------------------------------------------------------
# Formule :
#   total_points  = PPG × GP (matches joués)
#   cout_par_point = Salary / total_points
# -------------------------------------------------------

# Calculer le total de points marqués dans la saison
df["Total_Points"] = df["PPG"] * df["GP"]

# Éviter la division par zéro (joueurs sans points)
df_actifs = df[df["Total_Points"] > 0].copy()

# Calculer le coût associé à chaque point
df_actifs["Cout_par_Point"] = df_actifs["Salary"] / df_actifs["Total_Points"]

# Trier et garder les 5 plus chers
top5 = df_actifs.nlargest(5, "Cout_par_Point")[
    ["Player", "Team", "PPG", "GP", "Total_Points", "Salary", "Cout_par_Point"]
].reset_index(drop=True)
top5.index += 1

print("=== 🏆 DÉFI — Top 5 joueurs les plus chers par point marqué ===\n")
print(f"{'#':<3} {'Joueur':<25} {'Équipe':<6} {'PPG':>5} {'GP':>4} "
      f"{'Pts total':>10} {'Salaire ($)':>14} {'$/Point':>12}")
print("-" * 82)

for rang, row in top5.iterrows():
    print(
        f"{rang:<3} {row['Player']:<25} {row['Team']:<6} "
        f"{row['PPG']:>5.1f} {row['GP']:>4.0f} "
        f"{row['Total_Points']:>10.1f} "
        f"${row['Salary']:>13,.0f} "
        f"${row['Cout_par_Point']:>11,.2f}"
    )

print("\n💡 Interprétation : un '$/Point' élevé signifie que l'équipe")
print("   paie très cher pour chaque point que ce joueur produit.")
