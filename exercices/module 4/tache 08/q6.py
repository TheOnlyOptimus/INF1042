import pandas as pd

df = pd.read_csv("nba_players.csv")

# Compter les joueurs par équipe ET par pays
repartition = df.groupby(["Team", "Country"])["Player"].count().reset_index()
repartition.columns = ["Équipe", "Pays", "Nombre de joueurs"]

print("=== Répartition des joueurs par pays pour chaque équipe ===\n")

# Afficher équipe par équipe
for equipe, groupe in repartition.groupby("Équipe"):
    print(f"🏀 {equipe}")
    for _, ligne in groupe.iterrows():
        print(f"   {ligne['Pays']:<20} : {ligne['Nombre de joueurs']} joueur(s)")
    print()
