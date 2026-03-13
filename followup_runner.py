import sqlite3
from datetime import datetime
from sms_service import send_sms

DB_PATH = "femme.db"


def run_followups():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT id, phone, name, intent, followup_stage
        FROM crm_followups
        WHERE status='active'
        AND next_followup_at <= ?
    """, (datetime.now().isoformat(),))

    leads = c.fetchall()

    if not leads:
        print("❌ No follow-ups due")
        return

    print(f"✅ Due leads: {len(leads)}")

    for lead in leads:
        lead_id, phone, name, intent, stage = lead

        message = generate_sms(intent, stage)

        print(f"📤 Sending SMS to {phone}")
        send_sms(phone, message)

        update_stage(c, lead_id, stage)

    conn.commit()
    conn.close()


def generate_sms(intent, stage):
    if intent == "maternity":
        return "Femme Med Hospital: Our doctor can guide you regarding maternity care. Timely consultation ensures safety."

    return "Femme Med Hospital: We are available to guide you for medical consultation."


def update_stage(cursor, lead_id, stage):
    if stage >= 2:
        cursor.execute("""
            UPDATE crm_followups SET status='closed'
            WHERE id=?
        """, (lead_id,))
    else:
        cursor.execute("""
            UPDATE crm_followups
            SET followup_stage=?, next_followup_at=datetime('now','+1 day')
            WHERE id=?
        """, (stage + 1, lead_id))


if __name__ == "__main__":
    print("🚀 SMS Follow-up Engine Started")
    run_followups()
