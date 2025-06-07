from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return 'Stripe webhook server is up and running!'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Railway sets $PORT
    app.run(host='0.0.0.0', port=port)
