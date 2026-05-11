import requests, os, json
from datetime import date
from urllib.parse import quote

API_URL    = os.environ["API_URL"]
API_FIELD  = os.environ["API_FIELD"]
STATE_FILE = "state.json"

def get_data():
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json()

def notify_whatsapp(message):
    phone  = os.environ["WA_PHONE"]
    apikey = os.environ["WA_APIKEY"]
    url = (
        f"https://api.callmebot.com/whatsapp.php"
        f"?phone={phone}&text={quote(message)}&apikey={apikey}"
    )
    res = requests.get(url)
    print(f"WhatsApp status: {res.status_code}")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"notified": False, "last_run_date": None}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def commit_state():
    os.system('git config user.email "bot@github.com"')
    os.system('git config user.name "Poller Bot"')
    os.system(f'git add {STATE_FILE}')
    os.system('git commit -m "chore: atualiza state" || true')
    os.system('git push')

def main():
    today = str(date.today())
    state = load_state()

    if state["last_run_date"] != today:
        print("📅 Primeiro job do dia — resetando flag...")
        state = {"notified": False, "last_run_date": today}
        save_state(state)
        commit_state()

    if state["notified"]:
        print("🔕 Já notificado hoje. Encerrando.")
        return

    print("Consultando API...")
    data = get_data()
    field = data.get(API_FIELD, [])
    print(f"Campo '{API_FIELD}': {field}")

    if field:
        print("✅ Encontrado! Enviando notificação...")
        notify_whatsapp(
            f"🗓️ Horários disponíveis para agendamento!\n"
            f"Acesse agora: {API_URL}\n"
            f"Total: {len(field)} horário(s)"
        )
        state["notified"] = True
        save_state(state)
        commit_state()
    else:
        print("❌ Nenhum horário disponível.")

if __name__ == "__main__":
    main()
