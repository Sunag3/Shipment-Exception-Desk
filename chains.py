from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm import llm


# 1. Define the Prompt (Strictly restricted to the 4 classification categories)
classify_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a logistics claims classifier.\n\n"
        "Classify the given incident report into EXACTLY one of these four categories:\n"
        "- delayed\n"
        "- damaged\n"
        "- lost\n"
        "- unknown\n\n"
        "Rules:\n"
        "- If the report mentions delay, late, days late, held, customs hold, weather delay → delayed\n"
        "- If the report mentions damage, broken, crushed, destroyed, wet, dented → damaged\n"
        "- If the report mentions lost, missing, stolen, never delivered, disappeared → lost\n"
        "- Only use unknown if you truly cannot decide.\n\n"
        "Reply with ONLY the category word. Do not write any other text."
    ),
    ("human", "Shipment Value: ${shipment_value}\nReport Text: {report_text}")
])

# 2. Define the Chain
classify_chain = classify_prompt | llm | StrOutputParser()



# System prompt configured to receive data directly from previous agent steps
escalation_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an AI logistics assistant drafting an escalation email to a Human-in-the-Loop (HIL) supervisor.\n"
        "Draft a concise, professional email requesting review and approval based on the claim details provided below:\n\n"
        "Incident Details:\n"
        "- Category: {category}\n"
        "- Compensation Amount: ${amount}\n"
        "- Reasoning: {reasoning}\n"
        "- Original Report Text: {report_text}\n\n"
        "Email Draft Requirements:\n"
        "1. Include a clear subject line with the claim category.\n"
        "2. Summarize the incident details clearly for supervisor review.\n"
        "3. Provide a clear call to action asking for approval or decision."
    )
])

# Chain setup
escalation_chain = escalation_prompt | llm | StrOutputParser()


# Combined prompt taking all inputs directly from the previous agent state
draft_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an AI logistics assistant drafting an email based on the claim analysis from the previous agent step.\n\n"
        "Claim Details Received:\n"
        "- Category: {category}\n"
        "- Compensation Amount: ${amount}\n"
        "- Compensable Status: {compensable}\n"
        "- Reasoning: {reasoning}\n"
        "- Report Text: {report_text}\n\n"
        "Instructions:\n"
        "1. IF amount > 0 (NO HIL NEEDED):\n"
        "   - Draft a polite, professional notification email to the CUSTOMER.\n"
        "   - Subject Line: Claim Approved - {category} Shipment\n"
        "   - Inform them that compensation of ${amount} has been approved.\n"
        "   - Provide the reasoning and mention payout processing steps.\n\n"
        "2. amount == 0 (HIL ESCALATION REQUIRED):\n"
        "   - Draft an escalation request email to the SUPERVISOR / HIL TEAM.\n"
        "   - Subject Line: Claim Escalation Review Required - {category}\n"
        "   - Explain why the automated system could not approve payout and request manual decision."
    )
])

# Single unified email chain
draft_email_chain = draft_prompt | llm | StrOutputParser()