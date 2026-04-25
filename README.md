# 🚀 AI-Powered Agentic Security + IaC Visualization

An end-to-end **Agentic AI system** that:

* 🧠 Plans tasks
* 🔍 Retrieves context (RAG)
* 🛡️ Performs security analysis
* ⚙️ Generates Terraform (IaC)
* 🖼️ Automatically visualizes infrastructure as an architecture diagram

All through a **simple FastAPI web UI**.

---

## 📌 Features

* Multi-agent pipeline:

  * Planner
  * Retriever
  * Security Analyzer
  * Responder
* Clean Terraform (IaC) generation
* Automatic `.tf` file creation (`infra.tf`)
* Architecture diagram generation using IaC
* Interactive web UI (no Swagger needed)
* Real-time execution flow visualization

---

## 🏗️ Architecture Flow

```
User Query
   ↓
Planner Agent
   ↓
Retriever (RAG Context)
   ↓
Security Analyzer
   ↓
Responder (Generates IaC)
   ↓
clean_iac_answer()
   ↓
infra.tf (Terraform file)
   ↓
diagram.py
   ↓
Architecture Diagram (PNG)
   ↓
Displayed in UI
```

---

## 📂 Project Structure

```
agentic_ai/
│
├── app.py                # FastAPI app + UI
├── diagram.py             # Terraform → Architecture Diagram
├── infra.tf               # Generated IaC (auto-created)
├── llm.py
├── ingest.py
├── rag.py  
│
├── agents/
│   ├── planner.py
│   ├── retriever.py
│   ├── security.py
│   └── responder.py
│
├── tests/
│   ├── test_basic.py
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/agentic-ai.git
cd agentic-ai
```

---

### 2. Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# OR
source .venv/bin/activate  # Mac/Linux
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Install Graphviz (Required only if you need to run it locally)

👉 https://graphviz.org/download/

Make sure it's added to your system PATH.

---

## ▶️ Run the Application

```bash
uvicorn main:app --reload
```

Open in browser:

```
http://127.0.0.1:8000/
```

---

## 💻 How It Works

1. Enter a query in the UI
2. System:

   * Plans solution
   * Retrieves context
   * Analyzes risks
   * Generates Terraform code
3. Terraform is saved as:

   ```
   infra.tf
   ```
4. `diagram.py`:

   * Parses Terraform using `hcl2`
   * Generates architecture diagram using `diagrams`
5. Diagram is displayed directly in UI

---

## 📊 Output

### ✅ UI Displays:

* Plan
* Security Risks
* Clean Terraform Code
* Architecture Diagram

---

## 🧠 Example Query

```
Create a simple AWS application to sell books online
```

---

## ⚠️ Known Requirements

* Python 3.12+
* Graphviz installed
* Internet access (for LLM APIs)

---

## 🚀 Future Enhancements

* Multi-cloud support (Azure, GCP)
* Terraform validation (linting)
* Security scoring
* Export diagrams (PDF, SVG)
* Live deployment option

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first.

---

## 📄 License

MIT License

---

## 👨‍💻 Author

Kiran K
Cybersecurity & AI Enthusiast
