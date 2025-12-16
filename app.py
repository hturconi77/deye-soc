import os
import time
import requests
from flask import Flask, jsonify

app = Flask(__name__)

DEYE_BASE = "https://developer.deyecloud.com"

APP_ID = os.environ["DEYE_APP_ID"]
APP_SECRET = os.environ["DEYE_APP_SECRET"]
EMAIL = os.environ["DEYE_EMAIL"]
PASSWORD = os.environ["DEYE_PASSWORD"]

token_cache = {"token": None, "expires": 0}

def get_token():
    if token_cache["token"] and time.time() < token_cache["expires"]:
        return token_cache["token"]

    r = requests.post(
        f"{DEYE_BASE}/v1.0/account/token",
        json={
            "email": EMAIL,
            "password": PASSWORD,
            "appId": APP_ID,
            "appSecret": APP_SECRET
        },
        timeout=10
    )
    r.raise_for_status()
    data = r.json()

    token_cache["token"] = data["accessToken"]
    token_cache["expires"] = time.time() + 7000
    return token_cache["token"]

def get_soc():
    headers = {"Authorization": f"Bearer {get_token()}"}

    plant = requests.get(
        f"{DEYE_BASE}/v1.0/plants",
        headers=headers,
        timeout=10
    ).json()["data"][0]["plantId"]

    device = requests.get(
        f"{DEYE_BASE}/v1.0/plants/{plant}/devices",
        headers=headers,
        timeout=10
    ).json()["data"][0]["deviceId"]

    status = requests.get(
        f"{DEYE_BASE}/v1.0/devices/{device}/status",
        headers=headers,
        timeout=10
    ).json()["data"]

    return status.get("batterySoc")

@app.route("/soc")
def soc():
    return jsonify({"soc": get_soc()})

@app.route("/")
def home():
    return "Deye SOC backend OK"

if __name__ == "__main__":
    app.run()
