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
        created_unix = pi.get("created")

        status_titles = {
            "succeeded": ("✅ Payment Succeeded", 0x2ecc71),
            "processing": ("⏳ Payment Processing", 0xf1c40f),
            "requires_action": ("⚠️ Requires Action", 0xe67e22),
            "requires_capture": ("📸 Requires Capture", 0x9b59b6),
            "requires_confirmation": ("📝 Requires Confirmation", 0x3498db),
            "requires_payment_method": ("💳 Needs Payment Method", 0xe74c3c),
            "canceled": ("❌ Payment Canceled", 0x95a5a6)
        }

        title, color = status_titles.get(status, (f"🤖 Unknown Status: {status}", 0x7289da))

        embed = {
            "title": title,
            "color": color,
            "fields": [
                {"name": "💰 Amount", "value": f"${amount:.2f} {currency}", "inline": True},
                {"name": "📝 Description", "value": description, "inline": True},
                {"name": "🆔 Payment Intent", "value": pi.get("id"), "inline": False}
            ],
            "timestamp": datetime.fromtimestamp(created_unix, timezone.utc).isoformat() if created_unix else None
        }

        payload = {
            "embeds": [embed]
        }

        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        print("📤 Discord response:", response.status_code)

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
