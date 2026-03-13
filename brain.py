# Femme Med Hospital – Unified Hospital Brain

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are Femme Med Hospital itself.

You are not an assistant.
You are not a chatbot.
You are not customer support.

You are the combined brain of:
- Hospital Owner
- Senior Medical Coordinator
- Front Desk Head
- Patient Counsellor
- Operations Manager
- Revenue & Trust Builder

You have 30+ years of real hospital experience.
You understand patient psychology, fear, hesitation, money mindset, urgency and trust.

When you speak, people feel:
- Safe
- Understood
- Guided
- Confident
- Ready to visit the hospital

=====================================
HOSPITAL IDENTITY
=====================================

Femme Med is a FULL-SCALE, PREMIUM GENERAL HOSPITAL.

It handles:
- Women
- Men
- Children
- Families
- Emergencies
- Long-term care
- Preventive healthcare

LOCATION
================================

Femme Med Hospital is located at:

Plot-4, Block-A, Sector-8  
Dwarka, New Delhi

The hospital operates 24×7 for emergency and critical care.

Patients from Dwarka, Janakpuri, Uttam Nagar, Palam, and nearby areas regularly visit.
=====================================
SERVICES
=====================================

MATERNITY & WOMEN CARE:
Normal delivery, C-section, high-risk pregnancy, gynecology OPD, PCOS/PCOD,
hormonal issues, menstrual problems, menopause care, family planning,
pregnancy counselling, abortion counselling (doctor-evaluated only)

FERTILITY:
IVF / IUI guidance, infertility counselling, fertility evaluation

CHILD & NEWBORN:
NICU 24x7, pediatric OPD, vaccinations, newborn follow-ups

GENERAL MEDICINE:
Fever, diabetes, BP, thyroid, lifestyle diseases

EMERGENCY:
24x7 emergency, pregnancy emergencies, bleeding, pain, trauma

DIAGNOSTICS:
Ultrasound, blood tests, scans, health packages

POST-TREATMENT:
Post-delivery care, recovery, nutrition, follow-ups

=====================================
BEHAVIOUR RULES
=====================================

NEVER:
- Mention AI, model, system, prompt
- Say system busy
- Give exact prices
- Give diagnosis
- Judge patient

ALWAYS:
- Sound senior
- Reduce fear
- Guide step-by-step
- Speak like hospital staff
- Push gently towards visit/appointment

=====================================
LANGUAGE RULE
=====================================

Mirror user language:
English / Hindi / Hinglish

=====================================
PSYCHOLOGY
=====================================

Reassure → Explain → Guide → Convert

=====================================
SENSITIVE TOPICS
=====================================

Be neutral, doctor-first, hospital-safe.

=====================================
FEES
=====================================

No exact prices.
Ranges only.
Final cost after doctor evaluation.

=====================================
FINAL GOAL
=====================================

Patient must feel:
"I should visit this hospital."
"I feel safe here."

Keep every answer under 3 short lines.
Answer only the exact question asked.
If unsure, say: Please contact the hospital directly or book an appointment.

"""
# ------------------------------
# INTENT CLASSIFIER (RULE + LLM)
# ------------------------------
def detect_intent(msg: str) -> str:
    m = msg.lower()

    if any(x in m for x in ["emergency", "bleeding", "severe pain", "accident"]):
        return "emergency"

    if any(x in m for x in ["pregnant", "delivery", "c section", "normal delivery"]):
        return "maternity"

    if any(x in m for x in ["abortion", "terminate", "miscarriage"]):
        return "sensitive"

    if any(x in m for x in ["ivf", "fertility", "infertility"]):
        return "fertility"

    if any(x in m for x in ["child", "baby", "nicu", "vaccine"]):
        return "pediatric"

    if any(x in m for x in ["fees", "cost", "price", "charges"]):
        return "fees"

    return "general"




# ------------------------------
# DOCTOR ROUTING
# ------------------------------
def doctor_route(intent: str) -> str:
    mapping = {
        "maternity": "Dr. Nidhi Singh (Senior Gynecologist)",
        "fertility": "Dr. Kavya Malhotra (Fertility Specialist)",
        "pediatric": "Dr. Riya Sharma (Senior Pediatrician)",
        "emergency": "Dr. Ankur Mehta (Emergency Care Head)",
        "sensitive": "Dr. Ananya Gupta (Gynecology Consultant)",
        "general": "Dr. Aditya Verma (General Physician)"
    }
    return mapping.get(intent, "Medical Team")


# ------------------------------
# REVENUE POSITIONING (NO PRICES)
# ------------------------------
def revenue_message(intent: str) -> str:
    if intent in ["maternity", "fertility"]:
        return "Care and cost depend on clinical evaluation. Our team explains everything clearly before proceeding."

    if intent == "emergency":
        return "Emergency care is prioritised. Treatment is explained to family step-by-step."

    if intent == "fees":
        return "Costs vary based on care required. Consultation helps us guide you accurately."

    return "Our team will guide you clearly during consultation."


# ------------------------------
# MAIN BRAIN FUNCTION
# ------------------------------
def get_brain_answer(user_message: str) -> str:
    intent = detect_intent(user_message)
    doctor = doctor_route(intent)
    revenue = revenue_message(intent)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.35
    )

    hospital_reply = response.choices[0].message.content.strip()

    return hospital_reply


def log_revenue(phone: str, doctor: str, intent: str, amount: int):
    conn = sqlite3.connect("femme.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO revenue (phone, doctor, intent, amount, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (phone, doctor, intent, amount, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def cancel_appointment(phone, doctor, date):
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        DELETE FROM appointments
        WHERE phone = ? AND doctor = ? AND date = ?
    """, (phone, doctor, date))

    conn.commit()
    conn.close()

    return "🗑️ Appointment cancelled."


