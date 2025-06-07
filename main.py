import os
import stripe
import requests
from flask import Flask, request, jsonify

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

    if event["type"].startswith("payment_intent."):
        payment_intent = event["data"]["object"]
        amount = payment_intent["amount_received"] / 100
        currency = payment_intent["currency"].upper()
        description = payment_intent.get("description", "No description")

        discord_message = {
            "content": f"💰 Payment received: ${amount} {currency}\nDescription: {description}"
        }
        requests.post(DISCORD_WEBHOOK_URL, json=discord_message)

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
