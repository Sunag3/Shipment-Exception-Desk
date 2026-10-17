DAILY_LOG = []

"""

    final_state {
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
"""
def record(final_state: dict):
    DAILY_LOG.append(final_state)



def generate_daily_summary() -> str:
    if not DAILY_LOG:
        return "No Exceptions processed yet today"

    total_compensation = sum(e['compensation'] for e in DAILY_LOG)
    escalated = [e for e in DAILY_LOG if e['needs_approval']]
    escalation_rate = round((100 * len(escalated)) / len(DAILY_LOG), 1)

    by_category = dict()

    for e in DAILY_LOG:
        cat = e['category']
        by_category[cat] = by_category.get(cat, 0.0) + e['compensation']

    costliest_category = max(by_category, key=by_category.get) if by_category else 'N/A'

    lines = [
        "========================================",
        "        DAILY TRIAGE LOG SUMMARY        ",
        "========================================",
        f"Total Claims Processed : {len(DAILY_LOG)}",
        f"Total Compensation Paid: ${total_compensation:,.2f}",
        f"Claims Escalated (HIL) : {len(escalated)} ({escalation_rate}%)",
        f"Costliest Category     : {costliest_category.title()} (${by_category.get(costliest_category, 0.0):,.2f})",
        "----------------------------------------",
        "Compensation Breakdown by Category:"
    ]

    for cat, amount in by_category.items():
        lines.append(f"  - {cat.title():<12}: ${amount:,.2f}")

    lines.append("========================================")

    return "\n".join(lines)

