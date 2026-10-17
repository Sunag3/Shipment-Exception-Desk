from tools import (
    calculate_delay_compensation,
    calculate_damage_compensation,
    calculate_lost_compensation
)
from chains import classify_chain, escalation_chain, draft_email_chain
import mlflow
import os
import sys


# Safely initialize MLflow tracking and autologging
# If the local server (port 5000) is down (e.g. during pytest), it won't crash import collection.

if "pytest" not in sys.modules:
    try:
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment("Shipment Exception Automation")
        mlflow.langchain.autolog()
    except Exception as e:
        print(f"Warning: MLflow server unreachable. Running without remote tracking. ({e})")

STANDARD_ESCALATION_THRESHOLD = 200.0
PREMIUM_ESCALATION_THRESHOLD = 100.0

def process_exception(report_text: str, shipment_value: float, customer_tier: str) -> dict:
    log = []

    # Safely handle mlflow run tracking if the server is offline
    try:
        active_run = mlflow.start_run(run_name="shipment_exception")
    except Exception:
        active_run = None

    try:
        if active_run:
            mlflow.log_param("shipment_value", shipment_value)
            mlflow.log_param("customer_tier", customer_tier)
            mlflow.log_param("report_text", report_text[:200])

        # ---------- Classification ----------
        raw_category = classify_chain.invoke({
            "report_text": report_text,
            "shipment_value": shipment_value
        }).strip().lower()

        if raw_category == "delayed":
            category = "delayed"
            comp = calculate_delay_compensation(shipment_value, report_text)
        elif raw_category == "damaged":
            category = "damaged"
            comp = calculate_damage_compensation(shipment_value, report_text)
        elif raw_category == "lost":
            category = "lost"
            comp = calculate_lost_compensation(shipment_value, report_text)
        else:
            category = "unknown"
            comp = {
                "compensation_amount": 0.0,
                "reason": "Could not confidently classify this report"
            }

        log.append(f"Classified as '{category}'")
        log.append(f"Compensation calculated: ${comp['compensation_amount']:.2f}")

        # ---------- Escalation logic ----------
        threshold = (
            PREMIUM_ESCALATION_THRESHOLD
            if customer_tier == "premier"
            else STANDARD_ESCALATION_THRESHOLD
        )

        needs_approval = category == "unknown" or comp["compensation_amount"] > threshold

        chain_input = {
            "report_text": report_text,
            "category": category,
            "amount": comp["compensation_amount"],
            "reasoning": comp["reason"],
            "compensable": not needs_approval
        }

        if needs_approval:
            message_draft = escalation_chain.invoke(chain_input)
            log.append("Escalated to Manager for approval")
        else:
            message_draft = draft_email_chain.invoke(chain_input)
            log.append("Direct customer payout notification drafted")

        # ---------- Log outputs / metrics ----------
        if active_run:
            mlflow.log_param("category", category)
            mlflow.log_param("needs_approval", needs_approval)
            mlflow.log_metric("compensation_amount", comp["compensation_amount"])
            mlflow.log_param("compensation_reason", comp["reason"][:150])

            with open("message_draft.txt", "w", encoding="utf-8") as f:
                f.write(message_draft)
            mlflow.log_artifact("message_draft.txt")

        return {
            "report_text": report_text,
            "shipment_value": shipment_value,
            "customer_tier": customer_tier,
            "category": category,
            "compensation": comp["compensation_amount"],
            "compensation_reason": comp["reason"],
            "needs_approval": needs_approval,
            "message_draft": message_draft,
            "log": log
        }
    finally:
        if active_run and mlflow.active_run():
            mlflow.end_run()