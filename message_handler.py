
from services_data import SERVICES, MAIN_MENU, FEE_SUMMARY, IMPORTANT_NOTES, GOLDEN_VISA_INFO
from whatsapp_api import send_message


# Keywords mapping for natural language detection
KEYWORDS = {
    "tourist": "entry_permits",
    "visit": "entry_permits",
    "visa": "entry_permits",
    "entry": "entry_permits",
    "travel": "entry_permits",
    "residence": "residence_permits",
    "renewal": "residence_permits",
    "renew": "residence_permits",
    "golden": "golden_visa",
    "green": "residence_permits",
    "emirates id": "emirates_id",
    "id card": "emirates_id",
    "eid": "emirates_id",
    "identity": "emirates_id",
    "cancel": "other_services",
    "cancellation": "other_services",
    "fine": "other_services",
    "overstay": "other_services",
    "fee": "fee_summary",
    "fees": "fee_summary",
    "cost": "fee_summary",
    "price": "fee_summary",
}


def handle_message(sender, message_text):
    """Route incoming messages to appropriate handlers."""
    text = message_text.strip().lower()

    # Main menu triggers
    if text in ["hi", "hello", "hey", "menu", "start", "help", "main", "home", "مرحبا", "السلام"]:
        send_message(sender, MAIN_MENU)
        return

    # Number-based menu selection
    if text == "1":
        send_category(sender, "entry_permits")
    elif text == "2":
        send_category(sender, "residence_permits")
    elif text == "3":
        send_category(sender, "emirates_id")
    elif text == "4":
        send_category(sender, "other_services")
    elif text == "5":
        send_message(sender, GOLDEN_VISA_INFO)
    elif text == "6":
        send_message(sender, FEE_SUMMARY)
    elif text == "7":
        send_message(sender, IMPORTANT_NOTES)
    else:
        # Keyword-based search
        handled = False
        for keyword, action in KEYWORDS.items():
            if keyword in text:
                if action == "golden_visa":
                    send_message(sender, GOLDEN_VISA_INFO)
                elif action == "fee_summary":
                    send_message(sender, FEE_SUMMARY)
                else:
                    send_category(sender, action)
                handled = True
                break

        if not handled:
            send_not_understood(sender)


def send_category(sender, category_key):
    """Send all services in a category with fees and documents."""
    category = SERVICES[category_key]
    response = f"{category['title']}\n{'━' * 20}\n\n"

    for key, service in category["services"].items():
        fee = service["fee"]
        if isinstance(fee, int):
            fee_str = f"AED {fee}"
        else:
            fee_str = f"AED {fee}"

        response += f"📌 *{service['name']}*\n"
        response += f"💰 Fee: {fee_str}\n"
        response += f"📄 Documents:\n"
        for doc in service["documents"]:
            response += f"   • {doc}\n"
        response += "\n"

    response += "━━━━━━━━━━━━━━━━━━━━\n"
    response += "Type *menu* for main menu | Type a keyword for other services"

    # WhatsApp has 4096 character limit - split if needed
    if len(response) > 4000:
        parts = split_message(response, 4000)
        for part in parts:
            send_message(sender, part)
    else:
        send_message(sender, response)


def send_not_understood(sender):
    """Send help message when input is not recognized."""
    msg = (
        "❓ Sorry, I didn't understand that.\n\n"
        "Type *menu* to see all options, or try keywords like:\n"
        "• tourist visa\n"
        "• residence\n"
        "• emirates id\n"
        "• golden visa\n"
        "• fees\n"
        "• overstay\n"
        "• cancellation\n\n"
        "Or type a number (1-7) to select from the menu."
    )
    send_message(sender, msg)


def split_message(text, max_length):
    """Split long messages at line breaks to stay within WhatsApp limits."""
    parts = []
    while len(text) > max_length:
        split_index = text.rfind("\n", 0, max_length)
        if split_index == -1:
            split_index = max_length
        parts.append(text[:split_index])
        text = text[split_index:]
    parts.append(text)
    return parts

