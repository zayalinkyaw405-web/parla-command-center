"""
Scripts/send_email_outreach.py
==============================
Automated Local Email & API Outreach Dispatcher.
Supports:
  1. Resend API (Free 3,000 emails/mo - https://resend.com)
  2. Brevo API (Free 300 emails/day - https://brevo.com)
  3. Standard SMTP (Gmail, Outlook, Custom Domain)
"""

import os
import sys
import json
import smtplib
import urllib.request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PITCHES_DIR = PROJECT_ROOT / "Project" / "outbound_prospects" / "singapore_pitches"

# Free API Keys & SMTP Config
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")

SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "")

def send_via_resend(to_email: str, subject: str, body_text: str) -> bool:
    """Sends email via Resend Free REST API (3,000 free emails/mo)."""
    url = "https://api.resend.com/emails"
    payload = {
        "from": SENDER_EMAIL or "Parla Risk <onboarding@resend.dev>",
        "to": [to_email],
        "subject": subject,
        "text": body_text
    }
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f" [+] Success (Resend API): Email sent to {to_email}")
            return True
    except Exception as e:
        print(f" [!] Resend API Error for {to_email}: {e}")
        return False

def send_via_brevo(to_email: str, subject: str, body_text: str) -> bool:
    """Sends email via Brevo Free REST API (300 free emails/day)."""
    url = "https://api.brevo.com/v3/smtp/email"
    payload = {
        "sender": {"name": "Parla Intelligence", "email": SENDER_EMAIL or "risk@parlatelemetry.org"},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": body_text
    }
    headers = {
        "api-key": BREVO_API_KEY,
        "Content-Type": "application/json"
    }
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f" [+] Success (Brevo API): Email sent to {to_email}")
            return True
    except Exception as e:
        print(f" [!] Brevo API Error for {to_email}: {e}")
        return False

def send_email(to_email: str, subject: str, body_text: str):
    if RESEND_API_KEY:
        return send_via_resend(to_email, subject, body_text)
    if BREVO_API_KEY:
        return send_via_brevo(to_email, subject, body_text)
    if SENDER_EMAIL and SENDER_PASSWORD:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()
            print(f" [+] Success (SMTP): Email sent to {to_email}")
            return True
        except Exception as e:
            print(f" [!] SMTP Error for {to_email}: {e}")
            return False

    print("[!] Error: No mail credentials provided (RESEND_API_KEY, BREVO_API_KEY, or SMTP credentials).")
    return False

def dispatch_pitches():
    print("=" * 80)
    print("         PARLA AUTOMATED LOCAL SMTP OUTREACH DISPATCHER")
    print("=" * 80)
    
    if not PITCHES_DIR.exists():
        print(f"[!] Pitch directory not found: {PITCHES_DIR}")
        return

    pitch_files = list(PITCHES_DIR.glob("pitch_*.txt"))
    print(f" [*] Found {len(pitch_files)} prepared pitch files in {PITCHES_DIR.name}/")
    
    if not RESEND_API_KEY and not BREVO_API_KEY and (not SENDER_EMAIL or not SENDER_PASSWORD):
        print("\n [!] Mail Credentials missing!")
        print("     To activate automated sending, provide RESEND_API_KEY, BREVO_API_KEY, or SMTP credentials.")
        print("=" * 80)
        return

    for pf in pitch_files:
        content = pf.read_text(encoding="utf-8")
        lines = content.splitlines()
        subject = lines[0].replace("Subject: ", "").strip() if lines else "Sanctions Due-Diligence Alert"
        body = "\n".join(lines[2:])
        
        # Placeholder recipient - specify recipient email in prompt or config
        recipient = os.environ.get("RECIPIENT_EMAIL", SENDER_EMAIL)
        print(f"\n [+] Preparing dispatch for file: {pf.name}")
        print(f"     Subject: {subject}")
        print(f"     Recipient: {recipient}")
        send_email(recipient, subject, body)

    print("\n" + "=" * 80)
    print(" [PASS] Automated SMTP Dispatch Cycle Complete.")

if __name__ == "__main__":
    dispatch_pitches()
