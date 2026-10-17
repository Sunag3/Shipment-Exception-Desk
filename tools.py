import re

def calculate_delay_compensation(shipment_value: float, report_text: str) -> dict:
    """
    Calculates shipment delay compensation based on shipment value and incident report text.
    
    Args:
        shipment_value (float): The total monetary value of the shipment.
        report_text (str): Descriptive report of the delay, cause, and duration.
        
    Returns:
        dict: Compensation details including amount, days delayed, applied percentage, and reason.
    """
    text_lower = report_text.lower()
    
    # 1. Extract delay duration (e.g., "delayed by 3 days", "3-day delay")
    days_match = re.search(r'(\d+)\s*(?:days?|day)', text_lower)
    delay_days = int(days_match.group(1)) if days_match else 0
    
    # 2. Check for force majeure or exempt causes
    force_majeure_keywords = [
        'weather', 'storm', 'strike', 'natural disaster', 
        'customs hold', 'force majeure', 'act of god', 'government'
    ]
    is_force_majeure = any(keyword in text_lower for keyword in force_majeure_keywords)
    
    if is_force_majeure:
        return {
            "compensation_amount": 0.0,
            "delay_days": delay_days,
            "percentage_applied": 0.0,
            "compensable": False,
            "reason": "Delay caused by exempt external factors (force majeure / weather / customs)."
        }
        
    # 3. Standard compensation rules (Example: 1% per day of delay, capped at 20% max)
    daily_rate = 0.01      # 1% per day
    max_cap_rate = 0.20    # Maximum cap of 20%
    
    calculated_rate = min(delay_days * daily_rate, max_cap_rate)
    compensation_amount = round(shipment_value * calculated_rate, 2)
    
    return {
        "compensation_amount": compensation_amount,
        "delay_days": delay_days,
        "percentage_applied": round(calculated_rate * 100, 2),
        "compensable": True,
        "reason": f"Standard carrier delay of {delay_days} day(s) applied at {daily_rate * 100}% per day."
    }


def calculate_damage_compensation(shipment_value: float, report_text: str) -> dict:
    """
    Calculates shipment damage compensation based on shipment value and damage report text.
    
    Args:
        shipment_value (float): The total monetary value of the shipment.
        report_text (str): Descriptive report of the damage, condition, and severity.
        
    Returns:
        dict: Compensation details including amount, severity level, applied percentage, and reason.
    """
    text_lower = report_text.lower()
    
    # 1. Define severity keyword categories and their corresponding payout percentages
    # Total loss / catastrophic
    total_loss_keywords = ['destroyed', 'total loss', 'crushed', 'unusable', 'complete ruin', 'smashed']
    # Severe damage
    severe_keywords = ['severe', 'heavy', 'major', 'broken', 'extensive', 'compromised', 'deep dents']
    # Moderate damage
    moderate_keywords = ['moderate', 'partial', 'dented', 'scratch', 'torn', 'leak', 'wet']
    # Minor damage
    minor_keywords = ['minor', 'scuff', 'cosmetic', 'slight', 'surface']
    
    # 2. Evaluate severity and determine compensation percentage
    if any(kw in text_lower for kw in total_loss_keywords):
        percentage = 1.00
        severity = "Total Loss"
    elif any(kw in text_lower for kw in severe_keywords):
        percentage = 0.75
        severity = "Severe"
    elif any(kw in text_lower for kw in moderate_keywords):
        percentage = 0.40
        severity = "Moderate"
    elif any(kw in text_lower for kw in minor_keywords):
        percentage = 0.10
        severity = "Minor"
    else:
        # Default fallback if no specific damage keywords are matched
        percentage = 0.05
        severity = "Unspecified / Minimal"
        
    # 3. Calculate final compensation amount
    compensation_amount = round(shipment_value * percentage, 2)
    
    return {
        "compensation_amount": compensation_amount,
        "severity_level": severity,
        "percentage_applied": round(percentage * 100, 2),
        "compensable": True,
        "reason": f"Damage classified as '{severity}' based on report wording, applying a {round(percentage * 100)}% compensation rate."
    }


def calculate_lost_compensation(shipment_value: float, report_text: str) -> dict:
    """
    Calculates shipment compensation for a lost shipment based on shipment value and incident report text.
    
    Args:
        shipment_value (float): The total monetary value of the shipment.
        report_text (str): Descriptive report confirming the loss or disappearance of the shipment.
        
    Returns:
        dict: Compensation details including full amount, confirmation status, and reason.
    """
    text_lower = report_text.lower()
    
    # 1. Check for keywords indicating loss, theft, or missing status
    loss_keywords = [
        'lost', 'missing', 'stolen', 'unaccounted for', 
        'disappeared', 'not delivered', 'undeliverable', 'unlocatable'
    ]
    
    is_confirmed_lost = any(keyword in text_lower for keyword in loss_keywords)
    
    # 2. Determine compensation payout (Full value for lost shipments if confirmed)
    if is_confirmed_lost:
        compensation_amount = round(shipment_value, 2)
        percentage = 1.00
        status = "Confirmed Lost"
        reason = "Shipment confirmed lost/missing based on report wording. Full compensation applied."
    else:
        # Fallback if the report doesn't clearly state loss
        compensation_amount = 0.0
        percentage = 0.0
        status = "Unconfirmed"
        reason = "Report does not clearly indicate loss or missing status. Verification required."

    return {
        "compensation_amount": compensation_amount,
        "status": status,
        "percentage_applied": round(percentage * 100, 2),
        "compensable": is_confirmed_lost,
        "reason": reason
    }