import json
import os
import requests
import smtplib
from email.message import EmailMessage

def send_email(subject, body):
 
sender = os.environ["EMAIL_ADDRESS"]
password = os.environ["EMAIL_PASSWORD"]
 
msg = EmailMessage()
 
msg["Subject"] = subject
msg["From"] = sender
msg["To"] = sender
 
msg.set_content(body)
 
with smtplib.SMTP_SSL(
"smtp.gmail.com",
465
) as smtp:
 
smtp.login(
sender,
password
)
 
smtp.send_message(msg)

STATUS_FILE = "status.json"

with open("races.json") as f:
    races = json.load(f)

if os.path.exists(STATUS_FILE):
    with open(STATUS_FILE) as f:
        previous_status = json.load(f)
else:
    previous_status = {}

current_status = {}

for race in races:

    name = race["name"]
    url = race["organizer_url"]

    print(f"\nChecking: {name}")

    try:

        response = requests.get(
            url,
            timeout=30,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        text = response.text.lower()

        found = name.lower() in text

        current_status[name] = found

        previous = previous_status.get(name)

        if previous is None:
            print(f"First observation: {found}")

        elif previous != found:

            print(
                f"CHANGE DETECTED: "
                f"{name} "
                f"{previous} -> {found}"
            )

        else:

            print(
                f"No change: {found}"
            )

    except Exception as e:

        print(
            f"ERROR: {name} - {e}"
        )

with open(STATUS_FILE, "w") as f:
    json.dump(
        current_status,
        f,
        indent=2
    )

send_email(
    "Race Monitor Test",
    "If you received this email, GitHub Actions email is working."
)
