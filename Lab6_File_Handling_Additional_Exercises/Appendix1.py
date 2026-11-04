import csv
import json
import os
from collections import Counter

TOTAL_RECORDS_TO_PROCESS = 1022 
TARGET_CLASS_PREFIX = "4"

input_csv_file = "weblog.csv"
filtered_csv_file = "filtered_weblog.csv"
json_summary_file = "summary.json"
json_backup_file = "summary_backup.json"

processed_count = 0
records_in_target_class = 0
status_code_counter = Counter()
url_counter = Counter()

with open(input_csv_file, mode="r", encoding="utf-8", errors="ignore") as infile, \
     open(filtered_csv_file, mode="w", newline="", encoding="utf-8") as outfile:
    
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in reader:
        if processed_count >= TOTAL_RECORDS_TO_PROCESS:
            break
            
        processed_count += 1
        
        if not row or not row.get("IP") or not row.get("URL") or not row.get("Staus"):
            continue
            
        status_code = row["Staus"].strip()
        url = row["URL"].strip()
        
        if status_code.startswith(TARGET_CLASS_PREFIX):
            records_in_target_class += 1
            status_code_counter[status_code] += 1
            url_counter[url] += 1
            
            writer.writerow(row)

five_most_requested = [url for url, _ in url_counter.most_common(5)]

summary_data = {
    "records_processed": processed_count,
    "target_status_class": f"{TARGET_CLASS_PREFIX}xx",
    "records_in_target_class": records_in_target_class,
    "count_per_status_code": dict(status_code_counter),
    "five_most_requested_urls": five_most_requested
}

with open(json_summary_file, mode="w", encoding="utf-8") as json_file:
    json.dump(summary_data, json_file, indent=4)

with open(json_summary_file, mode="r", encoding="utf-8") as json_file, \
     open(json_backup_file, mode="w", encoding="utf-8") as backup_file:
    backup_file.write(json_file.read())

backup_verified = os.path.exists(json_backup_file)

print("=" * 45)
print("ASSESSMENT DATA RESULT")
print("=" * 45)
print(f"Records processed: {processed_count}")
print(f"Target status class: {TARGET_CLASS_PREFIX}xx")
print(f"Records in target class: {records_in_target_class}")
print(f"Count per status code: {dict(status_code_counter)}")
print(f"Five most requested URLs: {five_most_requested}")
print(f"Filtered CSV file: Generated ('{filtered_csv_file}')")
print(f"JSON summary file: Generated ('{json_summary_file}')")
print(f"Backup verification: {'SUCCESS' if backup_verified else 'FAILED'}")
print("=" * 45)