import sqlite3

DB_FILE = "femme.db"


def get_pending():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, phone, doctor, date FROM appointments WHERE status='pending'")
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "name": r[1],
            "phone": r[2],
            "doctor": r[3],
            "date": r[4]
        }
        for r in rows
    ]


def confirm_appointment(app_id: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("UPDATE appointments SET status='confirmed' WHERE id=?", (app_id,))
    conn.commit()
    conn.close()


def reject_appointment(app_id: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("UPDATE appointments SET status='rejected' WHERE id=?", (app_id,))
    conn.commit()
    conn.close()
