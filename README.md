# Tennis Poller 🎾

Simple Python bot that monitors tennis court availability and sends WhatsApp notifications whenever new slots become available.

## ⚙️ How it works

```text
GitHub Actions → Python Poller → Tennis API → WhatsApp Notification
```

- Runs automatically every 5 minutes using GitHub Actions
- Checks the scheduling API for available courts
- Sends WhatsApp alerts through CallMeBot
- Prevents duplicate notifications during the same day

## 🔐 Required GitHub Secrets

### `BOOKING_USER_JSON`

```json
{
  "cpf": "...",
  "name": "...",
  "birth_date": "...",
  "phone": "...",
  "email": "...",
  "neighborhood": "...",
  "city": "..."
}
```

### `BASE_URL`

```text
Private booking API URL
```

### `WA_PHONE`

```text
WhatsApp phone number
```

### `WA_APIKEY`

```text
CallMeBot API key
```

## ⚙️ Required GitHub Variables

### `COURT_ID`

```text
Court identifier
```

### `TARGET_TIMES`

```text
08:00,09:20
```

## 🛠 Stack

- Python
- GitHub Actions
- Requests
- CallMeBot API
