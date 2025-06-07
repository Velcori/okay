from flask import Flask

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)
