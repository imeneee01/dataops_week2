import pandas as pd
from pathlib import Path
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.clean_data import clean_orders

# Chemins absolus
data_dir = Path("./data")

input_file = data_dir / "raw" / "orders_dirty_v1.csv"

output_dir = data_dir / "processed"
output_dir.mkdir(parents=True, exist_ok=True)

report_dir = data_dir / "reports"
report_dir.mkdir(parents=True, exist_ok=True)

# Lecture
df = pd.read_csv(input_file)

# Nettoyage
df_clean = clean_orders(df)

# Fichiers de sortie
output_file = output_dir / "orders_clean_v1.csv"
report_file = report_dir / "orders_report_v1.txt"

# Sauvegarde CSV
df_clean.to_csv(output_file, index=False)

# Rapport simple
with open(report_file, "w") as f:
    f.write(f"Fichier nettoyé : {output_file.name}\n")
    f.write(f"Lignes initiales : {len(df)}\n")
    f.write(f"Lignes finales : {len(df_clean)}\n")
    f.write(f"Lignes supprimées : {len(df) - len(df_clean)}\n")

print(f"{output_file.name} → {len(df)} lignes initiales, "
      f"{len(df) - len(df_clean)} supprimées")