```markdown
# 📦 Shipment Exception & Triage Desk

An AI-powered logistics claims processing system that automatically classifies shipment exceptions, calculates policy-based compensation, drafts customer/HIL communication, and maintains a daily triage log.

---

## Features

- **Automatic Classification** of incident reports into:
  - `delayed`
  - `damaged`
  - `lost`
  - `unknown`
- **Policy-based Compensation Calculation**
  - Delay: 1% per day (capped at 20%)
  - Damage: Severity-based (10% – 100%)
  - Lost: Full shipment value
  - Force Majeure / Customs / Weather → $0 compensation
- **Human-in-the-Loop (HIL) Escalation** when compensation exceeds thresholds or category is unknown
- **Auto-generated Email Drafts** (Customer notification or Supervisor escalation)
- **Daily Triage Summary Log**

---

## Project Structure

```
Shipment Exception Desk/
├── app.py                 # Gradio UI
├── pipeline.py            # Main processing logic
├── chains.py              # LangChain prompts & chains
├── tools.py               # Compensation calculation tools
├── session.py             # Daily log & summary
├── llm.py                 # LLM configuration
├── test_triage_check.py   # Pytest test suite
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Create & activate virtual environment

```bash
python -m venv .venv

# Windows (Git Bash)
source .venv/Scripts/activate

# Windows (CMD)
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set OpenAI API Key

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-key-here
```

---

## How to Run

### Launch the Gradio UI

```bash
python app.py
```

Open the local URL shown in the terminal (usually `http://127.0.0.1:7860`).

### Run Tests

```bash
pytest test_triage_check.py -v
```

---

## Business Rules

| Category   | Compensation Rule                          | Escalation Threshold          |
|------------|--------------------------------------------|-------------------------------|
| Delayed    | 1% per day (max 20%)                       | Standard: $200 / Premier: $100 |
| Damaged    | 10% – 100% based on severity               | Same as above                 |
| Lost       | 100% of shipment value                     | Same as above                 |
| Unknown    | $0                                         | Always escalates              |
| Force Majeure / Weather / Customs | $0                            | No escalation if $0           |

---

## Example Usage

**Input:**
```
Report: The shipment was delayed by 4 days due to severe winter storms and a regional customs hold at the port terminal
Value:  $500
Tier:   standard
```

**Output:**
- Category: `delayed`
- Compensation: `$0.00` (Force Majeure)
- Needs HIL: `False`
- Message Draft: Customer notification explaining no compensation due to external factors

---

## Tech Stack

- **LangChain** + **OpenAI (gpt-4o-mini)**
- **Gradio** for the UI
- **Pytest** for testing
- **Python 3.11 / 3.12 / 3.13**

---

## Notes

- Classification quality depends heavily on the prompt in `chains.py`.
- Force majeure keywords (weather, storm, customs, strike, etc.) automatically set compensation to $0.
- Daily log is stored in memory (`session.DAILY_LOG`) and resets when the process restarts.
```