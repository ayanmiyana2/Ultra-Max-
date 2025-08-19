import json, random, string
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from config import BOT_TOKEN, ADMIN_IDS

app = Flask(__name__)

# ---------- Helper Functions ----------
def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# Files
KEYS_FILE = "data/keys.json"
POINTS_FILE = "data/points.json"
ACCOUNTS_FILE = "data/accounts.json"
STATE_FILE = "data/state.json"
USERS_FILE = "data/users.json"

# In-memory dictionaries
users_used_redeem = {}
pending_redeem = {}

# Ensure JSON files exist with default data
for f in [KEYS_FILE, POINTS_FILE, ACCOUNTS_FILE, STATE_FILE, USERS_FILE]:
    save_json(f, load_json(f))


# ---------- BOT Commands ----------
def start(update: Update, context: CallbackContext):
    uid = str(update.message.from_user.id)
    users = load_json(USERS_FILE)
    if uid not in users:
        users[uid] = {"plan": "free"}
        save_json(USERS_FILE, users)

    update.message.reply_text(
        "Welcome To Aizen Bot ⚡️\n"
        "Please Use this /redeem Command For Get Prime video 🧑‍💻 \n"
        "For Premium use This Command /premium"
    )


def redeem(update: Update, context: CallbackContext):
    uid = str(update.message.from_user.id)
    username = update.message.from_user.username
    name = update.message.from_user.first_name

    state = load_json(STATE_FILE)
    free_on = state.get("free_on", False)

    if uid in users_used_redeem and not free_on:
        return update.message.reply_text("Please Purchase Premium Key For Use 🗝️")

    if len(context.args) == 0:
        return update.message.reply_text("After /redeem Enter Your Account To Activate Premium ⚡️")

    msg = " ".join(context.args)

    for admin in ADMIN_IDS:
        context.bot.send_message(
            chat_id=admin,
            text=f"New Redeem Request:\nName: {name}\nUser: @{username}\nID: {uid}\nMsg: {msg}\n\n/approved_{uid} या /failed_{uid} से रिप्लाई करें।"
        )

    pending_redeem[uid] = msg
    users_used_redeem[uid] = True
    update.message.reply_text("Processing... ⚡️")


def premium(update: Update, context: CallbackContext):
    uid = str(update.message.from_user.id)
    if len(context.args) == 0:
        return update.message.reply_text("Send `/premium <key>` to activate.")

    key = context.args[0]
    keys = load_json(KEYS_FILE)
    users = load_json(USERS_FILE)

    if key in keys and not keys[key]["used"]:
        keys[key]["used"] = True
        save_json(KEYS_FILE, keys)
        users[uid]["plan"] = "premium"
        save_json(USERS_FILE, users)
        update.message.reply_text("Premium Activated ⚡️")
        for admin in ADMIN_IDS:
            context.bot.send_message(chat_id=admin, text=f"User {uid} upgraded to Premium ✅")
    else:
        update.message.reply_text("Invalid or Already Used Key ❌")


def genk(update: Update, context: CallbackContext):
    if update.message.from_user.id not in ADMIN_IDS:
        return
    if len(context.args) == 0:
        return update.message.reply_text("Usage: /genk <days>")

    days = context.args[0]
    key = ''.join(random.choices(string.ascii_uppercase+string.digits, k=12))
    keys = load_json(KEYS_FILE)
    keys[key] = {"days": days, "used": False}
    save_json(KEYS_FILE, keys)
    update.message.reply_text(f"Generated Key: {key} for {days} days")


def broadcast(update: Update, context: CallbackContext):
    if update.message.from_user.id not in ADMIN_IDS:
        return
    text = " ".join(context.args)
    users = load_json(USERS_FILE)
    for uid in users.keys():
        try:
            context.bot.send_message(chat_id=uid, text=text)
        except:
            pass
    update.message.reply_text("Broadcast done ✅")


def approved(update: Update, context: CallbackContext):
    if update.message.from_user.id not in ADMIN_IDS:
        return
    try:
        uid = update.message.text.split("_")[1]
    except:
        return
    users = load_json(USERS_FILE)
    plan = users.get(uid, {}).get("plan", "free")
    context.bot.send_message(chat_id=uid, text="Successfully Done ⚡️")
    u = context.bot.get_chat(uid)
    bc_msg = f"""
(╔═══━─༺༻─━═══╗
   ♛ New Order Done ♛
╚═══━─༺༻─━═══╝
༺🌸 New Redeem 🌸༻

👤 Name :⫸ {u.first_name}
✉️ Username :⫸ @{u.username}
🆔 UserID :⫸ {uid}
👑 User Plan :⫸ {plan}

⚡ Secure Service ⚡ )
"""
    all_users = load_json(USERS_FILE)
    for idd in all_users.keys():
        try:
            context.bot.send_message(chat_id=idd, text=bc_msg)
        except:
            pass


def failed(update: Update, context: CallbackContext):
    if update.message.from_user.id not in ADMIN_IDS:
        return
    try:
        uid = update.message.text.split("_")[1]
    except:
        return
    context.bot.send_message(chat_id=uid, text="Failed For Some Technical issues 🧑‍💻")


def on(update: Update, context: CallbackContext):
    if update.message.from_user.id not in ADMIN_IDS:
        return
    state = load_json(STATE_FILE)
    state["free_on"] = True
    save_json(STATE_FILE, state)
    update.message.reply_text("Free Service On time ⚡️")


def off(update: Update, context: CallbackContext):
    if update.message.from_user.id not in ADMIN_IDS:
        return
    state = load_json(STATE_FILE)
    state["free_on"] = False
    save_json(STATE_FILE, state)
    update.message.reply_text("Free Service Off ♻️")


def reply(update: Update, context: CallbackContext):
    if update.message.from_user.id not in ADMIN_IDS:
        return
    if len(context.args) < 2:
        return update.message.reply_text("Usage: /reply <uid> <message>")
    uid = context.args[0]
    msg = " ".join(context.args[1:])
    context.bot.send_message(chat_id=uid, text=msg)
    update.message.reply_text("Replied ✅")


# ---------- Points + Accounts ----------
def add_points(update: Update, context: CallbackContext):
    if update.message.from_user.id not in ADMIN_IDS:
        return
    if len(context.args) < 2:
        return update.message.reply_text("Usage: /add_points <uid> <points>")
    uid, pts = context.args[0], int(context.args)
    points = load_json(POINTS_FILE)
    points[uid] = points.get(uid, 0) + pts
    save_json(POINTS_FILE, points)
    context.bot.send_message(chat_id=uid, text=f"Points added: {pts}, Total: {points[uid]}")
    update.message.reply_text("Points updated ✅")


def add_accounts(update: Update, context: CallbackContext):
    if update.message.from_user.id not in ADMIN_IDS:
        return
    accs = load_json(ACCOUNTS_FILE)
    for arg in context.args:
        if ":" not in arg:
            continue
        email, pwd = arg.split(":", 1)
        accs[email] = {"password": pwd, "count": 0}
    save_json(ACCOUNTS_FILE, accs)
    update.message.reply_text("Accounts Added ✅")


def acc(update: Update, context: CallbackContext):
    uid = str(update.message.from_user.id)
    context.bot.send_message(chat_id=uid, text="Please Confirm Purchase 🤳 (send /confirm)")


def confirm(update: Update, context: CallbackContext):
    uid = str(update.message.from_user.id)
    points = load_json(POINTS_FILE)
    accs = load_json(ACCOUNTS_FILE)
    if points.get(uid, 0) < 5:
        return update.message.reply_text("Not Enough Points 🪡")

    for email, data in accs.items():
        if data["count"] < 2:
            data["count"] += 1
            save_json(ACCOUNTS_FILE, accs)
            points[uid] -= 5
            save_json(POINTS_FILE, points)
            return update.message.reply_text(
                f"Aᴄᴄᴏᴜɴᴛ Wɪᴛʜᴅʀᴀᴡʟ 🌐\n\n"
                f"✉ Email: {email}\n"
                f"🔑 Password: {data['password']}\n"
                f"🛒 Service: Amazon\n\n"
                f"Thanks For Purchase 😊"
            )
    update.message.reply_text("No Accounts Available ❌")


def stock(update: Update, context: CallbackContext):
    if update.message.from_user.id not in ADMIN_IDS:
        return
    accs = load_json(ACCOUNTS_FILE)
    cnt = sum(1 for acc in accs.values() if acc["count"] < 2)
    update.message.reply_text(f"Stock Available: {cnt} accounts")


# ---------- Flask ----------
@app.route('/')
def index():
    return "Bot Running..."


# ---------- Main ----------
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("redeem", redeem))
    dp.add_handler(CommandHandler("premium", premium))
    dp.add_handler(CommandHandler("genk", genk))
    dp.add_handler(CommandHandler("broadcast", broadcast))
    dp.add_handler(CommandHandler("approved", approved))
    dp.add_handler(CommandHandler("failed", failed))
    dp.add_handler(CommandHandler("on", on))
    dp.add_handler(CommandHandler("off", off))
    dp.add_handler(CommandHandler("reply", reply))
    dp.add_handler(CommandHandler("add_points", add_points))
    dp.add_handler(CommandHandler("add_accounts", add_accounts))
    dp.add_handler(CommandHandler("acc", acc))
    dp.add_handler(CommandHandler("confirm", confirm))
    dp.add_handler(CommandHandler("stock", stock))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
