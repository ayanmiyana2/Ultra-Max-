import json, os

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "banned": [],
            "premium_users": {},    # {userid: expiry}
            "premium_keys": {},    # {key: {"expiry":..., "used":False/True}}
            "free_mode": False,
            "accounts": [],        # [{email, password, service, used_by:[]} ...]
            "points": {},          # {userid: points}
            "redeem_used": {},     # {userid: True/False}
            "pending_redeem": {}   # {userid: {"msg":..., "text":...}}
        }
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
