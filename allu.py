import requests
import json
import os

# The hidden database URL used by 0xme.github.io
# Based on the repo: https://github.com/0xMe/ItemID2
DB_URL = "https://0xme.github.io/ItemID2/assets/itemData.json"

OUTPUT_FILE = "itemss.txt"

def fetch_and_save():
    print(f"[i] Connecting to {DB_URL}...")
    
    try:
        # 1. Download the Database
        response = requests.get(DB_URL)
        response.raise_for_status() # Check for errors
        
        data = response.json()
        
        # The data structure is likely a list of objects or a dict
        # We need to find the 'itemID' in each entry
        
        all_ids = []
        
        print(f"[i] Database downloaded. Parsing...")
        
        # Handle if it's a list [ {item}, {item} ]
        if isinstance(data, list):
            for item in data:
                if 'itemID' in item:
                    all_ids.append(item['itemID'])
                    
        # Handle if it's a dict { "items": [...] }
        elif isinstance(data, dict):
            # Sometimes keys are the IDs themselves
            for key, value in data.items():
                if isinstance(value, dict) and 'itemID' in value:
                    all_ids.append(value['itemID'])
                elif key.isdigit() and len(key) > 6:
                     all_ids.append(key)
        
        # 2. Filter & Sort
        # Remove duplicates and ensure they are numbers
        unique_ids = sorted(list(set(all_ids)))
        
        print(f"[+] Found {len(unique_ids)} unique items!")
        
        # 3. Save to items.txt
        with open(OUTPUT_FILE, "w") as f:
            for uid in unique_ids:
                f.write(f"{uid}\n")
                
        print(f"[+] Successfully saved all IDs to '{OUTPUT_FILE}'")
        print("[i] You can now run 'unlock_skins_unlimited.py'")
        
    except Exception as e:
        print(f"[!] Error: {e}")
        print("[i] Trying alternative source...")
        try_backup_source()

def try_backup_source():
    # If the first link fails, we try scraping the raw text for 9-digit numbers
    # This is a fallback "Brute Force" method
    try:
        import re
        backup_url = "https://0xme.github.io/ItemID2/"
        r = requests.get(backup_url)
        # Regex for Free Fire IDs (usually 9 digits, starting with 1-9)
        found = re.findall(r'\b[1-9]\d{8}\b', r.text)
        
        unique = sorted(list(set(found)))
        with open(OUTPUT_FILE, "w") as f:
            for uid in unique:
                f.write(f"{uid}\n")
        print(f"[+] Backup method found {len(unique)} IDs.")
    except:
        print("[!] Backup failed too.")

if __name__ == "__main__":
    fetch_and_save()