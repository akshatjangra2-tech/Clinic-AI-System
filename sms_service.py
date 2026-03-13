# sms_service.py
# Femme Med Hospital – SMS Follow-up Service (Normal SMS Only)

import requests

# TEMP TEST CONFIG (CHANGE LATER)
SMS_API_KEY = "SBYdapwjkTGQtA6zOr9hx2F5Egbs07CHulmJvLoPXU8DRyZc34w6lR0N3mBHViJtaAoG8xPudqejrkMX"
SMS_SENDER = "FEMMED"


def send_sms(phone: str, message: str):
    """
    Send a normal SMS (non-promotional, hospital reminder style)
    """

    if not phone or not message:
        return

    url = "https://www.fast2sms.com/dev/bulkV2"

    payload = {
        "route": "q",
        "language": "english",
        "numbers": phone,
        "message": message
    }

    headers = {
        "authorization": SMS_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        requests.post(url, json=payload, headers=headers, timeout=5)
    except Exception:
        # Silent fail – hospital behaviour (no crash)
        pass
