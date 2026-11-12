<<<<<<< HEAD
import blackboxprotobuf
import gzip
import io
import time
from mitmproxy import http
from mitmproxy.tools.main import mitmweb

# ==========================================
# --- CONFIGURATION ---
# ==========================================
TARGET_URL = "GetMailList"

# --- 1. TEXT SETTINGS ---
# We try Type 0 (System) or Type 5 (GM Mail) to bypass the "Guild" template.
MAIL_TYPE    = 0      # 0 = Standard Text Mail (Best for custom text)
MAIL_TITLE   = b"FREE REWARDS FOR USING PROXY SERVER"
MAIL_CONTENT = b"WELCOme TO VPS.COM FREE PROXY SERVER.\n\nEnjoy!"

# --- 2. REWARD SETTINGS ---
# We use REAL Item IDs so the icons appear.
# ID 203000014 = Common Crate (Should show icon)
# ID 100000000 = Often Gold/Coins
MAIL_REWARDS = [
    {'1': 203000014, '2': 1},     # A Crate (To test Icon)
    {'1': 1, '2': 99999}          # Gold (Might still be gray, but valid)
]

# ==========================================

class MailInjectorFix:
    def response(self, flow: http.HTTPFlow) -> None:
        if TARGET_URL.lower() in flow.request.path.lower():
            print(f"\n[+] Intercepted Mail List! Applying Fix...")
            
            data = flow.response.content
            is_gzipped = False
            if flow.response.headers.get("Content-Encoding") == "gzip" or (len(data) > 2 and data[:2] == b'\x1f\x8b'):
                try:
                    buf = io.BytesIO(data)
                    with gzip.GzipFile(fileobj=buf) as f:
                        data = f.read()
                    is_gzipped = True
                except: pass
            
            try:
                message, typedef = blackboxprotobuf.decode_message(data)
                
                if '1' in message and isinstance(message['1'], list):
                    
                    fake_mail = {
                        '1': 20009999999999,     
                        '2': MAIL_TYPE,          # <--- CHANGED THIS (0 is usually Text)
                        '3': MAIL_TITLE,         
                        '4': MAIL_CONTENT,       
                        '5': {},                 
                        '6': {                   
                            '1': {
                                '1': MAIL_REWARDS
                            }
                        },
                        '7': int(time.time()),   
                        '11': b'OB51',           
                        '15': int(time.time()) + 999999 
                    }

                    # Inject at top
                    message['1'].insert(0, fake_mail)
                    print(f"   [+] Injected Mail (Type {MAIL_TYPE})")

                    # --- MANUAL TYPEDEF FIX ---
                    # This ensures the game reads Title/Body as text, not numbers.
                    try:
                        mail_typedef = typedef['1']['message_typedef']
                        mail_typedef['3'] = {'type': 'bytes', 'name': ''} # Title
                        mail_typedef['4'] = {'type': 'bytes', 'name': ''} # Body
                        mail_typedef['5'] = {'type': 'message', 'message_typedef': {}, 'name': ''}
                        
                        # Rewards
                        rewards_typedef = mail_typedef['6']['message_typedef']['1']['message_typedef']['1']['message_typedef']
                        rewards_typedef['1']['type'] = 'int'
                        rewards_typedef['2']['type'] = 'int'
                    except: pass

                    new_data = blackboxprotobuf.encode_message(message, typedef)
                    
                    if is_gzipped:
                        out = io.BytesIO()
                        with gzip.GzipFile(fileobj=out, mode='wb', mtime=0) as f:
                            f.write(new_data)
                        final_payload = out.getvalue()
                    else:
                        final_payload = bytes(new_data)
                    
                    flow.response.content = final_payload
                    if "Content-Encoding" in flow.response.headers:
                        del flow.response.headers["Content-Encoding"]
                    flow.response.headers["Content-Length"] = str(len(final_payload))
                    print("[+] Mail Fix Applied.")

            except Exception as e:
                print(f"[!] Error: {e}")

addons = [MailInjectorFix()]

if __name__ == "__main__":
    mitmweb([
        "-s", __file__,
        "-p", "8080",
        "--set", "block_global=false"
=======
import blackboxprotobuf
import gzip
import io
import time
from mitmproxy import http
from mitmproxy.tools.main import mitmweb

# ==========================================
# --- CONFIGURATION ---
# ==========================================
TARGET_URL = "GetMailList"

# --- 1. TEXT SETTINGS ---
# We try Type 0 (System) or Type 5 (GM Mail) to bypass the "Guild" template.
MAIL_TYPE    = 0      # 0 = Standard Text Mail (Best for custom text)
MAIL_TITLE   = b"FREE REWARDS FOR USING PROXY SERVER"
MAIL_CONTENT = b"WELCOme TO VPS.COM FREE PROXY SERVER.\n\nEnjoy!"

# --- 2. REWARD SETTINGS ---
# We use REAL Item IDs so the icons appear.
# ID 203000014 = Common Crate (Should show icon)
# ID 100000000 = Often Gold/Coins
MAIL_REWARDS = [
    {'1': 203000014, '2': 1},     # A Crate (To test Icon)
    {'1': 1, '2': 99999}          # Gold (Might still be gray, but valid)
]

# ==========================================

class MailInjectorFix:
    def response(self, flow: http.HTTPFlow) -> None:
        if TARGET_URL.lower() in flow.request.path.lower():
            print(f"\n[+] Intercepted Mail List! Applying Fix...")
            
            data = flow.response.content
            is_gzipped = False
            if flow.response.headers.get("Content-Encoding") == "gzip" or (len(data) > 2 and data[:2] == b'\x1f\x8b'):
                try:
                    buf = io.BytesIO(data)
                    with gzip.GzipFile(fileobj=buf) as f:
                        data = f.read()
                    is_gzipped = True
                except: pass
            
            try:
                message, typedef = blackboxprotobuf.decode_message(data)
                
                if '1' in message and isinstance(message['1'], list):
                    
                    fake_mail = {
                        '1': 20009999999999,     
                        '2': MAIL_TYPE,          # <--- CHANGED THIS (0 is usually Text)
                        '3': MAIL_TITLE,         
                        '4': MAIL_CONTENT,       
                        '5': {},                 
                        '6': {                   
                            '1': {
                                '1': MAIL_REWARDS
                            }
                        },
                        '7': int(time.time()),   
                        '11': b'OB51',           
                        '15': int(time.time()) + 999999 
                    }

                    # Inject at top
                    message['1'].insert(0, fake_mail)
                    print(f"   [+] Injected Mail (Type {MAIL_TYPE})")

                    # --- MANUAL TYPEDEF FIX ---
                    # This ensures the game reads Title/Body as text, not numbers.
                    try:
                        mail_typedef = typedef['1']['message_typedef']
                        mail_typedef['3'] = {'type': 'bytes', 'name': ''} # Title
                        mail_typedef['4'] = {'type': 'bytes', 'name': ''} # Body
                        mail_typedef['5'] = {'type': 'message', 'message_typedef': {}, 'name': ''}
                        
                        # Rewards
                        rewards_typedef = mail_typedef['6']['message_typedef']['1']['message_typedef']['1']['message_typedef']
                        rewards_typedef['1']['type'] = 'int'
                        rewards_typedef['2']['type'] = 'int'
                    except: pass

                    new_data = blackboxprotobuf.encode_message(message, typedef)
                    
                    if is_gzipped:
                        out = io.BytesIO()
                        with gzip.GzipFile(fileobj=out, mode='wb', mtime=0) as f:
                            f.write(new_data)
                        final_payload = out.getvalue()
                    else:
                        final_payload = bytes(new_data)
                    
                    flow.response.content = final_payload
                    if "Content-Encoding" in flow.response.headers:
                        del flow.response.headers["Content-Encoding"]
                    flow.response.headers["Content-Length"] = str(len(final_payload))
                    print("[+] Mail Fix Applied.")

            except Exception as e:
                print(f"[!] Error: {e}")

addons = [MailInjectorFix()]

if __name__ == "__main__":
    mitmweb([
        "-s", __file__,
        "-p", "8080",
        "--set", "block_global=false"
>>>>>>> a2a665344e26425a247661a985e563d37eb0f539
    ])