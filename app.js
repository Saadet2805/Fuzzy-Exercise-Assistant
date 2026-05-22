/**
 * Fuzzy Exercise Assistant — frontend
 */

const API_BASE =
  window.location.protocol === "file:"
    ? "http://127.0.0.1:5000"
    : window.location.origin;
const API_RECOMMEND = `${API_BASE}/api/recommend`;

const BMI_CALC_URL = "https://www.calculator.net/bmi-calculator.html";

const REC_META = {
  Rec_Light_Cardio: {
    title: "Light cardio",
    examples: "For example: walking, swimming, light aerobics",
    color: "#3dd6c3",
    detail: "Steady, low-impact activity — often suitable when you want gentler training.",
  },
  Rec_Strength: {
    title: "Strength training",
    examples: "For example: push-ups, pull-ups, weightlifting",
    color: "#f5a623",
    detail: "Resistance work to build muscle and strength.",
  },
  Rec_HIIT: {
    title: "HIIT",
    examples: "High-Intensity Interval Training — e.g. sprint intervals, burpees, jump rope",
    color: "#ff6b7a",
    detail: "Short periods of very hard effort, then rest, repeated. Best if you are already fairly fit.",
  },
  Rec_Beginner: {
    title: "Beginner program",
    examples: "Beginner-level pilates, yoga, and similar guided sessions",
    color: "#6eb5ff",
    detail: "Structured basics if you are new or returning after a break.",
  },
};

const welcomeScreen = document.getElementById("welcome-screen");
const resultsScreen = document.getElementById("results-screen");
const modal = document.getElementById("input-modal");
const form = document.getElementById("profile-form");
const btnStart = document.getElementById("btn-start");
const btnBack = document.getElementById("btn-back");
const submitBtn = form.querySelector('button[type="submit"]');
const formError = document.getElementById("form-error");
const saveNotice = document.getElementById("save-notice");
const bmiInput = document.getElementById("bmi-value");
const bmiCategory = document.getElementById("bmi-category");

function pct(score) {
  return Math.round(Math.min(1, Math.max(0, score)) * 100);
}

function bmiCategoryLabel(bmi) {
  const v = Number(bmi);
  if (Number.isNaN(v)) return "";
  if (v < 18.5) return "Category: underweight (BMI below 18.5)";
  if (v < 25) return "Category: normal weight (BMI 18.5–24.9)";
  if (v < 30) return "Category: overweight (BMI 25–29.9)";
  return "Category: obese (BMI 30 or above)";
}

function updateBmiHint() {
  const v = bmiInput.value.trim();
  bmiCategory.textContent = v ? bmiCategoryLabel(v) : "";
}

bmiInput.addEventListener("input", updateBmiHint);

function bindSlider(inputId, outputId) {
  const input = document.getElementById(inputId);
  const output = document.getElementById(outputId);
  const sync = () => {
    output.textContent = input.value;
  };
  input.addEventListener("input", sync);
  sync();
}

["fitness", "muscle", "weightloss"].forEach((name) => {
  bindSlider(name, `${name}-val`);
});

function showScreen(screen) {
  const isWelcome = screen === "welcome";
  const isResults = screen === "results";
  welcomeScreen.classList.toggle("screen--active", isWelcome);
  resultsScreen.classList.toggle("screen--active", isResults);
  if (isResults) {
    requestAnimationFrame(() => window.scrollTo({ top: 0, behavior: "smooth" }));
  }
}

function openModal(clearForm = false) {
  modal.hidden = false;
  document.body.style.overflow = "hidden";
  hideFormError();
  if (clearForm) {
    document.getElementById("user-name").value = "";
    bmiInput.value = "";
    bmiCategory.textContent = "";
    ["fitness", "muscle", "weightloss"].forEach((id) => {
      const el = document.getElementById(id);
      el.value = "5";
      document.getElementById(`${id}-val`).textContent = "5";
    });
  }
  document.getElementById("user-name").focus();
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
  submitBtn.textContent = loading ? "Calculating…" : "Get my recommendation";
  resultsScreen.classList.toggle("results-screen--loading", loading);
}

function showSaveNotice(name, total) {
  saveNotice.hidden = false;
  saveNotice.textContent = `Saved for ${name}. Total entries in results.csv: ${total}.`;
}

btnStart.addEventListener("click", () => openModal(true));
btnBack.addEventListener("click", () => {
  saveNotice.hidden = true;
  showScreen("welcome");
});

modal.querySelectorAll("[data-close-modal]").forEach((el) => {
  el.addEventListener("click", closeModal);
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !modal.hidden) closeModal();
});

function enrichRecommendations(apiRecs) {
  return apiRecs
    .map((r) => ({
      key: r.key,
      score: r.score,
      percent: pct(r.score),
      ...(REC_META[r.key] || {
        title: r.key,
        examples: "",
        color: "#3dd6c3",
        detail: "",
      }),
    }))
    .sort((a, b) => b.score - a.score);
}

const REQUIRED_SERVER_VERSION = "2.3";

async function checkServerVersion() {
  const res = await fetch(`${API_BASE}/api/health`, { cache: "no-store" });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error("Cannot reach the server. Run RESTART.bat first.");
  }
  if (data.engine_version !== REQUIRED_SERVER_VERSION) {
    throw new Error(
      "Server is outdated (still using old BMI rules). Close all terminal windows, " +
        "then double-click RESTART.bat and refresh the page (Ctrl+F5)."
    );
  }
  return data;
}

async function fetchRecommendations(payload) {
  const res = await fetch(API_RECOMMEND, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    cache: "no-store",
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || `Server error (${res.status})`);
  }
  return data;
}

function renderResults(data, ranked) {
  const top = ranked[0];
  const displayName = data.name && data.name !== "Anonymous" ? data.name : "Participant";

  document.getElementById("result-user-name").textContent = displayName;
  document.getElementById("best-match-title").textContent = top.title;
  document.getElementById("best-match-examples").textContent = top.examples;
  document.getElementById("best-match-text").textContent = top.detail;
  document.getElementById("best-match-pct").textContent =
    `${top.percent}% match with your profile`;

  const list = document.getElementById("compare-list");
  list.innerHTML = "";

  ranked.forEach((item, index) => {
    const row = document.createElement("article");
    row.className = `compare-card${index === 0 ? " compare-card--top" : ""}`;
    row.innerHTML = `
      <div class="compare-card-head">
        <div>
          <span class="compare-rank">${index === 0 ? "★ Best" : `#${index + 1}`}</span>
          <h3 class="compare-name">${item.title}</h3>
          <p class="compare-examples">${item.examples}</p>
        </div>
        <span class="compare-pct" style="color:${item.color}">${item.percent}%</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width:0%;background:${item.color}"></div>
      </div>
    `;
    list.appendChild(row);
    requestAnimationFrame(() => {
      row.querySelector(".bar-fill").style.width = `${item.percent}%`;
    });
  });

  const bmiDisplay = data.inputs?.bmi ?? data.bmi_value ?? "—";
  document.getElementById("inputs-summary").innerHTML = `
    <h2 class="inputs-summary-label">Answers for <strong>${displayName}</strong></h2>
    <div class="input-chips">
      <span class="input-chip">BMI: <strong>${bmiDisplay}</strong></span>
      <span class="input-chip">Fitness: <strong>${data.inputs.fitness}/10</strong></span>
      <span class="input-chip">Muscle goal: <strong>${data.inputs.muscle}/10</strong></span>
      <span class="input-chip">Weight loss goal: <strong>${data.inputs.weightloss}/10</strong></span>
    </div>
  `;

  if (data.total_saved != null) {
    showSaveNotice(displayName, data.total_saved);
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  hideFormError();
  setLoading(true);

  const name = document.getElementById("user-name").value.trim();
  const bmi = parseFloat(bmiInput.value);

  if (!name) {
    showFormError("Please enter your first name.");
    setLoading(false);
    return;
  }
  if (Number.isNaN(bmi) || bmi < 10 || bmi > 60) {
    showFormError(
      `Please calculate your BMI (${BMI_CALC_URL}) and enter a value between 10 and 60.`
    );
    setLoading(false);
    return;
  }

  const payload = {
    name,
    bmi,
    fitness: Number(document.getElementById("fitness").value),
    muscle: Number(document.getElementById("muscle").value),
    weightloss: Number(document.getElementById("weightloss").value),
  };

  try {
    await checkServerVersion();
    const data = await fetchRecommendations(payload);
    const ranked = enrichRecommendations(data.recommendations);
    closeModal();
    showScreen("results");
    renderResults(data, ranked);
  } catch (err) {
    const hint =
      window.location.protocol === "file:"
        ? " Run START.bat and open http://127.0.0.1:5000"
        : " Run START.bat and keep the server window open.";
    showFormError(err.message || "Could not connect to the server." + hint);
  } finally {
    setLoading(false);
  }
});

showScreen("welcome");
