import sqlite3

def book_appointment(name, phone, doctor, date):
    conn = sqlite3.connect("femme.db")
    c = conn.cursor()

    # duplicate check
    c.execute("""
        SELECT id FROM appointments
        WHERE phone=? AND doctor=? AND date=?
    """, (phone, doctor, date))

    if c.fetchone():
        conn.close()
        return "❌ Appointment already booked."

    c.execute("""
        INSERT INTO appointments (name, phone, doctor, date)
        VALUES (?, ?, ?, ?)
    """, (name, phone, doctor, date))

    conn.commit()
    conn.close()
    return "✅ Appointment booked successfully."


def cancel_appointment(phone, doctor, date):
    conn = sqlite3.connect("femme.db")
    c = conn.cursor()

    c.execute("""
        DELETE FROM appointments
        WHERE phone=? AND doctor=? AND date=?
    """, (phone, doctor, date))

    if c.rowcount == 0:
        conn.close()
        return "❌ No appointment found to cancel."

    conn.commit()
    conn.close()
    return "✅ Appointment cancelled."
