"""
Requirement #9: Central PII masking function.
Requirement #10: No clear-text PII in logs or error messages.
"""

import re
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)


# Example: mask credit card numbers in logs with a simple pattern: "####-####-####-1234"
def mask_credit_card(cc_number: str) -> str:
    # Very naive example for demonstration
    if len(cc_number) < 12:
        return cc_number  # or some fallback
    return f"####-####-####-{cc_number[-4:]}"


def redact_pii(message: str) -> str:
    """
    Replace any credit card patterns with masked versions.
    Real logic might handle multiple PII types (SSN, phone, etc.).
    """
    # Simple regex for demonstration (looking for digits separated by optional dashes/spaces)
    pattern = r"\b(\d[ -]*){12,19}\b"

    def _mask_match(match):
        raw = re.sub(r"[ -]", "", match.group(0))  # remove spaces/dashes
        return mask_credit_card(raw)

    return re.sub(pattern, _mask_match, message)


logger = logging.getLogger("pii_logger")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)


@app.errorhandler(Exception)
def handle_exception(e):
    # Generic error handler that redacts PII from the exception message
    safe_message = redact_pii(str(e))
    logger.error(f"Exception: {safe_message}")
    return jsonify({"error": "Internal Server Error"}), 500


@app.route("/process_payment", methods=["POST"])
def process_payment():
    cc_number = request.form.get("credit_card")
    amount = request.form.get("amount")

    if not cc_number or not amount:
        return jsonify({"error": "Missing credit card or amount"}), 400

    # Redact in logs
    masked_cc = mask_credit_card(cc_number)
    logger.info(f"Processing payment with CC={masked_cc}, amount={amount}")

    # Simulate processing
    # ...
    return jsonify({"message": f"Payment of {amount} processed successfully."})


if __name__ == "__main__":
    app.run()
