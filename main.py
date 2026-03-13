from doctors import handle_message, is_booking_active
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
from datetime import datetime
from fastapi.responses import StreamingResponse
from bookings import book_appointment, cancel_appointment
import csv
import io

from appointments import (
    get_pending,
    confirm_appointment,
    reject_appointment
)
from crm_brain import decide_followup
from brain import get_brain_answer
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Femme Med AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "femme.db"

# ================= DB INIT =================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        doctor TEXT,
        date TEXT,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_message TEXT,
        ai_reply TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= MODELS =================
class ChatIn(BaseModel):
    user_id: str
    message: str

class AppointmentIn(BaseModel):
    name: str
    phone: str
    doctor: str
    date: str

# ================= UI FILES =================
@app.get("/")
def serve_ui():
    return FileResponse("ui.html")

@app.get("/style.css")
def serve_css():
    return FileResponse("style.css", media_type="text/css")

@app.get("/app.js")
def serve_js():
    return FileResponse("app.js", media_type="application/javascript")

@app.get("/admin")
def serve_admin():
    return FileResponse("admin.html")

@app.get("/admin.js")
def serve_admin_js():
    return FileResponse("admin.js", media_type="application/javascript")

# ================= CHAT API =================
@app.post("/chat")
def chat(data: ChatIn):
    msg = data.message.lower().strip()

    # ===== FEES QUICK REPLY =====
    if (
        "fee" in msg
        or "fees" in msg
        or "consultation fee" in msg
        or "price" in msg
        or "charges" in msg
    ):
        return {
            "reply": """Our consultation fees are:

* General consultation: ₹500
* Gynecology consultation: ₹700
* Emergency consultation: ₹1000

Delivery, C-section, IVF, NICU, and test charges vary depending on the treatment.

Would you like me to book an appointment?"""
        }

    booking_keywords = ["appointment", "book", "booking"]

    if is_booking_active(data.user_id) or any(k in msg for k in booking_keywords):
        reply = handle_message(data.user_id, data.message)
    else:
        reply = get_brain_answer(data.message)

    return {"reply": reply}

@app.get("/admin/revenue/doctor-wise")
def doctor_wise_revenue():
    conn = sqlite3.connect("femme.db")
    c = conn.cursor()
    c.execute("""
        SELECT doctor, SUM(amount) as total
        FROM revenue
        GROUP BY doctor
        ORDER BY total DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [{"doctor": r[0], "revenue": r[1]} for r in rows]


# ================= APPOINTMENT API =================
@app.post("/book-appointment")
def book_appointment(data: AppointmentIn):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("""
            INSERT INTO appointments (name, phone, doctor, date, created_at)
            VALUES (?, ?, ?, ?,'pending', ?)
        """, (
            data.name,
            data.phone,
            data.doctor,
            data.date,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

        return {
            "success": True
        }

    except Exception as e:
        print("BOOKING ERROR:", e)
        return {
            "success": False
        }


# ================================
# ADMIN APPOINTMENT PANEL ROUTES
# ================================

@app.get("/admin/pending-appointments")
def pending_appointments():
    return get_pending()


@app.post("/admin/confirm-appointment/{appt_id}")
def confirm(appt_id: int):
    return confirm_appointment(appt_id)


@app.post("/admin/reject-appointment/{appt_id}")
def reject(appt_id: int):
    return reject_appointment(appt_id)


@app.get("/admin/leads")
def get_leads():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT phone, intent, last_message, created_at
        FROM crm_followups
        ORDER BY created_at DESC
        LIMIT 100
    """)

    rows = c.fetchall()
    conn.close()

    leads = []
    for r in rows:
        leads.append({
            "phone": r[0],
            "intent": r[1],
            "last_message": r[2],
            "created_at": r[3]
        })

    return {"leads": leads}



@app.get("/admin/analytics")
def analytics():
    conn = sqlite3.connect("femme.db")
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM crm_followups")
    leads = c.fetchone()[0]

    c.execute("SELECT SUM(amount) FROM revenue")
    revenue = c.fetchone()[0] or 0

    c.execute("""
        SELECT intent, COUNT(*) 
        FROM crm_followups 
        GROUP BY intent
    """)
    intents = c.fetchall()

    conn.close()
    return {
        "total_leads": leads,
        "total_revenue": revenue,
        "intent_breakdown": intents
    }


# ================= CHAT LOGS API =================

@app.get("/admin/chat-logs")
def get_chat_logs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT user_message, ai_reply, created_at
        FROM chats
        ORDER BY created_at DESC
        LIMIT 200
    """)

    rows = c.fetchall()
    conn.close()

    logs = []
    for r in rows:
        logs.append({
            "user_message": r[0],
            "ai_reply": r[1],
            "created_at": r[2]
        })

    return logs

# ================= CHAT LOGS CSV DOWNLOAD =================

@app.get("/admin/chat-logs/download")
def download_chat_logs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT user_message, ai_reply, created_at
        FROM chats
        ORDER BY created_at DESC
    """)

    rows = c.fetchall()
    conn.close()

    import csv
    from fastapi.responses import Response
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["User Message", "AI Reply", "Created At"])
    writer.writerows(rows)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=chat_logs.csv"
        }
    )

# ================== DOWNLOAD APPOINTMENTS EXCEL ==================

@app.get("/download/appointments")
def download_appointments():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT name, phone, doctor, date, created_at FROM appointments")
    rows = c.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Name", "Phone", "Doctor", "Date", "Created At"])

    for row in rows:
        writer.writerow(row)

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=appointments.csv"}
    )

# ================= HEALTH =================
@app.get("/health")
def health():
    return {"ok": True}
