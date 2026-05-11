import json
import os
import subprocess
import time
from datetime import date
from urllib.parse import quote

import requests

BASE_URL = os.environ["BASE_URL"]

COURT_ID = int(os.environ.get("COURT_ID", "2186"))
TARGET_TIMES = os.environ.get("TARGET_TIMES", "08:00,09:20").split(",")

BOOKING_USER_JSON = os.environ["BOOKING_USER_JSON"]

WA_PHONE = os.environ["WA_PHONE"]
WA_APIKEY = os.environ["WA_APIKEY"]

STATE_FILE = "state.json"

PEOPLE_COUNT = "4"

ADDITIONAL_FIELDS = {
    "birth_date": 18388,
    "phone": 18387,
    "people_count": 18389,
    "email": 18391,
    "neighborhood": 18392,
    "city": 18390,
}


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
            "booked_slots": [],
            "failed_slots": [],
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
        print("New day detected. Resetting state.")
        return {
            "last_run_date": today,
            "booked_slots": [],
            "failed_slots": [],
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


def is_target_slot(slot):
    return any(slot.endswith(f"T{target}:00") for target in TARGET_TIMES)


def build_booking_payload(slot):
    user = json.loads(BOOKING_USER_JSON)

    return {
        "id_servico": COURT_ID,
        "data_hora_agendamento": slot,
        "is_app": False,
        "cpf": user["cpf"],
        "nome": user["name"],
        "campos_adicionais": [
            {
                "id": ADDITIONAL_FIELDS["birth_date"],
                "valor": user["birth_date"],
                "id_metadado_servico": 0,
            },
            {
                "id": ADDITIONAL_FIELDS["phone"],
                "valor": user["phone"],
                "id_metadado_servico": 0,
            },
            {
                "id": ADDITIONAL_FIELDS["people_count"],
                "valor": PEOPLE_COUNT,
                "id_metadado_servico": 0,
            },
            {
                "id": ADDITIONAL_FIELDS["email"],
                "valor": user["email"],
                "id_metadado_servico": 0,
            },
            {
                "id": ADDITIONAL_FIELDS["neighborhood"],
                "valor": user["neighborhood"],
                "id_metadado_servico": 0,
            },
            {
                "id": ADDITIONAL_FIELDS["city"],
                "valor": user["city"],
                "id_metadado_servico": 0,
            },
        ],
    }


def book_slot(slot):
    url = f"{BASE_URL}/{COURT_ID}"
    payload = build_booking_payload(slot)

    response = request_with_retry("POST", url, json=payload)
    data = response.json()

    return data.get("sucesso", False), data


def notify_whatsapp(message):
    url = (
        "https://api.callmebot.com/whatsapp.php"
        f"?phone={WA_PHONE}"
        f"&text={quote(message)}"
        f"&apikey={WA_APIKEY}"
    )

    request_with_retry("GET", url)


def main():
    state = load_state()
    state = reset_state_if_needed(state)

    available_slots = get_available_slots()
    target_slots = [slot for slot in available_slots if is_target_slot(slot)]

    print(f"Available slots: {available_slots}")
    print(f"Target slots: {target_slots}")

    if not target_slots:
        print("No target slots found.")
        save_state(state)
        commit_state()
        return

    booked_now = []
    failed_now = []

    for slot in target_slots:
        if slot in state.get("booked_slots", []):
            print(f"Slot already booked previously: {slot}")
            continue

        try:
            success, response_data = book_slot(slot)

            if success:
                print(f"Booked slot successfully: {slot}")
                booked_now.append(slot)
                state["booked_slots"].append(slot)
            else:
                print(f"Failed to book slot: {slot} - {response_data}")
                failed_now.append({"slot": slot, "response": response_data})
                state["failed_slots"].append(slot)

        except Exception as error:
            print(f"Exception while booking slot {slot}: {error}")
            failed_now.append({"slot": slot, "error": str(error)})
            state["failed_slots"].append(slot)

    if booked_now:
        notify_whatsapp(
            "🎾 Agendamento realizado com sucesso!\n\n"
            + "\n".join(f"✅ {slot}" for slot in booked_now)
        )

    if failed_now:
        notify_whatsapp(
            "⚠️ Encontrei horários, mas houve falha ao tentar agendar.\n\n"
            + "\n".join(f"❌ {item['slot']}" for item in failed_now)
        )

    save_state(state)
    commit_state()


if __name__ == "__main__":
    main()
