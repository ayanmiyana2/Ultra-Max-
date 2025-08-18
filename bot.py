import telebot, time
from telebot.types import (
    ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
)
from config import TOKEN, ADMIN_ID
from utils.database import load_data, save_data
from utils.key_manager import generate_key, validate_key, is_premium

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Redeem ⚡", "Premium 🗝️")
    markup.add("Buy Key 🛒", "Support 📩")
    return markup

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "Welcome To Aizen Bot ⚡️\nPlease Use this /redeem Command For Get Prime video 🧑‍💻\nFor Premium use This Command /premium",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda m: m.text == "Redeem ⚡")
def redeem_button(msg):
    redeem(msg)
@bot.message_handler(func=lambda m: m.text == "Premium 🗝️")
def premium_button(msg):
    bot.send_message(msg.chat.id, "Premium lene ke liye /premium <key> likhein.")

@bot.message_handler(func=lambda m: m.text == "Buy Key 🛒")
def buy_button(msg):
    bot.send_message(msg.chat.id, "Admin ko request bheji gayi! Jaldi contact karega.")
    bot.send_message(ADMIN_ID, f"User @{msg.from_user.username} ({msg.from_user.id}) wants to Buy Premium Key!")

@bot.message_handler(func=lambda m: m.text == "Support 📩")
def support_button(msg):
    bot.send_message(msg.chat.id, "Yahan apna message bhejiye. Admin aapko reply karega.")

@bot.message_handler(commands=['redeem'])
def redeem(msg):
    data = load_data()
    uid = str(msg.from_user.id)
    if uid in data["banned"]:
        return bot.send_message(msg.chat.id, "⛔ You are banned by Admin.")
    if not is_premium(uid):
        if not data["free_mode"]:
            if data["redeem_used"].get(uid, False):
                return bot.send_message(msg.chat.id, "Please Purchase Premium Key For Use 🗝️")
            data["redeem_used"][uid] = True
            save_data(data)
    bot.send_message(msg.chat.id, "After /redeem Enter Your Account To Activate Premium ⚡️")

# ----- After /redeem: User message is treat as redeem request -----
@bot.message_handler(func=lambda m: True, content_types=['text'])
def after_redeem(msg):
    if msg.text.startswith("/"): return  # skip commands  
    data = load_data()
    uid = str(msg.from_user.id)
    # pending redeem store
    if msg.text in ("Redeem ⚡", "Premium 🗝️", "Buy Key 🛒", "Support 📩"): return
    if "pending_redeem" not in data: data["pending_redeem"] = {}
    # Only after redeem
    if not data["pending_redeem"].get(uid):
        data["pending_redeem"][uid] = {"text": msg.text}
        save_data(data)
        # Send to admin
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{uid}"),
            InlineKeyboardButton("❌ Failed", callback_data=f"fail_{uid}")
        )
        plan = "Premium" if is_premium(uid) else "Free"
        msgtext = (
            f"(╔═══━─༺༻─━═══╗ \n"
            f"   ♛  New Order Done  ♛ \n"
            f"╚═══━─༺༻─━═══╝ \n"
            f"༺🌸 New Redeem  🌸༻\n\n"
            f"👤 Name :⫸ {msg.from_user.first_name}\n"
            f"✉️ Username :⫸ @{msg.from_user.username}\n"
            f"🆔 UserID :⫸ {uid}\n"
            f"👑 User Plan :⫸ {plan}\n\n"
            f"⚡ Secure Service ⚡\n"
            f"--\nUser's msg: {msg.text}"
        )
        bot.send_message(ADMIN_ID, msgtext, reply_markup=markup)
        bot.send_message(msg.chat.id, "Processing...")

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_") or call.data.startswith("fail_"))
def handle_redeem_admin_decision(call):
    data = load_data()
    act, uid = call.data.split("_")
    uid = str(uid)
    if act == "approve_":
        # Inform user
        bot.send_message(uid, "Successfully Done ⚡️")
        # Broadcast to all
        to_broadcast = (
            f"(╔═══━─༺༻─━═══╗ \n"
            f"   ♛  New Order Done  ♛ \n"
            f"╚═══━─༺༻─━═══╝ \n"
            f"༺🌸 New Redeem  🌸༻\n\n"
            f"👤 Name :⫸ {call.from_user.first_name}\n"
            f"✉️ Username :⫸ @{call.from_user.username}\n"
            f"🆔 UserID :⫸ {uid}\n"
            f"👑 User Plan :⫸ {'Premium' if is_premium(uid) else 'Free'}\n\n"
            f"⚡ Secure Service ⚡"
        )
        for u in (list(data["premium_users"].keys()) + list(data["redeem_used"].keys())):
            try:
                bot.send_message(u, to_broadcast)
            except:
                continue
    else:
        bot.send_message(uid, "Failed For Some Technical issues 🧑‍💻")
    # Clean
    if data["pending_redeem"].get(uid):
        del data["pending_redeem"][uid]
        save_data(data)
    bot.answer_callback_query(call.id, "Done")

@bot.message_handler(commands=['premium'])
def premium(msg):
    parts = msg.text.split()
    if len(parts) < 2:
        return bot.send_message(msg.chat.id, "Usage: /premium <key>")
    key = parts[1]
    ok = validate_key(msg.from_user.id, key)
    if ok:
        bot.send_message(msg.chat.id, "Premium Activated ⚡️")
        bot.send_message(ADMIN_ID, f"User @{msg.from_user.username} ({msg.from_user.id}) got Premium ✅")
    else:
        bot.send_message(msg.chat.id, "Invalid or Used Key ❌")

# =========== ADMIN COMMANDS ===========
@bot.message_handler(commands=['genk'])
def genk(msg):
    if msg.from_user.id != ADMIN_ID: return
    try:
        days = int(msg.text.split()[1])
        key = generate_key(days)
        bot.send_message(msg.chat.id, f"Key generated: <code>{key}</code> valid {days} days")
    except:
        bot.send_message(msg.chat.id, "Usage: /genk <days>")

@bot.message_handler(commands=['broadcast'])
def broadcast(msg):
    if msg.from_user.id != ADMIN_ID: return
    text = msg.text.replace("/broadcast", "").strip()
    if not text: return
    data = load_data()
    for uid in set(list(data["premium_users"].keys()) + list(data["redeem_used"].keys())):
        try: bot.send_message(uid, text)
        except: pass

@bot.message_handler(commands=['ban'])
def ban(msg):
    if msg.from_user.id != ADMIN_ID: return
    uid = msg.text.split()[1]
    data = load_data()
    if uid not in data["banned"]:
        data["banned"].append(uid)
        save_data(data)
    bot.send_message(msg.chat.id, f"User {uid} banned.")

@bot.message_handler(commands=['unban'])
def unban(msg):
    if msg.from_user.id != ADMIN_ID: return
    uid = msg.text.split()
    data = load_data()
    if uid in data["banned"]:
        data["banned"].remove(uid)
        save_data(data)
    bot.send_message(msg.chat.id, f"User {uid} unbanned.")

@bot.message_handler(commands=['on'])
def free_on(msg):
    if msg.from_user.id != ADMIN_ID: return
    data = load_data()
    data["free_mode"] = True
    save_data(data)
    bot.send_message(msg.chat.id, "Free Service On time ⚡️")

@bot.message_handler(commands=['off'])
def free_off(msg):
    if msg.from_user.id != ADMIN_ID: return
    data = load_data()
    data["free_mode"] = False
    save_data(data)
    bot.send_message(msg.chat.id, "Free Service Off ♻️")

@bot.message_handler(commands=['reply'])
def admin_reply(msg):
    if msg.from_user.id != ADMIN_ID: return
    try:
        parts = msg.text.split()
        uid = parts[1]
        reply = " ".join(parts[2:])
        bot.send_message(uid, reply)
    except:
        bot.send_message(msg.chat.id, "Usage: /reply <userid> <msg>")

# ========= ACCOUNTS + POINTS ============
@bot.message_handler(commands=['add_accounts'])
def add_accounts(msg):
    if msg.from_user.id != ADMIN_ID: return
    # /add_accounts email:pass:service
    try:
        arr = msg.text.split()[1:]
        data = load_data()
        for a in arr:
            email, password, service = a.split(":")
            data["accounts"].append({
                "email": email,
                "password": password,
                "service": service,
                "used_by": []
            })
        save_data(data)
        bot.send_message(msg.chat.id, f"Accounts Added.")
    except:
        bot.send_message(msg.chat.id, "Usage: /add_accounts email:pass:service ...")

@bot.message_handler(commands=['add_points'])
def add_points(msg):
    if msg.from_user.id != ADMIN_ID: return
    try:
        _, uid, pts = msg.text.split()
        data = load_data()
        data["points"][uid] = data["points"].get(uid, 0) + int(pts)
        save_data(data)
        bot.send_message(msg.chat.id, "Points Added.")
    except:
        bot.send_message(msg.chat.id, "Usage: /add_points <userid> <points>")

@bot.message_handler(commands=['stock'])
def stock(msg):
    if msg.from_user.id != ADMIN_ID: return
    data = load_data()
    stock = sum(1 for a in data["accounts"] if len(a["used_by"]) < 2)
    bot.send_message(msg.chat.id, f"Stock: {stock} accounts available.")

@bot.message_handler(commands=['acc'])
def acc(msg):
    data = load_data()
    uid = str(msg.from_user.id)
    if data["points"].get(uid, 0) < 5:
        return bot.send_message(msg.chat.id, "Not Enough Points 🪡")
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Please Confirm Purchase 🤳", callback_data=f"acc_confirm_{uid}"))
    bot.send_message(msg.chat.id, "Please Confirm Purchase 🤳", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("acc_confirm_"))
def confirm_acc(call):
    data = load_data()
    uid = call.data.split("_")[-1]
    found = None
    for acc in data["accounts"]:
        if uid not in acc["used_by"] and len(acc["used_by"]) < 2:
            found = acc
            acc["used_by"].append(uid)
            break
    if found:
        data["points"][uid] = data["points"].get(uid, 0) - 5
        save_data(data)
        msgtxt = (
            "Aᴄᴄᴏᴜɴᴛ Wɪᴛʜᴅʀᴀᴡʟ 🌐\n\n"
            f"✉ Eᴍᴀɪʟ: {found['email']}\n"
            f"Password : {found['password']}\n"
            f"🛒 Sᴇʀᴠɪᴄᴇ: {found['service']}\n\n"
            "Thanks For Purchase 😊"
        )
        bot.send_message(uid, msgtxt)
    else:
        bot.send_message(uid, "Stock is empty! Wait for new accounts.")

def run_bot():
    bot.infinity_polling()
