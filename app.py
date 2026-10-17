import gradio as gr
from pipeline import process_exception
from session import record, generate_daily_summary

def handle_exception_submission(report_text: str, shipment_value: float, customer_tier: str):
    """
    Processes the exception through the pipeline, records it in the session log,
    and returns formatted outputs for the Gradio UI.
    """
    if not report_text.strip():
        return "Error: Please provide a valid incident report text.", "N/A", "$0.00", "No action taken."

    try:
        # 1. Run through pipeline[cite: 3]
        result = process_exception(
            report_text=report_text,
            shipment_value=float(shipment_value),
            customer_tier=customer_tier
        )

        # 2. Record to session daily log[cite: 6]
        record(result)

        # 3. Format outputs
        category_out = result["category"].upper()
        compensation_out = f"${result['compensation']:,.2f} ({result['compensation_reason']})"
        message_draft_out = result["message_draft"]

        return category_out, compensation_out, message_draft_out

    except Exception as e:
        return "ERROR", "$0.00", f"An error occurred during pipeline execution:\n{str(e)}"

def handle_generate_summary():
    """Generates and returns the current daily triage log summary."""
    return generate_daily_summary()


# --- Gradio UI Layout ---
with gr.Blocks(theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="blue")) as demo:
    gr.Markdown("# 📦 Shipment Exception & Triage Desk")
    gr.Markdown("Process customer shipment exceptions, calculate policy-backed compensation, generate communication drafts, and track daily session logs automatically[cite: 4].")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📝 Incident Input")
            report_input = gr.Textbox(
                label="Report Text",
                placeholder="e.g., The package was delayed by 4 days due to customs hold...",
                lines=4
            )
            value_input = gr.Number(
                label="Shipment Value ($)",
                value=500.0,
                precision=2
            )
            tier_input = gr.Dropdown(
                label="Customer Tier",
                choices=["standard", "premier"],
                value="standard"
            )
            
            with gr.Row():
                process_btn = gr.Button("🚀 Process Exception", variant="primary")
                summary_btn = gr.Button("📊 Generate Daily Triage Log")

        with gr.Column(scale=1):
            gr.Markdown("### 🔍 Triage Results & Outputs")
            category_output = gr.Textbox(label="Classified Category")
            compensation_output = gr.Textbox(label="Compensation Payout & Details")
            message_output = gr.Textbox(label="Generated Message Draft (Customer / HIL)", lines=6)

    with gr.Row():
        with gr.Column(scale=1):
            log_summary_output = gr.Textbox(
                label="Daily Triage Summary Log",
                lines=12,
                max_lines=20
            )

    # Event bindings
    process_btn.click(
        fn=handle_exception_submission,
        inputs=[report_input, value_input, tier_input],
        outputs=[category_output, compensation_output, message_output]
    )

    summary_btn.click(
        fn=handle_generate_summary,
        inputs=[],
        outputs=[log_summary_output]
    )

if __name__ == "__main__":
    demo.launch()