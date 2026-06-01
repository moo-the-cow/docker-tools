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
EMAIL_TO = os.getenv("EMAIL_TO")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 1800))

CACHE_FILE = "/data/last_ip.txt"

def get_current_ip():
    try:
        # Querying a lightweight JSON IP endpoint
        req = urllib.request.Request(
            "https://ipify.org", 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get("ip")
    except Exception as e:
        print(f"Error fetching IP: {e}")
        return None

def send_email(old_ip, new_ip):
    msg = MIMEText(f"Your public WAN IP changed.\nOld IP: {old_ip}\nNew IP: {new_ip}")
    msg['Subject'] = '⚠️ WAN IP Address Changed'
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO

    try:
        # Secure SMTP connection using explicit STARTTLS
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, [EMAIL_TO], msg.as_string())
        server.quit()
        print("Notification email sent successfully.")
    except Exception as e:
        print(f"SMTP Error: Failed to send email: {e}")

def main():
    print("IP Monitor container started running...")
    os.makedirs("/data", exist_ok=True)
    
    while True:
        current_ip = get_current_ip()
        if current_ip:
            last_ip = None
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, "r") as f:
                    last_ip = f.read().strip()
            
            if current_ip != last_ip:
                print(f"IP Change detected: {last_ip} -> {current_ip}")
                if last_ip:  # Don't spam on the very first boot
                    send_email(last_ip, current_ip)
                with open(CACHE_FILE, "w") as f:
                    f.write(current_ip)
            else:
                print(f"IP unchanged: {current_ip}")
                
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
