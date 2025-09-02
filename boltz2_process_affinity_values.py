#!/usr/bin/env python3
"""
boltz_affinity_extract.py — Extract affinity values and derived metrics from Boltz‑2 JSONs, sorted by affinity probability.
"""

import os
import json
import csv
import glob
import math

BASE_DIR = "/ibex/scratch/projects/c2296/FUT6_dimmer_models/boltz_FUT6_VS"
OUTPUT_CSV = os.path.join(BASE_DIR, "affinity_results.csv")

all_rows = []

for compound_dir in glob.glob(os.path.join(BASE_DIR, "boltz_results_FUT6_monomer_*")):
    predictions_root = os.path.join(compound_dir, "predictions")
    if not os.path.isdir(predictions_root):
        continue

    affinity_jsons = glob.glob(os.path.join(predictions_root, "FUT6_monomer_*", "affinity_FUT6_monomer_*.json"))
    for aff_path in affinity_jsons:
        try:
            with open(aff_path) as f:
                data = json.load(f)

            affinity_val = float(data.get("affinity_pred_value", float('nan')))
            prob_val = float(data.get("affinity_probability_binary", float('nan')))

            ic50_uM = 10 ** affinity_val
            ic50_M = 10 ** (affinity_val - 6)
            pIC50 = 6 - affinity_val
            deltaG = 1.364 * (affinity_val - 6)

            row = {
                "compound_dir": os.path.basename(compound_dir),
                "affinity_probability_binary": prob_val,
                "affinity_pred_value": affinity_val,
                "IC50_uM": ic50_uM,
                "IC50_M": ic50_M,
                "pIC50": pIC50,
                "deltaG_kcalmol": deltaG
            }
            all_rows.append(row)
        except Exception as e:
            print(f"Error parsing {aff_path}: {e}")

# Sort rows by probability (descending)
all_rows = sorted(all_rows, key=lambda x: x["affinity_probability_binary"], reverse=True)

# Write to CSV
headers = ["compound_dir", "affinity_probability_binary", "affinity_pred_value", "IC50_uM", "IC50_M", "pIC50", "deltaG_kcalmol"]
with open(OUTPUT_CSV, 'w', newline='') as f_csv:
    writer = csv.DictWriter(f_csv, fieldnames=headers)
    writer.writeheader()
    for row in all_rows:
        writer.writerow(row)

print(f"Done. Sorted results saved to: {OUTPUT_CSV}")

