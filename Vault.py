import bbpb as blackboxprotobuf
import gzip
import io
import copy
import traceback
import os
import time
from pathlib import Path
from mitmproxy import http
from mitmproxy.tools.main import mitmweb

# --- DEPENDENCY CHECK ---
try:
    from proto_utils import ProtobufUtils
    from Login_pb2 import LoginReq, getUID
    import ban_pb2
    PROTO_AVAILABLE = True
except ImportError as e:
    print(f"[!] CRITICAL: Missing dependency files. ({e})")
    print("    Make sure Login_pb2.py, ban_pb2.py, and proto_utils.py are here.")
    PROTO_AVAILABLE = False



UID_FILE = "uid.txt"
ID_FILE  = "itemss.txt"


URL_AUTH     = "majorlogin"
URL_PRE_AUTH = "GetAccountBriefInfoBeforeLogin"
URL_BACKPACK = "GetBackPack"
URL_LOGIN    = "GetLoginData"
URL_MAIL     = "GetMailList"
URL_PROFILE  = "GetPlayerPersonalShow"

FAKE_NAME    = "[b][c][ffd319]Ⓥ[c][ffffff]STRAVEX"
FAKE_UID     = 1111111111
FAKE_REGION  = b"ME"
FAKE_LIKES   = 99999
INJECT_LEVEL = 100
ID_LEVEL_FIELD = '6' 


MAIL_TYPE    = 0
MAIL_TITLE   = b"STRAVEX PROXY"
MAIL_CONTENT = b"STRAVEX VIP.\n\nEnjoy!"
MAIL_REWARDS = [
    {'1': 203000014, '2': 1},     # Crate
    {'1': 1, '2': 99999},         # Gold
    {'1': 2000000030, '2': 1}     # Other
]


IS_AUTHENTICATED = False


if PROTO_AVAILABLE:
    protoUtils = ProtobufUtils()

def load_uids():
    if not os.path.exists(UID_FILE): return []
    with open(UID_FILE, "r") as f:
        return [line.strip() for line in f if line.strip().isdigit()]

def load_items():
    if not os.path.exists(ID_FILE):
        with open(ID_FILE, "w") as f: f.write("203000014\n")
        return [203000014]
    with open(ID_FILE, "r") as f:
        # Load all items
        return [int(line.replace(",","").strip()) for line in f if line.strip().isdigit()]

def get_data(f):
    d = f.response.content
    gz = False
    if f.response.headers.get("Content-Encoding") == "gzip" or (len(d)>2 and d[:2]==b'\x1f\x8b'):
        try:
            b = io.BytesIO(d)
            with gzip.GzipFile(fileobj=b) as z: d = z.read()
            gz = True
        except: pass
    return d, gz


def set_data(f, d, gz):
    
    
    final_payload = bytes(d) # Force immutable bytes
    
   
    if "Content-Encoding" in f.response.headers: 
        del f.response.headers["Content-Encoding"]
    
    
    f.response.content = final_payload
    f.response.headers["Content-Length"] = str(len(final_payload))


class UltimateInterceptor:
    
    def response(self, flow: http.HTTPFlow) -> None:
        global IS_AUTHENTICATED

        # [1] BAN MESSAGE
        if URL_PRE_AUTH in flow.request.path and PROTO_AVAILABLE:
            if not IS_AUTHENTICATED:
                try:
                    data, is_gzip = get_data(flow)
                    current_response = ban_pb2.THUG4FF()
                    current_response.ParseFromString(data)
                    old_nickname = current_response.nickname
                    print(f"[AUTH] Injecting Ban Message...")
                    current_response.nickname = (
                        f"[c][ff0000]{old_nickname}\n[000000]Reason:[b][c][ff0000]UID Not Whitelisted"
                    )
                    new_content = current_response.SerializeToString()
                    set_data(flow, new_content, is_gzip)
                except: pass

   
        if URL_AUTH.lower() in flow.request.path.lower() and flow.request.method == "POST":
            if not PROTO_AVAILABLE: return
            try:
                resp = flow.response.content
                decoded = protoUtils.decode_protobuf(resp, getUID)
                detected_uid = str(decoded.uid).strip()
                allowed_uids = load_uids()
                print(f"\n[AUTH] 🔒 Checking UID: {detected_uid}")

                if detected_uid in allowed_uids:
                    print(f"[AUTH] ✅ ACCESS GRANTED.")
                    IS_AUTHENTICATED = True
                else:
                    print(f"[AUTH] ⛔ ACCESS DENIED.")
                    IS_AUTHENTICATED = False
                    ban_payload = bytes.fromhex("6a0a0891a40118f697fcc4067a020801")
                    flow.response.content = ban_payload
                    flow.response.headers["Content-Length"] = str(len(ban_payload))
            except: pass


        if (URL_LOGIN.lower() in flow.request.path.lower() or 
            URL_BACKPACK.lower() in flow.request.path.lower() or 
            URL_PROFILE.lower() in flow.request.path.lower() or 
            URL_MAIL.lower() in flow.request.path.lower()):
            
            if not IS_AUTHENTICATED:
                flow.response = http.Response.make(403, b"Access Denied", {"Content-Type": "text/plain"})
                return

        if IS_AUTHENTICATED:
            
  
            if URL_LOGIN.lower() in flow.request.path.lower():
                data, is_gzip = get_data(flow)
                try:
                    msg, typedef = blackboxprotobuf.decode_message(data)
                    mod = False
                    if ID_LEVEL_FIELD in msg:
                        msg[ID_LEVEL_FIELD] = INJECT_LEVEL
                        typedef[ID_LEVEL_FIELD]['type'] = 'int'
                        mod = True
                    if '4' in msg and FAKE_NAME not in str(msg['4']):
                        msg['4'] = FAKE_NAME
                        mod = True
                    if mod:
                        new_d = blackboxprotobuf.encode_message(msg, typedef)
                        set_data(flow, new_d, is_gzip)
                except: pass

         
            if URL_PROFILE.lower() in flow.request.path.lower():
                data, is_gzip = get_data(flow)
                try:
                    msg, typedef = blackboxprotobuf.decode_message(data)
                    if '1' in msg and isinstance(msg['1'], dict):
                        profile = msg['1']
                        profile_typedef = typedef['1']['message_typedef']
                        
                        profile['1'] = FAKE_UID
                        profile_typedef['1']['type'] = 'int'

                        profile['3'] = FAKE_NAME.encode('utf-8') if isinstance(FAKE_NAME, str) else FAKE_NAME
                        profile_typedef['3']['type'] = 'bytes'

                        profile['5'] = FAKE_REGION
                        profile_typedef['5']['type'] = 'bytes'

                        profile['6'] = INJECT_LEVEL
                        profile_typedef['6']['type'] = 'int'

                        profile['21'] = FAKE_LIKES
                        profile_typedef['21'] = {'type': 'int', 'name': ''} 

                        new_d = blackboxprotobuf.encode_message(msg, typedef)
                        set_data(flow, new_d, is_gzip)
                except: pass

           
            if URL_BACKPACK.lower() in flow.request.path.lower():
                data, is_gzip = get_data(flow)
                try:
                    msg, typedef = blackboxprotobuf.decode_message(data)
                    if '3' in msg and isinstance(msg['3'], list) and len(msg['3']) > 0:
                        tpl = msg['3'][0]
                        exist = set(i.get('1') for i in msg['3'] if '1' in i)
                        ids = load_items()
                        
                    
                        count = 0
                        for i in ids:
                            if i not in exist:
                                new = copy.deepcopy(tpl)
                                new['1'] = int(i); new['2'] = 1; new['4'] = -1
                                msg['3'].append(new)
                                count += 1
                        
                        if count > 0:
                            print(f"[GAME] Unlocked {count} Items.")
                            try:
                                typedef['3']['message_typedef']['1']['type'] = 'int'
                                typedef['3']['message_typedef']['2']['type'] = 'int'
                                typedef['3']['message_typedef']['4']['type'] = 'int'
                            except: pass
                            new_d = blackboxprotobuf.encode_message(msg, typedef)
                            set_data(flow, new_d, is_gzip)
                except: pass


            if URL_MAIL.lower() in flow.request.path.lower():
                data, is_gzip = get_data(flow)
                try:
                    message, typedef = blackboxprotobuf.decode_message(data)
                    if '1' in message and isinstance(message['1'], list):
                        fake_mail = {
                            '1': 20009999999999, '2': MAIL_TYPE, '3': MAIL_TITLE, '4': MAIL_CONTENT,       
                            '5': {}, '6': { '1': { '1': MAIL_REWARDS } },
                            '7': int(time.time()), '11': b'OB51', '15': int(time.time()) + 999999 
                        }
                        message['1'].insert(0, fake_mail)
                        try:
                            mt = typedef['1']['message_typedef']
                            mt['3'] = {'type': 'bytes', 'name': ''}
                            mt['4'] = {'type': 'bytes', 'name': ''}
                            mt['5'] = {'type': 'message', 'message_typedef': {}, 'name': ''}
                            rt = mt['6']['message_typedef']['1']['message_typedef']['1']['message_typedef']
                            rt['1']['type'] = 'int'; rt['2']['type'] = 'int'
                        except: pass
                        new_d = blackboxprotobuf.encode_message(message, typedef)
                        set_data(flow, new_d, is_gzip)
                except: pass

addons = [UltimateInterceptor()]

if __name__ == "__main__":
    mitmweb([
        "-s", __file__,
        "--listen-host", "0.0.0.0",   # ← إجباري: البروكسي يستمع على كل الواجهات
        "-p", "30015",                 # ← منفذ البروكسي
        "--set", "block_global=false", # ← إجباري: يسمح باتصالات من الشبكة
    ])