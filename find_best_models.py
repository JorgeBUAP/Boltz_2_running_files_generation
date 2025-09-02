import os
import json
import csv
import glob

BASE_DIR = "/ibex/scratch/projects/c2296/FUT6_dimmer_models/boltz_FUT6_VS"
OUTPUT_BEST_LIST = os.path.join(BASE_DIR, "best_models.txt")
OUTPUT_CSV = os.path.join(BASE_DIR, "best_models.csv")

all_rows = []
csv_headers = set()
best_lines = []

for compound_dir in glob.glob(os.path.join(BASE_DIR, "boltz_results_FUT6_monomer_*")):
    predictions_root = os.path.join(compound_dir, "predictions")
    if not os.path.isdir(predictions_root):
        continue

    # Find all confidence JSONs in all predictions/*/ subdirs
    confidence_jsons = glob.glob(os.path.join(predictions_root, "FUT6_monomer_*", "confidence_FUT6_monomer_*.json"))
    best_json = None
    best_score = None
    best_json_path = None

    for conf_path in confidence_jsons:
        try:
            with open(conf_path) as f:
                data = json.load(f)
            # Only consider top-level numeric fields for scoring
            numeric_vals = [v for v in data.values() if isinstance(v, (float, int))]
            if not numeric_vals:
                continue
            avg_score = sum(numeric_vals) / len(numeric_vals)
            if best_score is None or avg_score > best_score:
                best_score = avg_score
                best_json = data
                best_json_path = conf_path
        except Exception as e:
            print(f"Error parsing {conf_path}: {e}")

    if best_json:
        # Prepare output row
        row = {}
        row['compound_dir'] = os.path.basename(compound_dir)
        row['best_model_json'] = os.path.basename(best_json_path)
        for k, v in best_json.items():
            row[k] = v
            csv_headers.add(k)
        all_rows.append(row)
        best_lines.append(f"{os.path.basename(compound_dir)},{os.path.basename(best_json_path)}")

# Write CSV output with sorted headers for consistency
ordered_headers = ['compound_dir', 'best_model_json'] + sorted(list(csv_headers))
with open(OUTPUT_CSV, 'w', newline='') as f_csv:
    writer = csv.DictWriter(f_csv, fieldnames=ordered_headers)
    writer.writeheader()
    for row in all_rows:
        writer.writerow(row)

# Write best models list
with open(OUTPUT_BEST_LIST, 'w') as f_txt:
    for line in best_lines:
        f_txt.write(line + '\n')

print(f"Done. Results in:\n  {OUTPUT_BEST_LIST}\n  {OUTPUT_CSV}")

