import csv
import json
import os
from collections import Counter

TARGET_YEAR = "2021"

input_csv_file = "Global_Cybersecurity_Threats_2015-2024.csv"
filtered_csv_file = "filtered_incidents.csv"
json_summary_file = "top_incidents.json"
json_backup_file = "top_incidents_backup.json"
text_report_file = "incident_report.txt"

total_dataset_records = 0
target_year_incidents = []
attack_type_counter = Counter()

total_financial_loss = 0.0

with open(input_csv_file, mode="r", encoding="utf-8", errors="ignore") as infile:
    reader = csv.DictReader(infile)
    
    fieldnames = reader.fieldnames
    
    for row in reader:
        total_dataset_records += 1

        incident_year = row.get("Year", "").strip()
        
        if incident_year == TARGET_YEAR:
            attack_type = row.get("Attack Type", "Unknown").strip()
            attack_type_counter[attack_type] += 1
            
            try:
                loss_val = float(row.get("Financial Loss (in Million $)", 0))
            except ValueError:
                loss_val = 0.0
                
            total_financial_loss += loss_val
            
            row["_original_index"] = total_dataset_records
            row["_parsed_loss"] = loss_val
            target_year_incidents.append(row)

matching_count = len(target_year_incidents)
avg_financial_loss = (total_financial_loss / matching_count) if matching_count > 0 else 0.0

sorted_incidents = sorted(
    target_year_incidents,
    key=lambda x: (-x["_parsed_loss"], x["_original_index"])
)
five_costliest = sorted_incidents[:5]

for item in target_year_incidents:
    item.pop("_original_index", None)
    item.pop("_parsed_loss", None)

with open(json_summary_file, mode="w", encoding="utf-8") as json_file:
    json.dump(five_costliest, json_file, indent=4)

with open(filtered_csv_file, mode="w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in target_year_incidents:
        writer.writerow(row)

with open(json_summary_file, mode="r", encoding="utf-8") as src, \
     open(json_backup_file, mode="w", encoding="utf-8") as bkp:
    bkp.write(src.read())

backup_verified = "PASSED" if os.path.exists(json_backup_file) else "FAILED"

report_content = f"""CYBERSECURITY INCIDENT REPORT
=====================================================
Target Year: {TARGET_YEAR}
Total Records in Dataset: {total_dataset_records}
Total Incidents in Target Year: {matching_count}
Total Financial Loss (USD Millions): ${total_financial_loss:,.2f}
Average Financial Loss (USD Millions): ${avg_financial_loss:,.2f}

Count Per Attack Type:
-----------------------------------------------------
"""
for attack, count in attack_type_counter.items():
    report_content += f"- {attack}: {count}\n"

report_content += """
Top 5 Costliest Incidents:
-----------------------------------------------------
"""
for idx, inc in enumerate(five_costliest, start=1):
    report_content += f"{idx}. Type: {inc.get('Attack Type') or 'N/A'} | Loss: ${inc.get('Financial Loss (in Million $)')}M\n"

report_content += f"""
Output Metadata Verification:
-----------------------------------------------------
Filtered CSV Generated: {filtered_csv_file}
JSON Summary Generated: {json_summary_file}
Backup Status: {backup_verified}
"""

with open(text_report_file, mode="w", encoding="utf-8") as report_file:
    report_file.write(report_content)

print(report_content)
print("=" * 53)
print("Execution Completed Successfully.")