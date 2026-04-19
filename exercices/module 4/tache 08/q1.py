import pandas as pd

# Chargement du fichier CSV
# Assurez-vous que le fichier CSV est dans le même dossier que ce script
df = pd.read_csv("nba_players.csv")

# Afficher les 5 premières lignes
print("=== 5 premières lignes du fichier ===")
print(df.head())

# Infos utiles sur le dataset
print(f"\nDimensions : {df.shape[0]} joueurs, {df.shape[1]} colonnes")
print(f"Colonnes   : {list(df.columns)}")
