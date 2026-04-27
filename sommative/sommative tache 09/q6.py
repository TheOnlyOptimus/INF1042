# QUESTION 6 — Magasin de jeux vidéo

achats = [
    ("Liam",   "Galaxy Battle", "PC",          59.99),
    ("Emma",   "Speed Zone",    "PlayStation", 49.99),
    ("Liam",   "Pixel Quest",   "Switch",      39.99),
    ("Noah",   "Galaxy Battle", "PC",          59.99),
    ("Emma",   "Sky Builder",   "PC",          29.99),
    ("Olivia", "Speed Zone",    "Xbox",        54.99),
    ("Liam",   "Sky Builder",   "PC",          29.99),
    ("Noah",   "Pixel Quest",   "Switch",      39.99),
]

print("--- Tous les achats ---")
for client, jeu, plateforme, prix in achats:
    print(f"  {client:<8} | {jeu:<16} | {plateforme:<12} | {prix:.2f} $")

jeux_uniques = {achat[1] for achat in achats}
print("\nJeux uniques :", jeux_uniques)

plateformes_uniques = {achat[2] for achat in achats}
print("Plateformes :", plateformes_uniques)

total_global = sum(achat[3] for achat in achats)
print(f"\nTotal dépensé : {total_global:.2f} $")

depenses_client = {}
for client, jeu, plateforme, prix in achats:
    depenses_client[client] = depenses_client.get(client, 0) + prix

print("\n--- Dépenses par client ---")
for client, montant in depenses_client.items():
    print(f"  {client:<8} : {montant:.2f} $")

top_client = max(depenses_client, key=depenses_client.get)
print(f"\nClient qui a le plus dépensé : {top_client} ({depenses_client[top_client]:.2f} $)")

achats_par_jeu = {}
for client, jeu, plateforme, prix in achats:
    achats_par_jeu[jeu] = achats_par_jeu.get(jeu, 0) + 1

print("\n--- Achats par jeu ---")
for jeu, nb in achats_par_jeu.items():
    print(f"  {jeu:<16} : {nb} fois")

print("\n--- Achats sur PC ---")
for client, jeu, plateforme, prix in achats:
    if plateforme == "PC":
        print(f"  {client} — {jeu} ({prix:.2f} $)")

jeu_populaire = max(achats_par_jeu, key=achats_par_jeu.get)

print("\n=== RÉSUMÉ FINAL ===")
print(f"  Nombre total d'achats : {len(achats)}")
print(f"  Jeux uniques          : {jeux_uniques}")
print(f"  Plateformes uniques   : {plateformes_uniques}")
print(f"  Meilleur client       : {top_client} ({depenses_client[top_client]:.2f} $)")
print(f"  Jeu le plus acheté    : {jeu_populaire} ({achats_par_jeu[jeu_populaire]} fois)")
