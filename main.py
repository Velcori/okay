from flask import Flask, request
import stripe
import requests
import os

app = Flask(__name__)

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        return 'Signature verification failed', 400

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        amount = intent['amount_received'] / 100
        currency = intent['currency'].upper()
        customer_email = intent.get('receipt_email', 'Unknown')

        message = {
            "content": f"✅ **New Payment Received**\nAmount: ${amount:.2f} {currency}\nEmail: {customer_email}"
        }

        requests.post(DISCORD_WEBHOOK_URL, json=message)

    return '', 200

@app.route('/')
def index():
    return 'Stripe Webhook is running!'

if __name__ == '__main__':
    app.run(port=5000)
