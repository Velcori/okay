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
            content = f"✅ Payment Succeeded!\n💰 ${amount} {currency}\n📝 {description}"
        elif status == "processing":
            content = f"⏳ Payment is processing...\n💰 ${amount} {currency}\n📝 {description}"
        elif status == "requires_action":
            content = f"⚠️ Payment requires further action!\n💰 ${amount} {currency}\n📝 {description}"
        elif status == "requires_capture":
            content = f"📸 Payment requires capture.\n💰 ${amount} {currency}\n📝 {description}"
        elif status == "requires_confirmation":
            content = f"📝 Payment requires confirmation.\n💰 ${amount} {currency}\n📝 {description}"
        elif status == "requires_payment_method":
            content = f"💳 Payment method required.\n💰 ${amount} {currency}\n📝 {description}"
        elif status == "canceled":
            content = f"❌ Payment was canceled.\n💰 ${amount} {currency}\n📝 {description}"
        else:
            content = f"🤖 Unknown status `{status}`\n💰 ${amount} {currency}\n📝 {description}"

        discord_message = { "content": content }
        response = requests.post(DISCORD_WEBHOOK_URL, json=discord_message)
        print("📤 Discord response:", response.status_code)

    return jsonify({"status": "success"}), 200
