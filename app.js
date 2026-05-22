/**
 * Frontend — sends slider values to Python FCM backend (POST /api/recommend).
 */

const API_BASE =
  window.location.protocol === "file:"
    ? "http://127.0.0.1:5000"
    : window.location.origin;
const API_RECOMMEND = `${API_BASE}/api/recommend`;

const REC_META = {
  Rec_Light_Cardio: {
    title: "Light Cardio",
    color: "#3dd6c3",
    detail: "Light cardio · 20–30 min · low intensity",
  },
  Rec_Strength: {
    title: "Strength",
    color: "#f5a623",
    detail: "Strength · 3×8–12 reps · moderate load",
  },
  Rec_HIIT: {
    title: "HIIT",
    color: "#ff6b7a",
    detail: "HIIT · 15–20 min · high intensity",
  },
  Rec_Beginner: {
    title: "Beginner",
    color: "#6eb5ff",
    detail: "Beginner · 25–35 min · guided basics",
  },
};

const INPUT_LABELS = {
  bmi: "BMI",
  fitness: "Fitness Level",
  muscle: "Muscle Gain Goal",
  weightloss: "Weight Loss Goal",
};

// --- DOM ---
const welcomeScreen = document.getElementById("welcome-screen");
const resultsScreen = document.getElementById("results-screen");
const modal = document.getElementById("input-modal");
const form = document.getElementById("profile-form");
const btnStart = document.getElementById("btn-start");
const btnBack = document.getElementById("btn-back");
const submitBtn = form.querySelector('button[type="submit"]');
const formError = document.getElementById("form-error");

function bindSlider(inputId, outputId) {
  const input = document.getElementById(inputId);
  const output = document.getElementById(outputId);
  const sync = () => {
    output.textContent = input.value;
  };
  input.addEventListener("input", sync);
  sync();
}

["bmi", "fitness", "muscle", "weightloss"].forEach((name) => {
  bindSlider(name, `${name}-val`);
});

function openModal() {
  modal.hidden = false;
  document.body.style.overflow = "hidden";
  hideFormError();
  document.getElementById("bmi").focus();
}

function closeModal() {
  modal.hidden = true;
  document.body.style.overflow = "";
}

function showFormError(message) {
  formError.hidden = false;
  formError.textContent = message;
}

function hideFormError() {
  formError.hidden = true;
  formError.textContent = "";
}

function setLoading(loading) {
  submitBtn.disabled = loading;
  submitBtn.textContent = loading ? "Running FCM…" : "Run FCM & show results";
}

btnStart.addEventListener("click", openModal);

modal.querySelectorAll("[data-close-modal]").forEach((el) => {
  el.addEventListener("click", closeModal);
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !modal.hidden) closeModal();
});

function showScreen(screen) {
  welcomeScreen.classList.toggle("screen--active", screen === "welcome");
  welcomeScreen.hidden = screen !== "welcome";
  resultsScreen.classList.toggle("screen--active", screen === "results");
  resultsScreen.hidden = screen !== "results";
}

function enrichRecommendations(apiRecs) {
  return apiRecs
    .map((r) => ({
      key: r.key,
      score: r.score,
      ...(REC_META[r.key] || { title: r.key, color: "#3dd6c3", detail: "" }),
    }))
    .sort((a, b) => b.score - a.score);
}

async function fetchRecommendations(payload) {
  const res = await fetch(API_RECOMMEND, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.error || `Server error (${res.status})`);
  }

  return data;
}

function renderInputsSummary(inputs) {
  const el = document.getElementById("inputs-summary");
  const chips = Object.entries(INPUT_LABELS)
    .map(([name, label]) => {
      const val = inputs[name];
      return `<span class="input-chip"><strong>${label}</strong> ${val}/10</span>`;
    })
    .join("");
  el.innerHTML = `<p class="inputs-summary-label">Your inputs</p><div class="input-chips">${chips}</div>`;
}

function renderBarChart(ranked) {
  const chart = document.getElementById("bar-chart");
  chart.innerHTML = "";

  ranked.forEach((item) => {
    const pct = Math.min(100, Math.max(0, item.score * 100));
    const row = document.createElement("div");
    row.className = "bar-row";
    row.innerHTML = `
      <div class="bar-row-header">
        <span class="bar-row-label">${item.title}</span>
        <span class="bar-row-value">${item.score.toFixed(3)}</span>
      </div>
      <div class="bar-track" aria-hidden="true">
        <div
          class="bar-fill"
          style="width: 0%; background: ${item.color};"
          title="${item.title}: ${pct.toFixed(0)}%"
        ></div>
      </div>
    `;
    chart.appendChild(row);

    requestAnimationFrame(() => {
      row.querySelector(".bar-fill").style.width = `${pct}%`;
    });
  });

  const top = ranked[0];
  document.getElementById("top-pick").innerHTML =
    `<strong>Best match:</strong> ${top.title} — ${top.detail}`;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  hideFormError();
  setLoading(true);

  const payload = {
    bmi: Number(form.bmi.value),
    fitness: Number(form.fitness.value),
    muscle: Number(form.muscle.value),
    weightloss: Number(form.weightloss.value),
  };

  try {
    const data = await fetchRecommendations(payload);
    const ranked = enrichRecommendations(data.recommendations);

    closeModal();
    showScreen("results");
    renderInputsSummary(data.inputs);
    renderBarChart(ranked);
  } catch (err) {
    const hint =
      window.location.protocol === "file:"
        ? " Double-click START.bat, then use http://127.0.0.1:5000 — do not open index.html directly."
        : " Double-click START.bat and keep the black window open. Use http://127.0.0.1:5000";
    showFormError(
      (err.message || "Connection failed — backend not running.") + hint
    );
  } finally {
    setLoading(false);
  }
});

btnBack.addEventListener("click", () => {
  showScreen("welcome");
});
