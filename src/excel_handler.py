import pandas as pd
import os
import json
from datetime import datetime

def save_results_sectionwise(results_dict, out_base, source_image_name, sections):
    section_data = {}
    for section, qrange in sections:
        rows = []
        for q in qrange:
            opts = results_dict.get(q, [])
            ans = ",".join(opts) if opts else ""
            rows.append(f"{q} - {ans}")
        section_data[section] = rows
    max_len = max(len(rows) for rows in section_data.values())
    for key in section_data:
        if len(section_data[key]) < max_len:
            section_data[key] += [""] * (max_len - len(section_data[key]))
    df = pd.DataFrame(section_data)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(os.path.basename(source_image_name))[0]
    out_dir = os.path.join(out_base, "excel")
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, f"{base_name}_results_{timestamp}.csv")
    xlsx_path = os.path.join(out_dir, f"{base_name}_results_{timestamp}.xlsx")
    json_path = os.path.join(out_dir, f"{base_name}_results_{timestamp}.json")
    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False)
    with open(json_path,"w") as f:
        json.dump({"source_image": source_image_name, "generated_at": timestamp, "answers": section_data}, f, indent=2)
    print(f"[OK] Saved CSV: {csv_path}")
    print(f"[OK] Saved XLSX: {xlsx_path}")
    print(f"[OK] Saved JSON: {json_path}")
    return {"csv": csv_path, "xlsx": xlsx_path, "json": json_path}
