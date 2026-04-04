import os
from flask import Flask, jsonify

app = Flask(__name__)

APP_ENV = os.getenv("APP_ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-insecure-key")

@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "environment": APP_ENV,
        "message": "DevOps Demo App is running"
    })

@app.route("/health")
def health():
    return jsonify({"healthy": True}), 200

@app.route("/version")
def version():
    return jsonify({"version": "1.0.0", "env": APP_ENV}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
