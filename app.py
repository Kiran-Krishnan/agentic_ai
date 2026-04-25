from agents.planner import plan_task
from agents.retriever import retrieve_context
from agents.security import analyze_security
from agents.responder import generate_final_answer
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import re
import base64
from diagram import render as render_diagram

app = FastAPI()

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>AI Security Agent</title>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;600;800&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:       #0a0c10;
      --surface:  #111318;
      --border:   #1f2430;
      --accent:   #00d4ff;
      --accent2:  #7b61ff;
      --warn:     #ff6b35;
      --text:     #c9d1d9;
      --muted:    #4a5568;
      --success:  #39d353;
    }

    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'JetBrains Mono', monospace;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px 20px 80px;
    }

    header {
      text-align: center;
      margin-bottom: 48px;
    }
    header .badge {
      display: inline-block;
      font-size: 11px;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: var(--accent);
      border: 1px solid var(--accent);
      padding: 4px 12px;
      border-radius: 2px;
      margin-bottom: 16px;
    }
    header h1 {
      font-family: 'Syne', sans-serif;
      font-size: clamp(28px, 5vw, 48px);
      font-weight: 800;
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      line-height: 1.1;
    }
    header p {
      color: var(--muted);
      font-size: 13px;
      margin-top: 10px;
    }

    .card {
      width: 100%;
      max-width: 820px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 28px;
      margin-bottom: 24px;
    }

    .input-label {
      font-size: 11px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 10px;
    }
    textarea {
      width: 100%;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 6px;
      color: var(--text);
      font-family: 'JetBrains Mono', monospace;
      font-size: 14px;
      padding: 14px;
      resize: vertical;
      min-height: 90px;
      outline: none;
      transition: border-color 0.2s;
    }
    textarea:focus { border-color: var(--accent); }
    textarea::placeholder { color: var(--muted); }

    button#runBtn {
      margin-top: 16px;
      width: 100%;
      padding: 14px;
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      border: none;
      border-radius: 6px;
      color: #000;
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 2px;
      text-transform: uppercase;
      cursor: pointer;
      transition: opacity 0.2s, transform 0.1s;
    }
    button#runBtn:hover:not(:disabled) { opacity: 0.9; }
    button#runBtn:active:not(:disabled) { transform: scale(0.99); }
    button#runBtn:disabled { opacity: 0.4; cursor: not-allowed; }

    #status {
      display: none;
      align-items: center;
      gap: 10px;
      margin-top: 18px;
      font-size: 13px;
      color: var(--muted);
    }
    #status.visible { display: flex; }
    .spinner {
      width: 16px; height: 16px;
      border: 2px solid var(--border);
      border-top-color: var(--accent);
      border-radius: 50%;
      animation: spin 0.7s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    #results { display: none; width: 100%; max-width: 820px; }
    #results.visible { display: block; }

    .result-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      margin-bottom: 18px;
      overflow: hidden;
      animation: fadeUp 0.4s ease both;
    }
    .result-card:nth-child(2) { animation-delay: 0.1s; }
    .result-card:nth-child(3) { animation-delay: 0.2s; }
    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(12px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    .result-header {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 14px 20px;
      border-bottom: 1px solid var(--border);
      font-size: 11px;
      letter-spacing: 2px;
      text-transform: uppercase;
      font-weight: 600;
    }
    .result-header .dot {
      width: 8px; height: 8px;
      border-radius: 50%;
    }
    .plan-header   { color: var(--accent); }
    .plan-header .dot   { background: var(--accent); }
    .risk-header   { color: var(--warn); }
    .risk-header .dot   { background: var(--warn); }
    .answer-header { color: var(--success); }
    .answer-header .dot { background: var(--success); }

    .result-body {
      padding: 20px;
      font-size: 13px;
      line-height: 1.8;
      white-space: pre-wrap;
      word-break: break-word;
      color: var(--text);
    }

    #error {
      display: none;
      width: 100%;
      max-width: 820px;
      background: rgba(255,107,53,0.08);
      border: 1px solid var(--warn);
      border-radius: 8px;
      padding: 16px 20px;
      color: var(--warn);
      font-size: 13px;
    }
    #error.visible { display: block; }

    footer {
      margin-top: 48px;
      font-size: 11px;
      color: var(--muted);
      text-align: center;
    }
  </style>
</head>
<body>

<header>
  <div class="badge">Multi-Agent System</div>
  <h1>AI Security Agent</h1>
  <p>Plan · Retrieve · Analyze · Respond</p>
</header>

<div class="card">
  <div class="input-label">Query</div>
  <textarea id="queryInput" placeholder="Ask anything — e.g. What are the key risks of deploying LLMs in banking?"></textarea>
  <button id="runBtn" onclick="runQuery()">▶ Run Agent</button>
  <div id="status">
    <div class="spinner"></div>
    <span id="statusText">Initialising agents...</span>
  </div>
</div>

<div id="error"></div>

<div id="results">
  <div class="result-card">
    <div class="result-header plan-header"><div class="dot"></div>Plan</div>
    <div class="result-body" id="planOut"></div>
  </div>
  <div class="result-card">
    <div class="result-header risk-header"><div class="dot"></div>Security Risks</div>
    <div class="result-body" id="riskOut"></div>
  </div>
  <div class="result-card">
    <div class="result-header answer-header"><div class="dot"></div>Final Answer</div>
    <div class="result-body" id="answerOut"></div>
  </div>
  <div class="result-card">
  <div class="result-header answer-header"><div class="dot"></div>Architecture Diagram</div>
  <div class="result-body">
    <img id="diagramImg" style="max-width:100%; height:auto; display:none; border-radius:8px;" />
  </div>
</div>

<footer>Powered by FastAPI · Running at localhost</footer>

<script>
  const steps = [
    "🧠 Planning task...",
    "🔍 Retrieving context...",
    "🛡️ Analysing security risks...",
    "🤖 Generating final answer..."
  ];

  async function runQuery() {
    const query = document.getElementById("queryInput").value.trim();
    if (!query) return;

    const btn       = document.getElementById("runBtn");
    const status    = document.getElementById("status");
    const statusTxt = document.getElementById("statusText");
    const results   = document.getElementById("results");
    const errBox    = document.getElementById("error");

    btn.disabled = true;
    results.classList.remove("visible");
    errBox.classList.remove("visible");
    status.classList.add("visible");

    let stepIdx = 0;
    statusTxt.textContent = steps[0];
    const ticker = setInterval(() => {
      stepIdx = (stepIdx + 1) % steps.length;
      statusTxt.textContent = steps[stepIdx];
    }, 2500);

    try {
      const res = await fetch(`/run?query=${encodeURIComponent(query)}`, {
        method: "POST"
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();

      document.getElementById("planOut").textContent   = data.plan   ?? "—";
      document.getElementById("riskOut").textContent   = data.risks  ?? "—";
      document.getElementById("answerOut").textContent = data.answer ?? "—";
      
      const diagramImg = document.getElementById("diagramImg");
      if (data.diagram) {
        diagramImg.src = `data:image/png;base64,${data.diagram}`;
        diagramImg.style.display = "block";
      } else {
        diagramImg.style.display = "none";
      }
      
      results.classList.add("visible");
    } catch (err) {
      errBox.textContent = "⚠ " + err.message;
      errBox.classList.add("visible");
    } finally {
      clearInterval(ticker);
      status.classList.remove("visible");
      btn.disabled = false;
    }
  }

  document.getElementById("queryInput").addEventListener("keydown", e => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) runQuery();
  });
</script>
</body>
</html>
"""

def clean_iac_answer(answer: str) -> str:
    if not answer:
        return ""

    text = answer.strip()

    marker = "Here is the generated Terraform code:"
    if marker in text:
        text = text.split(marker, 1)[1].strip()

    # Extract the first fenced code block exactly as-is
    code_block = re.search(
        r"```(?:terraform|hcl)?\s*\n(.*?)\n```",
        text,
        re.DOTALL | re.IGNORECASE
    )
    if code_block:
        return code_block.group(1).strip()

    # Fallback: return whatever remains after the marker
    return text.strip()


def run_agentic_system(query):
    plan = plan_task(query)
    context = retrieve_context(query)
    risks = analyze_security(context)
    answer = generate_final_answer(plan, context, risks)

    iac_code = clean_iac_answer(answer)

    with open("infra.tf", "w", encoding="utf-8") as f:
        f.write(iac_code)

    diagram_path = render_diagram("infra.tf")

    with open(diagram_path, "rb") as img_file:
        diagram_b64 = base64.b64encode(img_file.read()).decode("utf-8")

    return {
        "plan": plan,
        "risks": risks,
        "answer": iac_code,
        "diagram": diagram_b64
    }


@app.get("/", response_class=HTMLResponse)
def index():
    return HTML

# For FastAPI Dosc
@app.post("/run")
def run(query: str):
    return run_agentic_system(query)