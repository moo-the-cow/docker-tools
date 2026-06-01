import os
import time
import urllib.request
import json
import smtplib
from email.mime.text import MIMEText

# Load configuration from Environment Variables
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM")  # NEW: Explicit full sender address
EMAIL_TO = os.getenv("EMAIL_TO")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 1800))

CACHE_FILE = "/data/last_ip.json"

def get_current_ip_payload():
    try:
        req = urllib.request.Request(
            "https://v4.ipify.io/?format=json", 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            raw_data = response.read().decode('utf-8').strip()
            
            if not raw_data.startswith('{'):
                print(f"Error: API returned non-JSON response: {raw_data[:200]}")
                return None
                
            return json.loads(raw_data)
    except Exception as e:
        print(f"Error fetching IP payload: {e}")
        return None

def send_email(old_ip, new_ip):
    msg = MIMEText(f"Your public WAN IP changed.\nOld IP: {old_ip}\nNew IP: {new_ip}")
    msg['Subject'] = '⚠️ WAN IP Address Changed'
    msg['From'] = EMAIL_FROM  # FIXED: Now uses the explicit email address string
    msg['To'] = EMAIL_TO

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)  # Continues to login with plain username
        server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string()) # FIXED: Sender routing address
        server.quit()
        print("Notification email sent successfully.")
    except Exception as e:
        print(f"SMTP Error: Failed to send email: {e}")

def main():
    print("IP Monitor container started running (IPv4 JSON tracking mode)...")
    
    while True:
        current_payload = get_current_ip_payload()
        
        if current_payload and "ip" in current_payload:
            current_ip = current_payload["ip"]
            last_ip = None
            
            if os.path.exists(CACHE_FILE) and os.path.getsize(CACHE_FILE) > 0:
                try:
                    with open(CACHE_FILE, "r") as f:
                        cached_data = json.load(f)
                        last_ip = cached_data.get("ip")
                except Exception as e:
                    print(f"Warning: Could not parse cached JSON file: {e}")
            
            if last_ip is None:
                print(f"Initial boot or empty cache. Saving payload: {current_payload}")
                with open(CACHE_FILE, "w") as f:
                    json.dump(current_payload, f, indent=4)
            elif current_ip != last_ip:
                print(f"IP Change detected: {last_ip} -> {current_ip}")
                send_email(last_ip, current_ip)
                with open(CACHE_FILE, "w") as f:
                    json.dump(current_payload, f, indent=4)
            else:
                print(f"IP unchanged: {current_ip}")
                
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
