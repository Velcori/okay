import os
import stripe
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    if event["type"] == "payment_intent.succeeded":
        pi = event["data"]["object"]
        amount = pi["amount_received"] / 100
        currency = pi["currency"].upper()
        requests.post(DISCORD_WEBHOOK_URL, json={
            "content": f"✅ New payment received: **{amount} {currency}**"
        })

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway sets $PORT
    app.run(host="0.0.0.0", port=port)
