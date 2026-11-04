import csv
import json
import os

TARGET_OS = "Android"
TARGET_BEHAVIOR_CLASS = "2"

input_csv_file = "user_behavior_dataset.csv"
exported_csv_file = "selected_user_profiles.csv"
json_summary_file = "usage_summary.json"
csv_backup_file = "selected_user_profiles_backup.csv"

total_dataset_records = 0
matching_os_count = 0
matching_target_class_count = 0

total_battery_drain = 0.0
total_data_usage = 0.0

export_fields = [
    "User ID", 
    "Device Model", 
    "Operating System", 
    "Battery Drain (mAh/day)", 
    "Data Usage (MB/day)"
]

with open(input_csv_file, mode="r", encoding="utf-8", errors="ignore") as infile, \
     open(exported_csv_file, mode="w", newline="", encoding="utf-8") as outfile:
    
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=export_fields)
    writer.writeheader()
    
    for row in reader:
        total_dataset_records += 1
        current_os = row.get("Operating System", "").strip()
        current_class = row.get("User Behavior Class", "").strip()
        
        if current_os.lower() == TARGET_OS.lower():
            matching_os_count += 1
            
            if current_class == TARGET_BEHAVIOR_CLASS:
                matching_target_class_count += 1
                
                try:
                    battery = float(row.get("Battery Drain (mAh/day)", 0))
                    data = float(row.get("Data Usage (MB/day)", 0))
                except ValueError:
                    continue
                
                total_battery_drain += battery
                total_data_usage += data
                
                filtered_row = {field: row.get(field, "").strip() for field in export_fields}
                writer.writerow(filtered_row)

if matching_target_class_count > 0:
    avg_battery_drain = total_battery_drain / matching_target_class_count
    avg_data_usage = total_data_usage / matching_target_class_count
else:
    avg_battery_drain = 0.0
    avg_data_usage = 0.0

exported_row_count = 0
if os.path.exists(exported_csv_file):
    with open(exported_csv_file, mode="r", encoding="utf-8") as f:
        exported_row_count = sum(1 for line in f) - 1

count_verification = "PASSED" if exported_row_count == matching_target_class_count else "FAILED"

summary_data = {
    "operating_system": TARGET_OS,
    "user_behavior_class": TARGET_BEHAVIOR_CLASS,
    "total_records_in_dataset": total_dataset_records,
    "records_matching_os": matching_os_count,
    "records_in_target_behavior_class": matching_target_class_count,
    "average_battery_drain_mah_day": round(avg_battery_drain, 2),
    "average_data_usage_mb_day": round(avg_data_usage, 2),
    "count_verification": count_verification
}

with open(json_summary_file, mode="w", encoding="utf-8") as json_file:
    json.dump(summary_data, json_file, indent=4)

if os.path.exists(exported_csv_file):
    with open(exported_csv_file, mode="r", encoding="utf-8") as src, \
         open(csv_backup_file, mode="w", encoding="utf-8") as bkp:
        bkp.write(src.read())
        
    backup_file_size_bytes = os.path.getsize(csv_backup_file)
else:
    backup_file_size_bytes = 0

print("=" * 55)
print("ASSESSMENT DATA RESULT")
print("=" * 55)
print(f"Operating system and behavior class: {TARGET_OS} (Class {TARGET_BEHAVIOR_CLASS})")
print(f"Total records in dataset: {total_dataset_records}")
print(f"Records matching operating system: {matching_os_count}")
print(f"Records in target behavior class: {matching_target_class_count}")
print(f"Average battery drain (mAh/day): {avg_battery_drain:.2f}")
print(f"Average data usage (MB/day): {avg_data_usage:.2f}")
print(f"Count verification: {count_verification} ({exported_row_count} == {matching_target_class_count})")
print(f"Exported CSV file: Generated ('{exported_csv_file}')")
print(f"JSON summary file: Generated ('{json_summary_file}')")
print(f"Backup file and size: Generated ('{csv_backup_file}') | {backup_file_size_bytes} bytes")
print("=" * 55)