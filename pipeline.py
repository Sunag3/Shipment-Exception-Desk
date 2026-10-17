from tools import (
    calculate_delay_compensation,
    calculate_damage_compensation,
    calculate_lost_compensation
)

from chains import classify_chain, escalation_chain, draft_email_chain

STANDARD_ESCALATION_THRESHOLD = 200.0
PREMIUM_ESCALATION_THRESHOLD = 100.0


def process_exception(report_text: str, shipment_value: float, customer_tier: str) -> dict:
    log = []

    raw_category = classify_chain.invoke({
        "report_text": report_text,
        "shipment_value": shipment_value
    }).strip().lower()

    if raw_category == "delayed":
        category = 'delayed'
        comp = calculate_delay_compensation(shipment_value, report_text)

    elif raw_category == "damaged":
        category = 'damaged'
        comp = calculate_damage_compensation(shipment_value, report_text)

    elif raw_category == "lost":
        category = 'lost'
        comp = calculate_lost_compensation(shipment_value, report_text)

    else:
        category = 'unknown'
        comp = {'compensation_amount': 0.0, 'reason': "Could not confidently classify this report"}

    log.append(f"Classified as '{category}'")
    log.append(f"Compensation calculated: ${comp['compensation_amount']:.2f}")

    threshold = PREMIUM_ESCALATION_THRESHOLD if customer_tier == 'premier' else STANDARD_ESCALATION_THRESHOLD

    needs_approval = category == 'unknown' or comp['compensation_amount'] > threshold

    chain_input = {
        "report_text": report_text,
        "category": category,
        "amount": comp['compensation_amount'],
        "reasoning": comp['reason'],
        "compensable": True if not needs_approval else False
    }

    if needs_approval:
        message_draft = escalation_chain.invoke(chain_input)
        log.append("Escalated to Manager for approval")
    else:
        message_draft = draft_email_chain.invoke(chain_input)
        log.append("Direct customer payout notification drafted")

    return {
        "report_text": report_text,
        "shipment_value": shipment_value,
        "customer_tier": customer_tier,
        "category": category,
        "compensation": comp['compensation_amount'],
        "compensation_reason": comp['reason'],
        "needs_approval": needs_approval,
        "message_draft": message_draft,
        "log": log
    }