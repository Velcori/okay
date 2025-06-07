print("Starting main.py execution")

from flask import Flask, jsonify

print("Imported Flask")

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    print("Received GET /")
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    print(f"Running on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)
