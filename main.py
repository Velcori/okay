import os
import stripe
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timezone

app = Flask(__name__)

STRIPE_SECRET = os.getenv("STRIPE_SECRET")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET")

stripe.api_key = STRIPE_SECRET

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route("/", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_ENDPOINT_SECRET
        )
    except ValueError:
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({"error": "Invalid signature"}), 400

    print("🔔 Stripe event:", event["type"])

    if event["type"].startswith("payment_intent."):
        pi = event["data"]["object"]
        status = pi.get("status")

        amount = (pi.get("amount_received") or pi.get("amount") or 0) / 100
        currency = pi.get("currency", "usd").upper()
        description = pi.get("description", "No description")

        # Generate custom message per status
        if status == "succeeded":
            content = f"Payment Succeeded!\n ${amount} {currency}"
        elif status == "requires_action":
            content = f"Payment incomplete!\n ${amount} {currency}"
        elif status == "created":
            content = f"Payment created!\n ${amount} {currency}"
        else:
            content = f"Unknown status {status}\n ${amount} {currency}"

        discord_message = { "content": content }
        response = requests.post(DISCORD_WEBHOOK_URL, json=discord_message)
        print("📤 Discord response:", response.status_code)

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
