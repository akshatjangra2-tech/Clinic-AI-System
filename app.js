// ===============================
// FEMME AI - CLEAN APP.JS
// ===============================

// ✅ ONLY ONE SHEET URL
const SHEET_URL = "https://script.google.com/macros/s/AKfycbzQJkMpwfMzQu1Kv6Hj2WraLX1VsIFTudf63E_1KMjjkhnUEOZjOKc14TWc2286-qftWQ/exec";

// ✅ user id for chat session
const user_id =
  localStorage.getItem("user_id") ||
  (crypto.randomUUID ? crypto.randomUUID() : "u_" + Date.now());

localStorage.setItem("user_id", user_id);

// ===============================
// FORM BOOKING
// ===============================
async function bookAppointment() {
  const btn = document.getElementById("bookBtn");

  const name = (document.getElementById("patientName")?.value || "").trim();
  const phone = (document.getElementById("phone")?.value || "").trim();
  const doctor = (document.getElementById("doctor")?.value || "").trim();
  const doctorMap = {
  "aditya": "DR ADITYA VERMA (HIGH RISK PREGNANCY)",
  "ankur": "DR ANKUR MEHTA (EMERGENCY CARE)",
  "nidhi": "DR NIDHI SINGH (GYNECOLOGY)"
};

const finalDoctor = doctorMap[doctor.toLowerCase()] || doctor.toUpperCase();
  const date = (document.getElementById("date")?.value || "").trim();

  if (!name || !phone || !doctor || !date) {
    alert("Fill Name, Phone, Doctor, Date ✅");
    return;
  }

  if (btn) {
    btn.disabled = true;
    btn.innerText = "BOOKING...";
  }

  const payload = {
    name,
    phone,
    problem: "",
    date,
    time: "",
    doctor: finalDoctor,
    payment_status: "Pending",
    amount: "",
    payment_mode: ""
  };

  try {
    const ok = await bookToSheet(payload);

    if (ok) {
      if (btn) btn.innerText = "APPOINTMENT BOOKED ✅";
    } else {
      if (btn) btn.innerText = "CONFIRM APPOINTMENT";
      alert("❌ Booking failed");
    }
  } catch (e) {
    console.error("BOOKING ERROR:", e);
    if (btn) btn.innerText = "CONFIRM APPOINTMENT";
    alert("❌ Booking failed");
  }

  setTimeout(() => {
    if (btn) {
      btn.disabled = false;
      btn.innerText = "CONFIRM APPOINTMENT";
    }
  }, 1500);
}

window.bookAppointment = bookAppointment;

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("bookBtn")?.addEventListener("click", bookAppointment);
});

// ===============================
// COMMON SHEET POST
// ===============================
async function bookToSheet(payload) {
  const res = await fetch(SHEET_URL, {
    method: "POST",
    headers: { "Content-Type": "text/plain;charset=utf-8" },
    body: JSON.stringify(payload)
  });
  return res.ok;
}

// ===============================
// CHAT HELPERS
// ===============================
function addMsg(role, text) {
  const chatBox = document.getElementById("chat-messages");
  if (!chatBox) return;

  const cls = role === "user" ? "user-message" : "bot-message";
  const label = role === "user" ? "You" : "AI";

  chatBox.innerHTML += `
    <div class="${cls}">
      <strong>${label}:</strong> ${text}
    </div>
  `;
  chatBox.scrollTop = chatBox.scrollHeight;
}

function getSession() {
  return JSON.parse(localStorage.getItem("bot_session") || '{"step":"start"}');
}

function setSession(s) {
  localStorage.setItem("bot_session", JSON.stringify(s));
}

function resetSession() {
  setSession({ step: "start" });
}

function validPhone(x) {
  return (x || "").replace(/\D/g, "").length === 10;
}

function validDate(x) {
  return /^(\d{2})-(\d{2})-(\d{4})$/.test((x || "").trim());
}

function validTime(x) {
  return /^([01]\d|2[0-3]):([0-5]\d)$/.test((x || "").trim());
}

// ===============================
// SIMPLE CHAT BOOKING FLOW
// ===============================
async function sendMessage() {
  const input = document.getElementById("userInput");
  const message = (input?.value || "").trim();
  if (!message) return;

  input.value = "";
  addMsg("user", message);

  let s = getSession();
  const lower = message.toLowerCase();

  // cancel flow
  if (["cancel", "stop", "exit"].includes(lower)) {
    resetSession();
    addMsg("bot", "✅ Booking cancel kar di.");
    return;
  }

  // start booking
  if (
    s.step === "start" &&
    (lower.includes("appointment") || lower.includes("book") || lower.includes("booking"))
  ) {
    s = { step: "name" };
    setSession(s);
    addMsg("bot", "✅ Appointment booking start. 👤 Patient name?");
    return;
  }

  // booking flow active
  if (s.step !== "start") {
    if (s.step === "name") {
      s.name = message;
      s.step = "phone";
      setSession(s);
      addMsg("bot", "📞 Phone number? (10 digit)");
      return;
    }

    if (s.step === "phone") {
      if (!validPhone(message)) {
        addMsg("bot", "❌ Phone galat. 10 digit number bhejo.");
        return;
      }
      s.phone = message.replace(/\D/g, "");
      s.step = "problem";
      setSession(s);
      addMsg("bot", "🩺 Problem / symptoms?");
      return;
    }

    if (s.step === "problem") {
      s.problem = message;
      s.step = "doctor";
      setSession(s);
      addMsg("bot", "👨‍⚕️ Doctor choose karo: Nidhi / Aditya / Ankur");
      return;
    }

    if (s.step === "doctor") {
      s.doctor = message;
      s.step = "date";
      setSession(s);
      addMsg("bot", "📅 Date bhejo (DD-MM-YYYY)");
      return;
    }

    if (s.step === "date") {
      if (!validDate(message)) {
        addMsg("bot", "❌ Date format galat. Example: 25-03-2026");
        return;
      }
      s.date = message;
      s.step = "time";
      setSession(s);
      addMsg("bot", "⏰ Time bhejo (HH:MM) Example: 14:30");
      return;
    }

    if (s.step === "time") {
      if (!validTime(message)) {
        addMsg("bot", "❌ Time format galat. Example: 14:30");
        return;
      }
      s.time = message;
      s.step = "confirm";
      setSession(s);

      addMsg(
        "bot",
        `✅ Confirm karo:<br>
        <b>Name:</b> ${s.name}<br>
        <b>Phone:</b> ${s.phone}<br>
        <b>Problem:</b> ${s.problem}<br>
        <b>Doctor:</b> ${s.doctor}<br>
        <b>Date:</b> ${s.date}<br>
        <b>Time:</b> ${s.time}<br><br>
        Type <b>YES</b> to book`
      );
      return;
    }

    if (s.step === "confirm") {
      if (lower !== "yes" && lower !== "y") {
        addMsg("bot", "❌ Booking nahi ki. Agar karni ho to YES type karo.");
        return;
      }

      const payload = {
        name: s.name || "",
        phone: s.phone || "",
        problem: s.problem || "",
        doctor: s.doctor || "",
        date: s.date || "",
        time: s.time || "",
        payment_status: "Pending",
        amount: "",
        payment_mode: ""
      };

      addMsg("bot", "⏳ Booking ho rahi hai...");

      try {
        const ok = await bookToSheet(payload);
        if (ok) {
          addMsg("bot", "🎉 ✅ Appointment booked successfully!");
        } else {
          addMsg("bot", "❌ Booking failed. Sheet URL / permission check karo.");
        }
      } catch (e) {
        console.error("CHAT BOOKING ERROR:", e);
        addMsg("bot", "❌ Booking error.");
      }

      resetSession();
      return;
    }
  }

// ===============================
// NORMAL RAG CHAT
// ===============================
try {

  const res = await fetch("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      user_id: user_id,
      message: message
    })
  });

  const data = await res.json();

  addMsg("bot", data.reply || "No reply");

} catch (e) {

  console.error("CHAT ERROR:", e);
  addMsg("bot", "❌ Server error");

}

}


// ====================================
// CHAT EVENTS
// ====================================

document.getElementById("sendBtn")?.addEventListener("click", sendMessage);

document.getElementById("userInput")?.addEventListener("keydown", function (e) {

  if (e.key === "Enter") {

    e.preventDefault();
    sendMessage();

  }

});
