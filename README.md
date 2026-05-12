# Tennis Poller 🎾

Simple Python bot that monitors tennis court availability and sends WhatsApp notifications whenever new slots become available.

## ⚙️ How it works

```text
GitHub Actions → Python Poller → Tennis API → WhatsApp Notification
```

- Runs automatically every 5 minutes using GitHub Actions
- Monitors tennis court availability through the scheduling API
- Sends WhatsApp alerts whenever available slots are found
- Includes the direct booking page link in the notification
- Prevents duplicate notifications during the same day

## 🔐 Required GitHub Secrets

### `BASE_URL`

Private API base URL used to fetch available slots.

### `WA_PHONE`

WhatsApp phone number used by CallMeBot.

### `WA_APIKEY`

CallMeBot API key.

---

## ⚙️ Required GitHub Variables

### `COURT_ID`

Tennis court identifier.

Example:

```text
2186
```

### `BOOKING_PAGE_BASE_URL`

Booking page base URL.

---

## 🛠 Stack

- Python
- GitHub Actions
- Requests
- CallMeBot API
