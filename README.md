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

## 🛠 Stack

- Python
- GitHub Actions
- Requests
- CallMeBot API
