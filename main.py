import subprocess
import time
import sys

# --- CONFIGURATION ---
# Change these names if your files are named differently
SCRIPT_1 = "bot.py"       # Your Discord Bot
SCRIPT_2 = "Vault.py"     # Your Proxy Script

print(f"[*] Starting {SCRIPT_1}...")
# Start Discord Bot in background
p1 = subprocess.Popen([sys.executable, SCRIPT_1])

print(f"[*] Starting {SCRIPT_2}...")
# Start Proxy in background
p2 = subprocess.Popen([sys.executable, SCRIPT_2])

print("[*] Both scripts are running! Press CTRL+C to stop.")

try:
    # Keep the main process alive so Wispbyte doesn't think the server crashed
    while True:
        time.sleep(1)
        
        # Optional: Check if they crashed and restart them
        if p1.poll() is not None:
            print(f"[!] {SCRIPT_1} crashed! Restarting...")
            p1 = subprocess.Popen([sys.executable, SCRIPT_1])
            
        if p2.poll() is not None:
            print(f"[!] {SCRIPT_2} crashed! Restarting...")
            p2 = subprocess.Popen([sys.executable, SCRIPT_2])

except KeyboardInterrupt:
    print("\n[!] Stopping scripts...")
    p1.terminate()
    p2.terminate()