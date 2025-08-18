import uuid, time
from .database import load_data, save_data

def generate_key(days):
    data = load_data()
    key = str(uuid.uuid4())[:10]
    expiry = int(time.time()) + days * 86400
    data["premium_keys"][key] = {"expiry": expiry, "used": False}
    save_data(data)
    return key

def validate_key(user_id, key):
    data = load_data()
    if key in data["premium_keys"] and not data["premium_keys"][key]["used"]:
        expiry = data["premium_keys"][key]["expiry"]
        if int(time.time()) < expiry:
            data["premium_users"][str(user_id)] = expiry
            data["premium_keys"][key]["used"] = True
            save_data(data)
            return True
    return False

def is_premium(user_id):
    data = load_data()
    uid = str(user_id)
    return uid in data["premium_users"] and data["premium_users"][uid] > time.time()
