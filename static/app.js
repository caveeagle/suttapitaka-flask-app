async function postJSON(url, payload) {
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    const msg = (data && data.error) ? data.error : `HTTP ${resp.status}`;
    throw new Error(msg);
  }
  return data;
}

function setDisabled(disabled) {
  document.getElementById("run-btn").disabled = disabled;
  document.getElementById("question").disabled = disabled;
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("qa-form");
  const question = document.getElementById("question");
  const output = document.getElementById("output");
  const clearBtn = document.getElementById("clear-btn");

    function clearAll() {
      question.value = "";
      output.value = "";
      setTimeout(() => question.focus(), 0);
    }
    
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        e.preventDefault();
        e.stopPropagation();
        clearAll();
      }
    });

  clearBtn.addEventListener("click", () => clearAll());

  // Enter в input отправляет форму по умолчанию (submit).
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const text = question.value.trim();
    if (!text) {
      output.value = "";
      return;
    }

    output.value = "Please wait: the request is taking a long time (up to a minute).\nProcessing..............";
    setDisabled(true);

    try {
      const data = await postJSON("api/answer", { text });
      
      output.value = data.result ?? "";
    } catch (err) {
      output.value = `Error: ${err.message}`;
    } finally {
      setDisabled(false);
      question.focus();
    }
  });

  question.focus();
});
