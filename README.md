![Uploading image.png…]()



```markdown
# 📦 Shipment Exception & Triage Desk

An AI-powered logistics claims processing system that automatically classifies shipment exceptions, calculates policy-based compensation, drafts customer/HIL communication, and maintains a daily triage log.

It also integrates **MLflow** for experiment tracking and can be run easily using **Docker**.

---

## Features

- Automatic classification of incident reports into:
  - `delayed`
  - `damaged`
  - `lost`
  - `unknown`
- Policy-based compensation calculation
- Human-in-the-Loop (HIL) escalation when needed
- Auto-generated email drafts (Customer / Supervisor)
- Daily triage summary log
- **MLflow tracking** for every claim processed
- Ready-to-run with Docker (Gradio + MLflow)

---

## Project Structure

```
Shipment Exception Desk/
├── app.py                  # Gradio UI
├── pipeline.py             # Main processing logic + MLflow logging
├── chains.py               # LangChain prompts & chains
├── tools.py                # Compensation calculation logic
├── session.py              # Daily log & summary
├── llm.py                  # LLM configuration
├── test_triage_check.py    # Pytest test suite
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env                    # OpenAI API Key
└── README.md
```

---

## Installation (Local)

### 1. Create virtual environment

```bash
python -m venv .venv
source .venv/Scripts/activate      # Git Bash / Linux / Mac
# or
.venv\Scripts\activate             # Windows CMD
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set OpenAI API Key

Create a `.env` file:

```env
OPENAI_API_KEY=sk-your-key-here
```

---

## How to Run (Local)

### Start the Gradio App

```bash
python app.py
```

Open → [http://127.0.0.1:7860](http://127.0.0.1:7860)

### Start MLflow UI

```bash
mlflow ui
```

Open → [http://127.0.0.1:5000](http://127.0.0.1:5000)

### Run Tests

```bash
pytest test_triage_check.py -v
```

---

## Business Rules

| Category     | Compensation Rule                        | Escalation Condition                  |
|--------------|------------------------------------------|---------------------------------------|
| Delayed      | 1% per day (max 20%)                     | Amount > threshold                    |
| Damaged      | 10% – 100% based on severity             | Amount > threshold                    |
| Lost         | 100% of shipment value                   | Amount > threshold                    |
| Unknown      | $0                                       | Always escalates                      |
| Force Majeure / Weather / Customs | $0                            | No escalation if $0                   |

**Escalation Thresholds:**
- Standard tier → **$200**
- Premier tier → **$100**

---

## Sample Test Prompts & Expected Results

| # | Sample Report Text | Expected Category | Expected Compensation | Escalation (HIL) |
|---|--------------------|-------------------|-----------------------|------------------|
| 1 | The shipment was delayed by 4 days due to severe winter storms and a regional customs hold at the port terminal | `delayed` | $0.00 (Force Majeure) | No |
| 2 | The package was delayed by 3 days due to carrier operational issues at the sorting hub | `delayed` | 3% of value | Depends on amount |
| 3 | Shipment delayed by 25 days because of multiple internal routing errors by the carrier | `delayed` | 20% (capped) | Usually Yes |
| 4 | The box arrived completely crushed and the contents are destroyed and unusable | `damaged` | 100% | Yes |
| 5 | The package has moderate damage - the outer box is dented and one item inside is scratched | `damaged` | ~40% | Depends |
| 6 | There is only minor cosmetic damage - a small scuff on the packaging, product is fine | `damaged` | ~10% | Usually No |
| 7 | The shipment is missing and has been marked as lost by the carrier. It was never delivered. | `lost` | 100% | Yes |
| 8 | The package disappeared after leaving the last distribution center and is now reported as stolen | `lost` | 100% | Yes |
| 9 | Something went wrong with my delivery last week | `unknown` | $0.00 | Yes |
| 10 | Package delayed 6 days due to customs inspection and government clearance procedures | `delayed` | $0.00 (Force Majeure) | No |
| 11 | The shipment was delayed by 5 days due to internal carrier issues (Value $1500 + Premier) | `delayed` | 5% | Yes |

---

## MLflow Integration

Every claim processed is logged to MLflow with:

- Input parameters (`shipment_value`, `customer_tier`, report text)
- Classification result (`category`)
- Compensation amount
- Whether HIL was needed
- Generated message draft (as artifact)

**View experiments:**

```bash
mlflow ui
```

Then open → [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Docker Setup

### Files required

- `Dockerfile`
- `docker-compose.yml`
- `.env` (with `OPENAI_API_KEY`)

### Run with Docker

```bash
# Build and start both services
docker-compose up --build -d

# View logs
docker-compose logs -f
```

### Access Services

| Service       | URL                        |
|---------------|----------------------------|
| Gradio App    | http://localhost:7860      |
| MLflow UI     | http://localhost:5000      |

### Useful Docker Commands

```bash
# Stop everything
docker-compose down

# Rebuild after code changes
docker-compose up --build -d

# View only app logs
docker-compose logs -f app

# View only mlflow logs
docker-compose logs -f mlflow
```

---

## Tech Stack

- LangChain + OpenAI (`gpt-4o-mini`)
- Gradio (UI)
- MLflow (Experiment tracking)
- Pytest
- Docker & Docker Compose
- Python 3.12

---

## Notes

- Classification quality depends heavily on the prompt in `chains.py`.
- Force majeure keywords (`weather`, `storm`, `customs`, `strike`, etc.) automatically set compensation to `$0`.
- Daily log is stored in memory (`session.DAILY_LOG`) and resets when the process restarts.
- MLflow runs are stored in the `mlruns/` folder.
```
