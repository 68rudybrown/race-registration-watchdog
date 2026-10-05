import json
import requests

with open("races.json") as f:
    races = json.load(f)

for race in races:
    try:
        response = requests.get(race["url"], timeout=20)

        if response.status_code == 200:
            print(f"SUCCESS: {race['name']}")
        else:
            print(f"ERROR: {race['name']}")

    except Exception as e:
        print(f"FAILED: {race['name']} - {e}")
