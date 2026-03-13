console.log("ADMIN JS LOADED SUCCESSFULLY ✅");

// ===============================
// API ROUTES
// ===============================
const API = {
  analytics: "/admin/analytics",
  leads: "/admin/leads",
  chatLogs: "/admin/chat-logs",
  doctorRevenue: "/admin/revenue/doctor-wise",
  monthlyRevenue: "/admin/revenue/monthly",
  pendingAppointments: "/admin/pending-appointments",
  confirm: (id) => /admin/confirm/${id},
  reject: (id) => /admin/reject/${id},
};

// ===============================
// UTIL
// ===============================
const el = (id) => document.getElementById(id);

async function fetchJSON(url, options = {}) {
  const res = await fetch(url, options);

  console.log("FETCH:", url, "STATUS:", res.status);

  if (!res.ok) {
    throw new Error("API FAILED: " + url);
  }

  return res.json();
}

// ===============================
// INIT
// ===============================
document.addEventListener("DOMContentLoaded", () => {
  loadAnalytics();
  loadMonthlyRevenue();
  loadDoctorRevenue();
  loadLeads();
  loadChatLogs();
  loadPendingAppointments();   // 🔥 IMPORTANT
});


// ===============================
// PENDING APPOINTMENTS
// ===============================
async function loadPendingAppointments() {
  const box = el("pendingAppointments");
  if (!box) return;

  box.innerHTML = "Loading appointments...";

  try {
    const data = await fetchJSON(API.pendingAppointments);

    if (!data.length) {
      box.innerHTML = "<p>No pending appointments.</p>";
      return;
    }

    box.innerHTML = "";

    data.forEach(a => {
      box.innerHTML += `
        <div style="padding:15px;border:1px solid #ddd;margin-bottom:12px;border-radius:12px;">
          <b>${a.name}</b><br>
          📞 ${a.phone}<br>
          🧑‍⚕️ ${a.doctor}<br>
          📅 ${a.date}<br><br>

          <button onclick="confirmAppt(${a.id})">✅ Confirm</button>
          <button onclick="rejectAppt(${a.id})">❌ Reject</button>
        </div>
      `;
    });

  } catch (err) {
    console.error("Pending appointments error:", err);
    box.innerHTML = "Error loading appointments";
  }
}

window.confirmAppt = async function(id) {
  try {
    await fetchJSON(API.confirm(id), { method: "POST" });
    loadPendingAppointments();
  } catch (e) {
    alert("Confirm failed");
  }
};

window.rejectAppt = async function(id) {
  try {
    await fetchJSON(API.reject(id), { method: "POST" });
    loadPendingAppointments();
  } catch (e) {
    alert("Reject failed");
  }
};


// ===============================
// CHAT LOGS
// ===============================
async function loadChatLogs() {
  const box = el("chatLogs");
  if (!box) return;

  try {
    const data = await fetchJSON(API.chatLogs);
    box.innerHTML = "";

    data.slice(0, 10).forEach(c => {
      box.innerHTML += `
        <div style="border:1px solid #eee;padding:10px;margin-bottom:10px;border-radius:10px;">
          <p><strong>User:</strong> ${c.user_message}</p>
          <p><strong>AI:</strong> ${c.ai_reply}</p>
          <small>${new Date(c.created_at).toLocaleString()}</small>
        </div>
      `;
    });

  } catch (e) {
    console.error("Chat logs error:", e);
  }
}


// ===============================
// LEADS
// ===============================
async function loadLeads() {
  const tbody = el("leadsTable");
  if (!tbody) return;

  try {
    const data = await fetchJSON(API.leads);
    tbody.innerHTML = "";

    data.forEach(l => {
      tbody.innerHTML += `
        <tr>
          <td>${l.phone}</td>
          <td>${l.intent}</td>
          <td>${l.last_message || "-"}</td>
          <td>${new Date(l.created_at).toLocaleString()}</td>
        </tr>
      `;
    });

  } catch (e) {
    console.error("Leads error:", e);
  }
}


// ===============================
// ANALYTICS
// ===============================
async function loadAnalytics() {
  try {
    const data = await fetchJSON(API.analytics);

    if (el("totalLeads"))
      el("totalLeads").innerText = data.total_leads;

    if (el("totalRevenue"))
      el("totalRevenue").innerText = "₹" + data.total_revenue;

  } catch (e) {
    console.error("Analytics error", e);
  }
}


// ===============================
// MONTHLY REVENUE
// ===============================
async function loadMonthlyRevenue() {
  if (!el("monthlyRevenueChart")) return;

  try {
    const data = await fetchJSON(API.monthlyRevenue);

    new Chart(el("monthlyRevenueChart"), {
      type: "line",
      data: {
        labels: data.map(d => d.month),
        datasets: [{
          label: "Revenue",
          data: data.map(d => d.revenue),
        }]
      }
    });

  } catch (e) {
    console.error("Monthly revenue error", e);
  }
}


// ===============================
// DOCTOR REVENUE
// ===============================
async function loadDoctorRevenue() {
  const tbody = el("doctorRevenueTable");
  if (!tbody) return;

  try {
    const data = await fetchJSON(API.doctorRevenue);
    tbody.innerHTML = "";

    data.slice(0, 5).forEach((d, i) => {
      tbody.innerHTML += `
        <tr>
          <td>${i + 1}</td>
          <td>${d.doctor}</td>
          <td>${d.revenue}</td>
        </tr>
      `;
    });

  } catch (e) {
    console.error("Doctor revenue error", e);
  }
}
