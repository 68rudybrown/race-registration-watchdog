import json
import os
import requests
import smtplib

from datetime import datetime
from email.message import EmailMessage

STATUS_FILE = "status.json"

CURRENT_YEAR = datetime.now().year
NEXT_YEAR = CURRENT_YEAR + 1


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
    keywords = race["keywords"]

    print(f"\nChecking {name}")

    try:

        response = requests.get(
            url,
            timeout=30,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        page_text = response.text.lower()

        matched_keywords = []

        for keyword in keywords:

            if keyword.lower() in page_text:
                matched_keywords.append(keyword)

        registration_keywords = [
            "register now",
            "registration open",
            "sign up",
            "register today",
            "register"
        ]

        registration_open = any(
            keyword in page_text
            for keyword in registration_keywords
        )

        next_year_found = (
            str(NEXT_YEAR) in page_text
        )

        current_status[name] = {
            "matched_keywords": matched_keywords,
            "registration_open": registration_open,
            "next_year_found": next_year_found
        }

        previous = previous_status.get(name)

        if previous is None:

            print(
                f"First observation for {name}"
            )

        elif previous != current_status[name]:

            message = f"""
Race Monitor Alert

Race:
{name}

Previous State:
{json.dumps(previous, indent=2)}

Current State:
{json.dumps(current_status[name], indent=2)}

Organizer:
{url}
"""

            print(message)

            send_email(
                subject=f"Race Alert - {name}",
                body=message
            )

        else:

            print(
                f"No change detected for {name}"
            )

    except Exception as e:

        print(
            f"ERROR checking {name}: {e}"
        )

with open(
    STATUS_FILE,
    "w"
) as f:

    json.dump(
        current_status,
        f,
        indent=2
    )
