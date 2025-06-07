import stripe
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

stripe.api_key = "sk_test_..."  # Your secret key
endpoint_secret = "whsec_..."   # From Stripe dashboard
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."

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
            "content": f"✅ Received {amount} {currency} payment!"
        })

    return jsonify({"status": "ok"})
