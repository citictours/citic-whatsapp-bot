
import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ============================================================
# CONFIGURATION
# ============================================================
WHATSAPP_TOKEN = os.environ.get('WHATSAPP_TOKEN')
PHONE_NUMBER_ID = os.environ.get('PHONE_NUMBER_ID')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN', 'citic_verify_2026')
PORT = int(os.environ.get('PORT', 5000))

API_VERSION = 'v18.0'
API_URL = f'https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages'

HEADERS = {
    'Authorization': f'Bearer {WHATSAPP_TOKEN}',
    'Content-Type': 'application/json'
}


# ============================================================
# SERVICE DATABASE - ALL GDRFA, ICP & VFS SERVICES
# ============================================================
SERVICES = {
    "tourist_visa": {
        "name": "Tourist Visa (Single Entry)",
        "category": "GDRFA",
        "fee": "AED 300",
        "processing": "3-5 working days",
        "validity": "30 days",
        "docs": [
            "Passport copy (6+ months validity)",
            "Colored photo (white background)",
            "Travel insurance",
            "Return flight ticket",
            "Hotel booking confirmation"
        ]
    },
    "tourist_multi": {
        "name": "Tourist Visa (Multiple Entry)",
        "category": "GDRFA",
        "fee": "AED 500",
        "processing": "3-5 working days",
        "validity": "Multiple entries",
        "docs": [
            "Passport copy (6+ months validity)",
            "Colored photo (white background)",
            "Travel insurance",
            "Hotel booking",
            "Bank statement (3 months)"
        ]
    },
    "tourist_extension": {
        "name": "Tourist Visa Extension",
        "category": "GDRFA",
        "fee": "AED 600",
        "processing": "1-2 working days",
        "validity": "30 days extension",
        "docs": [
            "Original passport",
            "Current visa copy",
            "Passport photo",
            "Sponsor's Emirates ID copy"
        ]
    },
    "medical_visa": {
        "name": "Medical Visa (90 days)",
        "category": "GDRFA",
        "fee": "AED 200",
        "processing": "3-5 working days",
        "validity": "90 days",
        "docs": [
            "Passport copy (6+ months validity)",
            "Medical report from home country",
            "Hospital appointment letter (UAE)",
            "Passport photo",
            "Travel insurance"
        ]
    },
    "work_permit": {
        "name": "Work Entry Permit",
        "category": "GDRFA",
        "fee": "AED 500",
        "processing": "3-5 working days",
        "validity": "60 days",
        "docs": [
            "Passport copy (6+ months validity)",
            "Labor contract / Offer letter",
            "Sponsor's trade license",
            "Passport photo",
            "Educational certificates (attested)"
        ]
    },
    "family_visa": {
        "name": "Family Entry Permit (Spouse/Children)",
        "category": "GDRFA",
        "fee": "AED 200-300",
        "processing": "3-5 working days",
        "validity": "60 days",
        "docs": [
            "Passport copies (sponsor + family)",
            "Marriage/Birth certificate (attested)",
            "Sponsor's residence visa copy",
            "Salary certificate (min AED 4,000)",
            "Passport photos"
        ]
    },
    "residence_1yr": {
        "name": "Residence Permit (1 Year)",
        "category": "GDRFA",
        "fee": "AED 310-360",
        "processing": "5-10 working days",
        "validity": "1 year",
        "docs": [
            "Valid passport (6+ months)",
            "Entry permit",
            "Emirates ID application",
            "Medical fitness certificate",
            "Tenancy contract (Ejari)",
            "Health insurance"
        ]
    },
    "residence_2yr": {
        "name": "Residence Permit (2 Years)",
        "category": "GDRFA",
        "fee": "AED 410-460",
        "processing": "5-10 working days",
        "validity": "2 years",
        "docs": [
            "Valid passport (6+ months)",
            "Entry permit",
            "Emirates ID application",
            "Medical fitness certificate",
            "Tenancy contract (Ejari)",
            "Sponsor's trade license",
            "Health insurance",
            "Passport photos"
        ]
    },
    "residence_renewal": {
        "name": "Residence Permit Renewal",
        "category": "GDRFA",
        "fee": "AED 460-560",
        "processing": "5-10 working days",
        "validity": "2 years",
        "docs": [
            "Valid passport (6+ months)",
            "Current residence visa copy",
            "Emirates ID",
            "Medical fitness certificate",
            "Tenancy contract (Ejari)",
            "Labor contract",
            "Health insurance"
        ]
    },
    "golden_visa": {
        "name": "Golden Visa (10 Years)",
        "category": "GDRFA",
        "fee": "~AED 9,735 (main applicant) | Dependent: ~AED 5,400",
        "processing": "15-30 working days",
        "validity": "10 years (renewable)",
        "docs": [
            "Valid passport (6+ months)",
            "Property title deed (AED 2M+) OR",
            "Business investment proof OR",
            "Specialized talent contract OR",
            "Academic certificates (researchers)",
            "Emirates ID",
            "Medical fitness certificate",
            "Health insurance",
            "Bank statements",
            "Passport photos"
        ]
    },
    "green_visa": {
        "name": "Green Visa (5 Years)",
        "category": "GDRFA",
        "fee": "~AED 1,200",
        "processing": "10-15 working days",
        "validity": "5 years",
        "docs": [
            "Valid passport (6+ months)",
            "Freelance permit or employment contract",
            "Bank statements (AED 15,000+/month)",
            "Emirates ID",
            "Medical fitness certificate",
            "Health insurance",
            "Tenancy contract (Ejari)"
        ]
    },
    "visa_cancel": {
        "name": "Visa Cancellation",
        "category": "GDRFA",
        "fee": "AED 100-200",
        "processing": "1-3 working days",
        "validity": "30-day grace period after",
        "docs": [
            "Original passport",
            "Current residence visa",
            "Emirates ID",
            "Cancellation request from sponsor"
        ]
    },
    "status_change": {
        "name": "Status Adjustment (Inside UAE)",
        "category": "GDRFA",
        "fee": "AED 500-650",
        "processing": "5-10 working days",
        "validity": "As per new visa",
        "docs": [
            "Valid passport",
            "Current visa copy",
            "New sponsor documents",
            "Emirates ID",
            "Medical fitness certificate"
        ]
    },
    "overstay_fine": {
        "name": "Visa Overstay Fine",
        "category": "GDRFA",
        "fee": "AED 50/day (after grace period)",
        "processing": "Immediate",
        "validity": "N/A",
        "docs": [
            "Passport",
            "Expired visa copy",
            "Fine payment"
        ]
    },
    "emirates_id_new": {
        "name": "New Emirates ID (Residents)",
        "category": "ICP",
        "fee": "AED 100 per year of residence",
        "processing": "5-10 working days",
        "validity": "Same as residence visa",
        "docs": [
            "Valid passport (6+ months)",
            "Residence visa copy",
            "Passport photo",
            "Biometric registration"
        ]
    },
    "emirates_id_renewal": {
        "name": "Emirates ID Renewal",
        "category": "ICP",
        "fee": "AED 100 per year of validity",
        "processing": "5-10 working days",
        "validity": "Same as residence visa",
        "docs": [
            "Valid passport",
            "Current Emirates ID",
            "UAE PASS account",
            "Updated photo (if required)"
        ]
    },
    "emirates_id_lost": {
        "name": "Lost/Damaged Emirates ID Replacement",
        "category": "ICP",
        "fee": "~AED 300 + AED 40-70 (application)",
        "processing": "7-10 working days",
        "validity": "Same as original",
        "docs": [
            "Police report (for lost ID)",
            "Damaged card (if applicable)",
            "Passport copy",
            "Application form"
        ]
    },
    "schengen": {
        "name": "Schengen Visa (Europe - 27 Countries)",
        "category": "VFS Global",
        "fee": "EUR 90 (Adults) | EUR 45 (6-12yr) | Free (Under 6)\nVFS Fee: ~EUR 30-36",
        "processing": "15-45 calendar days",
        "validity": "Up to 90 days in 180-day period",
        "docs": [
            "Passport (6+ months, 2 blank pages)",
            "UAE residence visa (90+ days validity)",
            "Completed application form",
            "2 photos (35x45mm, white background)",
            "Travel insurance (EUR 30,000 minimum)",
            "Flight booking",
            "Hotel reservation",
            "Bank statements (3 months)",
            "Salary certificate",
            "NOC from employer",
            "Cover letter",
            "Day-by-day travel itinerary"
        ]
    },
    "uk_visa": {
        "name": "UK Standard Visitor Visa",
        "category": "VFS Global",
        "fee": "GBP 115 (6mo) | GBP 400 (2yr) | GBP 771 (5yr) | GBP 963 (10yr)\nPriority: +GBP 250 | Super Priority: +GBP 1,000",
        "processing": "15-20 working days (Standard)",
        "validity": "6 months to 10 years",
        "docs": [
            "Valid passport (6+ months)",
            "UAE residence visa copy",
            "Online application (GOV.UK)",
            "Biometric appointment",
            "Bank statements (6 months)",
            "Salary certificate",
            "Employer NOC",
            "Travel insurance",
            "Accommodation proof",
            "Flight itinerary",
            "Previous travel history"
        ]
    },
    "uk_work": {
        "name": "UK Work Visa (Skilled Worker)",
        "category": "VFS Global",
        "fee": "GBP 719-1,420",
        "processing": "3-8 weeks",
        "validity": "Up to 5 years",
        "docs": [
            "Valid passport",
            "Certificate of Sponsorship (CoS)",
            "English language test",
            "Financial proof (GBP 1,270 for 28 days)",
            "Criminal record certificate",
            "TB test results"
        ]
    },
    "uk_student": {
        "name": "UK Student Visa",
        "category": "VFS Global",
        "fee": "GBP 490",
        "processing": "3-6 weeks",
        "validity": "Duration of course",
        "docs": [
            "Valid passport",
            "CAS letter from university",
            "Financial proof (tuition + living costs)",
            "English test (IELTS)",
            "TB test results",
            "Academic transcripts"
        ]
    },
    "usa_visa": {
        "name": "USA Visitor Visa (B1/B2)",
        "category": "VFS Global",
        "fee": "USD 185 (~AED 680)",
        "processing": "Interview required - varies",
        "validity": "Up to 10 years (multiple entry)",
        "docs": [
            "Valid passport (6+ months)",
            "DS-160 form (online)",
            "Photo (51x51mm)",
            "Interview appointment confirmation",
            "Bank statements (6 months)",
            "Employment letter",
            "Property documents (ties to UAE)",
            "Previous travel history",
            "Invitation letter (if applicable)",
            "Travel itinerary"
        ]
    },
    "canada_visa": {
        "name": "Canada Visitor Visa",
        "category": "VFS Global",
        "fee": "CAD 100 (~AED 270)",
        "processing": "15-45 working days",
        "validity": "Up to 10 years",
        "docs": [
            "Valid passport (6+ months)",
            "UAE residence visa copy",
            "Bank statements (6 months)",
            "Employment letter",
            "Travel history",
            "Family ties proof",
            "Travel insurance",
            "Purpose of visit letter",
            "Invitation letter (if applicable)"
        ]
    },
    "canada_study": {
        "name": "Canada Study Permit",
        "category": "VFS Global",
        "fee": "CAD 150 (~AED 405)",
        "processing": "4-12 weeks",
        "validity": "Duration of study",
        "docs": [
            "Valid passport",
            "Acceptance letter from DLI",
            "Financial proof",
            "Medical examination",
            "Police clearance",
            "Statement of purpose",
            "Academic transcripts"
        ]
    },
    "australia_visa": {
        "name": "Australia Visitor Visa (Subclass 600)",
        "category": "VFS Global",
        "fee": "AUD 190 (~AED 460)",
        "processing": "15-30 working days",
        "validity": "3-12 months",
        "docs": [
            "Valid passport (6+ months)",
            "UAE residence visa copy",
            "Bank statements (3-6 months)",
            "Employment letter",
            "Travel insurance",
            "Travel itinerary",
            "Accommodation proof",
            "Previous travel history"
        ]
    },
    "new_zealand": {
        "name": "New Zealand Visitor Visa",
        "category": "VFS Global",
        "fee": "NZD 246 (~AED 550)",
        "processing": "20-25 working days",
        "validity": "Up to 9 months",
        "docs": [
            "Valid passport (6+ months)",
            "UAE residence visa",
            "Bank statements (3 months)",
            "Employment letter",
            "Travel insurance",
            "Flight itinerary",
            "Accommodation proof"
        ]
    },
    "malaysia_visa": {
        "name": "Malaysia eVisa",
        "category": "VFS Global",
        "fee": "AED 200-350",
        "processing": "3-5 working days",
        "validity": "30 days",
        "docs": [
            "Valid passport (6+ months)",
            "Passport photo",
            "Flight booking",
            "Hotel booking",
            "Bank statement (1 month)"
        ]
    }
}


# ============================================================
# MESSAGE FUNCTIONS
# ============================================================

def send_text(to, text):
    """Send plain text message"""
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.json()


def send_buttons(to, body, buttons, header=None, footer=None):
    """Send interactive button message (max 3 buttons)"""
    interactive = {
        "type": "button",
        "body": {"text": body},
        "action": {"buttons": [
            {"type": "reply", "reply": {"id": b["id"], "title": b["title"][:20]}}
            for b in buttons
        ]}
    }
    if header:
        interactive["header"] = {"type": "text", "text": header}
    if footer:
        interactive["footer"] = {"text": footer}

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": interactive
    }
    return requests.post(API_URL, headers=HEADERS, json=payload).json()


def send_list(to, body, button_text, sections, header=None, footer=None):
    """Send interactive list message"""
    interactive = {
        "type": "list",
        "body": {"text": body},
        "action": {"button": button_text[:20], "sections": sections}
    }
    if header:
        interactive["header"] = {"type": "text", "text": header}
    if footer:
        interactive["footer"] = {"text": footer}

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": interactive
    }
    return requests.post(API_URL, headers=HEADERS, json=payload).json()


# ============================================================
# SERVICE RESPONSE FORMATTER
# ============================================================

def format_service(service):
    """Format service details for WhatsApp"""
    docs = "\n".join([f"  {i+1}. {d}" for i, d in enumerate(service['docs'])])
    return (
        f"✈️ *CITIC Tourism & Leisure Consulting*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📋 *{service['name']}*\n"
        f"🏛️ Authority: {service['category']}\n\n"
        f"💰 *Fee:* {service['fee']}\n"
        f"⏱️ *Processing:* {service['processing']}\n"
        f"📅 *Validity:* {service['validity']}\n\n"
        f"📄 *Required Documents:*\n{docs}\n\n"
        f"⚠️ _All UAE fees +5% VAT_\n"
        f"_Typing/service fees: AED 50-200 extra_\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📞 +971 55 621 7946\n"
        f"💬 Type *menu* for all services"
    )


# ============================================================
# CHATBOT FLOWS
# ============================================================

def send_welcome(to):
    """Send welcome message with buttons"""
    send_text(to,
        "✈️ *Welcome to CITIC Tourism & Leisure Consulting!*\n\n"
        "Your trusted partner for UAE Immigration & International Visa Services 🌍\n\n"
        "📞 +971 55 621 7946"
    )
    send_buttons(to,
        "How can we help you today?",
        [
            {"id": "menu_uae", "title": "🇦🇪 UAE Services"},
            {"id": "menu_intl", "title": "🌍 International"},
            {"id": "menu_fees", "title": "💰 All Fees"}
        ],
        header="CITIC Service Assistant",
        footer="Available 24/7"
    )


def send_uae_menu(to):
    """Send UAE services list"""
    send_list(to,
        "🇦🇪 *UAE Immigration Services*\n\nSelect a service for fees & required documents:",
        "View Services",
        [
            {
                "title": "📋 Visas & Entry Permits",
                "rows": [
                    {"id": "s_tourist_visa", "title": "Tourist Visa (Single)", "description": "AED 300 | 30 days"},
                    {"id": "s_tourist_multi", "title": "Tourist Visa (Multiple)", "description": "AED 500"},
                    {"id": "s_tourist_extension", "title": "Tourist Extension", "description": "AED 600 | +30 days"},
                    {"id": "s_medical_visa", "title": "Medical Visa", "description": "AED 200 | 90 days"},
                    {"id": "s_work_permit", "title": "Work Entry Permit", "description": "AED 500 | 60 days"},
                    {"id": "s_family_visa", "title": "Family Entry Permit", "description": "AED 200-300"},
                ]
            },
            {
                "title": "🏠 Residence Permits",
                "rows": [
                    {"id": "s_residence_1yr", "title": "Residence (1 Year)", "description": "AED 310-360"},
                    {"id": "s_residence_2yr", "title": "Residence (2 Years)", "description": "AED 410-460"},
                    {"id": "s_residence_renewal", "title": "Residence Renewal", "description": "AED 460-560"},
                    {"id": "s_golden_visa", "title": "⭐ Golden Visa (10yr)", "description": "~AED 9,735"},
                    {"id": "s_green_visa", "title": "🟢 Green Visa (5yr)", "description": "~AED 1,200"},
                ]
            },
            {
                "title": "🪪 ID & Other Services",
                "rows": [
                    {"id": "s_emirates_id_new", "title": "New Emirates ID", "description": "AED 100/year"},
                    {"id": "s_emirates_id_renewal", "title": "Emirates ID Renewal", "description": "AED 100/year"},
                    {"id": "s_emirates_id_lost", "title": "Lost/Damaged ID", "description": "~AED 340-370"},
                    {"id": "s_visa_cancel", "title": "Visa Cancellation", "description": "AED 100-200"},
                    {"id": "s_status_change", "title": "Status Adjustment", "description": "AED 500-650"},
                ]
            }
        ],
        header="GDRFA & ICP Services",
        footer="All fees +5% VAT"
    )


def send_intl_menu(to):
    """Send international visa list"""
    send_list(to,
        "🌍 *International Visa Services*\n\nWe process visas to 60+ countries via VFS Global:",
        "View Countries",
        [
            {
                "title": "🇪🇺 Europe & UK",
                "rows": [
                    {"id": "s_schengen", "title": "Schengen (27 countries)", "description": "EUR 90 | 15-45 days"},
                    {"id": "s_uk_visa", "title": "🇬🇧 UK Visitor Visa", "description": "GBP 115-963"},
                    {"id": "s_uk_work", "title": "🇬🇧 UK Work Visa", "description": "GBP 719-1,420"},
                    {"id": "s_uk_student", "title": "🇬🇧 UK Student Visa", "description": "GBP 490"},
                ]
            },
            {
                "title": "🌎 Americas",
                "rows": [
                    {"id": "s_usa_visa", "title": "🇺🇸 USA Visa (B1/B2)", "description": "USD 185 | Interview"},
                    {"id": "s_canada_visa", "title": "🇨🇦 Canada Visitor", "description": "CAD 100"},
                    {"id": "s_canada_study", "title": "🇨🇦 Canada Study", "description": "CAD 150"},
                ]
            },
            {
                "title": "🌏 Asia & Oceania",
                "rows": [
                    {"id": "s_australia_visa", "title": "🇦🇺 Australia", "description": "AUD 190 | 15-30 days"},
                    {"id": "s_new_zealand", "title": "🇳🇿 New Zealand", "description": "NZD 246"},
                    {"id": "s_malaysia_visa", "title": "🇲🇾 Malaysia eVisa", "description": "AED 200-350"},
                ]
            }
        ],
        header="VFS Global Services",
        footer="Processing times approximate"
    )


def send_fees(to):
    """Send fee summary"""
    send_text(to,
        "💰 *CITIC - Complete Fee Summary*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🇦🇪 *GDRFA (Dubai):*\n"
        "• Tourist Visa: AED 300-500\n"
        "• Tourist Extension: AED 600\n"
        "• Medical Visa: AED 200\n"
        "• Work Permit: AED 500\n"
        "• Family Visa: AED 200-300\n"
        "• Residence (1yr): AED 310-360\n"
        "• Residence (2yr): AED 410-460\n"
        "• Renewal: AED 460-560\n"
        "• Golden Visa (10yr): ~AED 9,735\n"
        "• Green Visa (5yr): ~AED 1,200\n"
        "• Cancellation: AED 100-200\n"
        "• Status Change: AED 500-650\n"
        "• Overstay Fine: AED 50/day\n\n"
        "🪪 *ICP:*\n"
        "• Emirates ID: AED 100/year\n"
        "• ID Replacement: ~AED 340-370\n"
        "• Late Fine: AED 20/day\n\n"
        "🌍 *VFS Global:*\n"
        "• Schengen: EUR 90 (~AED 360)\n"
        "• UK (6mo): GBP 115 (~AED 530)\n"
        "• UK (2yr): GBP 400 (~AED 1,850)\n"
        "• UK Work: GBP 719-1,420\n"
        "• UK Student: GBP 490\n"
        "• USA: USD 185 (~AED 680)\n"
        "• Canada: CAD 100 (~AED 270)\n"
        "• Canada Study: CAD 150\n"
        "• Australia: AUD 190 (~AED 460)\n"
        "• New Zealand: NZD 246 (~AED 550)\n"
        "• Malaysia: AED 200-350\n\n"
        "⚠️ _All UAE fees +5% VAT_\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💬 Type service name for full details\n"
        "📞 +971 55 621 7946"
    )


# ============================================================
# KEYWORD MATCHING
# ============================================================

def find_service(text):
    """Find service by keyword matching"""
    text = text.lower().strip()

    keyword_map = {
        "tourist_visa": ["tourist visa", "tourist single", "visit visa", "tourism", "tourist"],
        "tourist_multi": ["tourist multiple", "multi entry", "multiple entry"],
        "tourist_extension": ["tourist extension", "extend tourist", "visa extension", "extend visa", "extension"],
        "medical_visa": ["medical visa", "medical", "treatment visa", "hospital visa"],
        "work_permit": ["work permit", "work visa", "employment visa", "work entry", "job visa", "work"],
        "family_visa": ["family visa", "family", "spouse visa", "wife visa", "children visa", "dependent"],
        "residence_1yr": ["1 year residence", "one year", "1yr residence"],
        "residence_2yr": ["2 year residence", "two year", "2yr residence", "residence permit", "residence"],
        "residence_renewal": ["renewal", "renew residence", "renew visa", "visa renewal", "renew"],
        "golden_visa": ["golden visa", "golden", "10 year", "investor visa", "10yr"],
        "green_visa": ["green visa", "5 year", "freelance visa", "self sponsored", "5yr"],
        "visa_cancel": ["cancel", "cancellation", "cancel visa"],
        "status_change": ["status change", "status adjustment", "change status", "transfer"],
        "overstay_fine": ["overstay", "fine", "penalty", "expired"],
        "emirates_id_new": ["emirates id", "new id", "eid", "id card", "identity"],
        "emirates_id_renewal": ["id renewal", "renew id", "renew emirates"],
        "emirates_id_lost": ["lost id", "damaged id", "replace id"],
        "schengen": ["schengen", "europe", "germany", "france", "italy", "spain", "eu visa", "netherlands", "switzerland"],
        "uk_visa": ["uk visa", "uk", "england", "britain", "london", "united kingdom"],
        "uk_work": ["uk work", "work uk", "skilled worker uk"],
        "uk_student": ["uk student", "study uk", "uk study"],
        "usa_visa": ["usa", "us visa", "america", "american visa", "b1", "b2", "united states"],
        "canada_visa": ["canada", "canadian"],
        "canada_study": ["canada study", "study canada"],
        "australia_visa": ["australia", "australian"],
        "new_zealand": ["new zealand", "nz visa"],
        "malaysia_visa": ["malaysia", "malaysian"],
    }

    for service_key, keywords in keyword_map.items():
        for keyword in keywords:
            if keyword in text:
                return service_key
    return None


# ============================================================
# MAIN MESSAGE HANDLER
# ============================================================

def handle_message(sender, msg_type, data):
    """Process all incoming messages"""

    if msg_type == "text":
        text = data.get("text", {}).get("body", "").strip()
        text_lower = text.lower()

        # Greetings
        if text_lower in ["hi", "hello", "hey", "start", "menu", "help", "hola", "marhaba", "assalam", "salam"]:
            send_welcome(sender)
            return

        # Fees
        if text_lower in ["fees", "fee", "price", "prices", "cost", "charges", "pricing"]:
            send_fees(sender)
            return

        # All services
        if text_lower in ["all", "all services", "services", "list"]:
            send_uae_menu(sender)
            return

        # UAE menu
        if text_lower in ["uae", "gdrfa", "icp", "dubai"]:
            send_uae_menu(sender)
            return

        # International menu
        if text_lower in ["international", "vfs", "abroad", "countries"]:
            send_intl_menu(sender)
            return

        # Search for specific service
        service_key = find_service(text_lower)
        if service_key and service_key in SERVICES:
            send_text(sender, format_service(SERVICES[service_key]))
            send_buttons(sender,
                "What would you like to do next?",
                [
                    {"id": "apply_now", "title": "📝 Apply Now"},
                    {"id": "menu_uae", "title": "📋 More Services"},
                    {"id": "back_menu", "title": "🏠 Main Menu"}
                ]
            )
            return

        # Default - not understood
        send_buttons(sender,
            f"I'm not sure about \"{text}\".\nLet me help you find what you need:",
            [
                {"id": "menu_uae", "title": "🇦🇪 UAE Services"},
                {"id": "menu_intl", "title": "🌍 International"},
                {"id": "menu_fees", "title": "💰 Fees"}
            ],
            footer="Or type: golden visa, schengen, uk visa"
        )

    elif msg_type == "interactive":
        interactive = data.get("interactive", {})
        itype = interactive.get("type", "")

        if itype == "button_reply":
            btn_id = interactive["button_reply"]["id"]
            handle_button(sender, btn_id)

        elif itype == "list_reply":
            list_id = interactive["list_reply"]["id"]
            handle_list_selection(sender, list_id)

    elif msg_type in ["image", "document"]:
        send_text(sender,
            "📎 *Document Received!* ✅\n\n"
            "Thank you! Our team will review it shortly.\n"
            "We'll respond within 30 minutes.\n\n"
            "📞 Urgent? Call: +971 55 621 7946"
        )


def handle_button(sender, btn_id):
    """Handle button clicks"""
    actions = {
        "menu_uae": lambda: send_uae_menu(sender),
        "menu_intl": lambda: send_intl_menu(sender),
        "menu_fees": lambda: send_fees(sender),
        "back_menu": lambda: send_welcome(sender),
        "apply_now": lambda: send_text(sender,
            "📝 *Ready to Apply?*\n\n"
            "Please send your documents:\n"
            "1. Passport copy (front page)\n"
            "2. UAE visa copy\n"
            "3. Passport photo\n\n"
            "📎 Send as photos or PDF\n\n"
            "📍 Or visit our office:\n"
            "⏰ Sun-Thu: 9AM-6PM\n"
            "📞 +971 55 621 7946"
        ),
    }
    action = actions.get(btn_id, lambda: send_welcome(sender))
    action()


def handle_list_selection(sender, list_id):
    """Handle list item selections"""
    service_key = list_id.replace("s_", "")

    if service_key in SERVICES:
        send_text(sender, format_service(SERVICES[service_key]))
        send_buttons(sender,
            "What would you like to do?",
            [
                {"id": "apply_now", "title": "📝 Apply Now"},
                {"id": "menu_uae", "title": "◀️ More Services"},
                {"id": "back_menu", "title": "🏠 Main Menu"}
            ]
        )
    else:
        send_welcome(sender)


# ============================================================
# WEBHOOK ENDPOINTS
# ============================================================

@app.route('/webhook', methods=['GET'])
def verify():
    """Webhook verification by Meta"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print("✅ Webhook verified successfully!")
        return challenge, 200
    print("❌ Webhook verification failed!")
    return 'Forbidden', 403


@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive and process incoming messages"""
    data = request.get_json()

    if data.get('object') == 'whatsapp_business_account':
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                for message in value.get('messages', []):
                    sender = message['from']
                    msg_type = message['type']
                    handle_message(sender, msg_type, message)

    return jsonify({"status": "ok"}), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "bot": "CITIC Tourism & Leisure Consulting",
        "phone": "+971556217946",
        "services": len(SERVICES)
    })


@app.route('/', methods=['GET'])
def home():
    """Home page"""
    return jsonify({
        "name": "CITIC Tourism WhatsApp Bot",
        "status": "active",
        "version": "1.0.0",
        "endpoints": {
            "webhook": "/webhook",
            "health": "/health"
        }
    })


# ============================================================
# START SERVER
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("  ✈️  CITIC Tourism & Leisure Consulting")
    print("  📱 WhatsApp Bot: +971 55 621 7946")
    print("=" * 60)
    print(f"  🔗 Webhook: http://localhost:{PORT}/webhook")
    print(f"  💚 Health:  http://localhost:{PORT}/health")
    print("=" * 60)
    app.run(host='0.0.0.0', port=PORT, debug=True)

