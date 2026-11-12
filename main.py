import subprocess
import time
import sys
import os

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# البروكسي الرئيسي فقط (Vault.py)
# Vault.py هو الذي يتحقق من uid.txt ويفتح العناصر ويحقن الإيميلات
SCRIPT_MAIN = os.path.join(BASE_DIR, "Vault.py")

# ملف UID الذي يقرأه Vault.py
UID_FILE = os.path.join(BASE_DIR, "uid.txt")


def ensure_uid_file():
    """تأكد أن uid.txt موجود قبل تشغيل البروكسي."""
    if not os.path.exists(UID_FILE):
        print(f"[!] {UID_FILE} غير موجود. جاري إنشاء ملف فارغ...")
        with open(UID_FILE, "w", encoding="utf-8") as f:
            f.write("")
        print(f"[i] أضف UIDs يدوياً في: {UID_FILE} (سطر لكل UID)")
    else:
        with open(UID_FILE, "r", encoding="utf-8") as f:
            count = sum(1 for line in f if line.strip().isdigit())
        print(f"[i] تم تحميل {count} UID من {UID_FILE}")


def start_proxy():
    """تشغيل Vault.py كعملية فرعية."""
    print(f"[*] تشغيل {os.path.basename(SCRIPT_MAIN)}...")
    return subprocess.Popen([sys.executable, SCRIPT_MAIN], cwd=BASE_DIR)


def main():
    if not os.path.exists(SCRIPT_MAIN):
        print(f"[!] خطأ: لم يتم العثور على {SCRIPT_MAIN}")
        sys.exit(1)

    ensure_uid_file()

    proxy = start_proxy()
    print("[*] البروكسي يعمل الآن على المنفذ 30015 (mitmweb).")
    print("[*] اضغط CTRL+C للإيقاف.\n")

    try:
        while True:
            time.sleep(1)

            # إعادة التشغيل التلقائي إذا انهار
            if proxy.poll() is not None:
                print(f"[!] {os.path.basename(SCRIPT_MAIN)} توقف! جاري إعادة التشغيل...")
                proxy = start_proxy()

    except KeyboardInterrupt:
        print("\n[!] إيقاف البروكسي...")
        proxy.terminate()
        try:
            proxy.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proxy.kill()
        print("[i] تم الإيقاف.")


if __name__ == "__main__":
    main()