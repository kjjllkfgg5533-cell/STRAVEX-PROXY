import blackboxprotobuf
import gzip
import io
import traceback
from mitmproxy import http
from mitmproxy.tools.main import mitmweb

# --- CONFIGURATION ---
REAL_GOLD = 7107        # <--- Your EXACT Gold amount
FAKE_AMOUNT = 99999999

# We target ALL of these now
TARGETS = [
    "GetLoginData", 
    "GetPlayerInfo", 
    "GetAccountBrief", 
    "GetCurrency", 
    "GetLobby",       # <--- The likely culprit
    "GetHomePage",    # <--- Another common culprit
    "Sync",
    "EnterGame"
]

class AntiRevertSpoofer:
    def response(self, flow: http.HTTPFlow) -> None:
        url = flow.request.path
        
        # Check if URL matches ANY of our targets
        if any(t.lower() in url.lower() for t in TARGETS):
            
            data = flow.response.content
            is_gzipped = False
            
            # 1. Decompress
            if flow.response.headers.get("Content-Encoding") == "gzip" or (len(data) > 2 and data[:2] == b'\x1f\x8b'):
                try:
                    buf = io.BytesIO(data)
                    with gzip.GzipFile(fileobj=buf) as f:
                        data = f.read()
                    is_gzipped = True
                except:
                    pass 

            try:
                # 2. Decode
                message, typedef = blackboxprotobuf.decode_message(data)
                
                # 3. Aggressive Search & Replace
                self.found = False
                
                def modify_recursive(msg, tdef):
                    if isinstance(msg, dict):
                        for key in list(msg.keys()):
                            value = msg[key]
                            
                            # CHECK FOR GOLD
                            if value == REAL_GOLD:
                                print(f"[+] FOUND GOLD ({value}) in {url} -> Field {key}")
                                msg[key] = FAKE_AMOUNT
                                if tdef and key in tdef: tdef[key]['type'] = 'int'
                                self.found = True
                            
                            # Dive Deeper
                            elif isinstance(value, (dict, list)):
                                sub_tdef = None
                                if tdef and key in tdef and 'message_typedef' in tdef[key]:
                                    sub_tdef = tdef[k]['message_typedef']
                                
                                if isinstance(value, dict):
                                    modify_recursive(value, sub_tdef)
                                elif isinstance(value, list):
                                    for item in value:
                                        modify_recursive(item, sub_tdef)

                modify_recursive(message, typedef)

                if self.found:
                    print(f"   [!!!] BLOCKED REVERT! Modified packet: {url}")
                    
                    # 4. Re-Encode
                    new_data = blackboxprotobuf.encode_message(message, typedef)
                    final_payload = bytes(new_data)
                    
                    # 5. Send Uncompressed
                    if "Content-Encoding" in flow.response.headers:
                        del flow.response.headers["Content-Encoding"]
                        
                    flow.response.content = final_payload
                    flow.response.headers["Content-Length"] = str(len(final_payload))
                
            except Exception:
                # If decoding fails, we try RAW BYTE DETECTION
                # 7107 in Protobuf Varint is bytes: C3 37
                # This is a last resort check to see if we missed it
                
                # Calculate Varint bytes for your gold (Logic for 7107)
                # This logic only works for 7107. If your gold changes, this alert might allow it.
                if b'\xC3\x37' in data:
                    print(f"[ALERT] RAW GOLD BYTES DETECTED IN: {url}")
                    print("   [!] This packet is resetting your gold but we couldn't decode it.")
                    print("   [!] It might be encrypted or raw data.")

addons = [AntiRevertSpoofer()]

if __name__ == "__main__":
    mitmweb(["-s", __file__, "-p", "8080", "--set", "block_global=false"])