
import requests
from config import WHATSAPP_TOKEN, WHATSAPP_API_URL


def send_message(to, text):
    """Send a text message via WhatsApp Cloud API."""
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    print(f"📤 Message sent to {to}: {response.status_code}")
    return response.json()


def send_interactive_list(to, header, body, button_text, sections):
    """Send an interactive list message."""
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": header},
            "body": {"text": body},
            "action": {
                "button": button_text,
                "sections": sections
            }
        }
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    return response.json()


def send_interactive_buttons(to, body, buttons):
    """Send interactive reply buttons (max 3)."""
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    button_list = []
    for btn in buttons:
        button_list.append({
            "type": "reply",
            "reply": {"id": btn["id"], "title": btn["title"]}
        })

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {"buttons": button_list}
        }
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    return response.json()

