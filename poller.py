import json
import os
import subprocess
import time
from datetime import date
from urllib.parse import quote

import requests

BASE_URL = os.environ["BASE_URL"]
BOOKING_PAGE_BASE_URL = os.environ["BOOKING_PAGE_BASE_URL"]
COURT_ID = int(os.environ.get("COURT_ID", "2186"))

WA_PHONE = os.environ["WA_PHONE"]
WA_APIKEY = os.environ["WA_APIKEY"]

STATE_FILE = "state.json"
BOT_HEADER = "Tenis de domingo 🎾"


def build_message(body):
    return f"{BOT_HEADER}\n\n{body}"


def request_with_retry(method, url, **kwargs):
    for attempt in range(1, 4):
        try:
            response = requests.request(method, url, timeout=20, **kwargs)
            print(f"{method.upper()} {url} - attempt {attempt} - status {response.status_code}")
            print(f"Response body: {response.text}")
            response.raise_for_status()
            return response
        except requests.RequestException as error:
            print(f"Request failed on attempt {attempt}: {error}")

            if attempt < 3:
                time.sleep(5)

    raise RuntimeError(f"Request failed after 3 attempts: {method.upper()} {url}")


def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "last_run_date": None,
            "notified": False,
        }

    with open(STATE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=2, ensure_ascii=False)
        file.write("\n")


def commit_state():
    subprocess.run(["git", "config", "user.email", "bot@github.com"], check=True)
    subprocess.run(["git", "config", "user.name", "Poller Bot"], check=True)
    subprocess.run(["git", "add", STATE_FILE], check=True)

    commit = subprocess.run(
        ["git", "commit", "-m", "chore: update poller state"],
        capture_output=True,
        text=True,
    )

    if commit.returncode != 0:
        print("No state changes to commit.")
        print(commit.stdout)
        print(commit.stderr)
        return

    subprocess.run(["git", "push"], check=True)


def reset_state_if_needed(state):
    today = str(date.today())

    if state.get("last_run_date") != today:
        print("New day detected. Resetting notification state.")
        return {
            "last_run_date": today,
            "notified": False,
        }

    return state


def get_available_slots():
    url = f"{BASE_URL}/{COURT_ID}/Horarios"
    response = request_with_retry("GET", url)
    data = response.json()

    if not data.get("sucesso", False):
        print(f"API returned sucesso=false: {data}")
        return []

    return data.get("horarios_disponiveis", [])


def notify_whatsapp(message):
    url = (
        "https://api.callmebot.com/whatsapp.php"
        f"?phone={WA_PHONE}"
        f"&text={quote(message)}"
        f"&apikey={WA_APIKEY}"
    )

    request_with_retry("GET", url)


def get_booking_page_url():
    return f"{BOOKING_PAGE_BASE_URL}/{COURT_ID}"


def main():
    state = load_state()
    state = reset_state_if_needed(state)

    if state.get("notified"):
        print("Already notified today. Exiting.")
        return

    available_slots = get_available_slots()

    print(f"Available slots: {available_slots}")

    if not available_slots:
        print("No available slots found.")
        save_state(state)
        commit_state()
        return

    notify_whatsapp(
        build_message(
            "Horários disponíveis encontrados!\n\n"
            + "\n".join(f"🕒 {slot}" for slot in available_slots)
            + f"\n\nAcesse para agendar:\n{get_booking_page_url()}"
        )
    )
    
    state["notified"] = True
    save_state(state)
    commit_state()


if __name__ == "__main__":
    main()
