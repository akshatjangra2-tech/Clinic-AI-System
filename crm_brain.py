CRM_SYSTEM_PROMPT = """
You are the internal CRM Brain of Femme Med Hospital.

You are NOT a chatbot.
You are the hospital’s internal operations system.

You behave like a senior hospital operations manager with 30+ years of experience.

=====================================
YOUR CORE RESPONSIBILITIES
=====================================

1. Track every patient interaction
2. Ensure no lead is forgotten
3. Trigger timely follow-ups automatically
4. Reduce missed appointments
5. Improve conversion from enquiry to visit
6. Support doctors without burdening them
7. Give owner visibility and control

=====================================
PATIENT PIPELINE LOGIC
=====================================

Each patient moves through these stages:
- New Enquiry
- Interested
- Appointment Booked
- Visited
- Follow-up Required
- Closed

You always know the current stage and the next action.

=====================================
AUTO FOLLOW-UP RULES
=====================================

If chat happened but no appointment:
- Trigger follow-up within 6–12 hours
- Tone: gentle, supportive, non-pushy

If appointment booked:
- Send reminder before appointment
- Prepare doctor context

If appointment missed:
- Trigger reschedule message

If visit completed:
- Trigger post-visit follow-up after 2–3 days

=====================================
COMMUNICATION RULES
=====================================

- Calm
- Professional
- Hospital-first language
- No sales pressure
- No automation mention

You NEVER say:
- CRM
- automation
- system triggered
- AI

=====================================
GOAL
=====================================

- Increase patient satisfaction
- Increase doctor efficiency
- Increase hospital revenue
- Reduce staff workload

You are Femme Med Hospital’s internal CRM brain.
"""


# crm_brain.py
# Femme Med Hospital – Auto Follow-up CRM Engine

import sqlite3
from datetime import datetime, timedelta

DB_PATH = "femme.db"


def insert_lead(phone: str, name: str, intent: str, message: str):
    """
    Insert new lead and schedule first follow-up automatically
    FIX-2: Prevent duplicate active leads (same phone)
    """

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # ================= FIX 2 =================
    # Do NOT create duplicate active leads
    c.execute("""
        SELECT id FROM crm_followups
        WHERE phone = ? AND status = 'active'
    """, (phone,))
    existing = c.fetchone()

    if existing:
        conn.close()
        return
    # =========================================

    now = datetime.now()
    next_followup = now + timedelta(minutes=30)  # warm follow-up

    c.execute("""
        INSERT INTO crm_followups
        (phone, name, intent, last_message, status, followup_stage, next_followup_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        phone,
        name,
        intent,
        message,
        "active",
        1,
        next_followup.isoformat(),
        now.isoformat()
    ))

    conn.commit()
    conn.close()


def update_followup_stage(lead_id: int, stage: int):
    """
    Move follow-up to next stage with smart delay
    """

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if stage == 1:
        next_time = datetime.now() + timedelta(hours=24)
    elif stage == 2:
        next_time = datetime.now() + timedelta(hours=72)
    else:
        # Premium behaviour: stop after stage 3
        c.execute("""
            UPDATE crm_followups
            SET status = 'closed'
            WHERE id = ?
        """, (lead_id,))
        conn.commit()
        conn.close()
        return

    c.execute("""
        UPDATE crm_followups
        SET followup_stage = ?, next_followup_at = ?
        WHERE id = ?
    """, (stage + 1, next_time.isoformat(), lead_id))

    conn.commit()
    conn.close()


def get_due_followups():
    """
    Fetch all leads whose follow-up time has arrived
    """

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT id, phone, name, intent, followup_stage
        FROM crm_followups
        WHERE status = 'active'
        AND next_followup_at <= ?
    """, (datetime.now().isoformat(),))

    rows = c.fetchall()
    conn.close()
    return rows


def generate_followup_message(intent: str, stage: int) -> str:
    """
    Premium hospital follow-up messages (non-spam, trust-first)
    """

    if intent == "maternity":
        if stage == 1:
            return (
                "We wanted to check if you need guidance regarding maternity care. "
                "Early consultation helps ensure safe care."
            )
        if stage == 2:
            return (
                "For pregnancy-related concerns, timely medical guidance is important. "
                "Our doctor can assist you if you wish to visit."
            )

    if intent == "emergency":
        return (
            "If your concern is still active, please visit the hospital immediately. "
            "Emergency care is available 24×7."
        )

    if stage == 1:
        return (
            "We are available to guide you further if you need medical assistance."
        )

    if stage == 2:
        return (
            "Just a reminder that medical consultation can help you get clear guidance."
        )

    return ""



def decide_followup(intent: str, last_message: str, stage: int = 1) -> str:
    """
    Smart wrapper used by main.py
    """
    return generate_followup_message(intent, stage)
