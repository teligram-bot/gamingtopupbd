# -*- coding: utf-8 -*-
import telebot
from telebot import types
import json
import os

TOKEN = '7688861803:AAFUu3Br4kDckYy1SAtWQFFCqDt8Fy0vIo8'
ADMIN_ID =   # Replace with your Telegram ID
ADMIN_BKASH_NO = '01883020171'
DATA_FILE = 'users.json'

bot = telebot.TeleBot(TOKEN)

# Load or initialize data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        users = json.load(f)
else:
    users = {}

# Save data function
def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f)

def home_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("\ud83d\udce4 Gmail Sell", "\ud83d\udce5 Gmail Buy")
    markup.add("\ud83d\udcb3 Balance", "\ud83d\udcb5 Withdraw")
    markup.add("\ud83c\udf10 Paid VPN Buy", "\ud83c\udfa5 YouTube Premium")
    markup.add("\ud83d\udc65 Refer", "\ud83d\ude98 Track Order", "\ud83d\ude98 Support")
    bot.send_message(chat_id, "\ud83c\udfe0 হোম মেনুতে স্বাগতম!", reply_markup=markup)

def back_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("\ud83d\udd19 Back")
    return markup

# /start command with referral
def register_user(user, ref=None):
    uid = str(user.id)
    if uid not in users:
        users[uid] = {
            "username": user.username,
            "balance": 0,
            "hold": 0,
            "ref": ref if ref and str(ref) != uid else None,
            "ref_count": 0
        }
        if ref and str(ref) != uid:
            users[str(ref)]["balance"] += 2
            users[str(ref)]["ref_count"] += 1
        save_data()

@bot.message_handler(commands=['start'])
def start(message):
    parts = message.text.split()
    ref = parts[1] if len(parts) > 1 else None
    register_user(message.from_user, ref)
    home_menu(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "\ud83d\udd19 Back")
def back_to_home(message):
    home_menu(message.chat.id)

# Gmail Sell
@bot.message_handler(func=lambda m: m.text == "\ud83d\udce4 Gmail Sell")
def gmail_sell(message):
    msg = bot.send_message(message.chat.id, "\ud83d\udce7 Gmail/Password দিন (example@gmail.com/pass):", reply_markup=back_markup())
    bot.register_next_step_handler(msg, process_gmail)

def process_gmail(message):
    if message.text == "\ud83d\udd19 Back":
        return home_menu(message.chat.id)

    uid = str(message.from_user.id)
    users[uid]["gmail"] = message.text
    users[uid]["gmail_step"] = "confirm"
    save_data()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("\u2705 Confirm Gmail", "\ud83d\udd19 Back")
    bot.send_message(message.chat.id, f"আপনি দিয়েছেন:\n`{message.text}`\n\n✅ নিশ্চিত করতে 'Confirm Gmail' চাপুন।", parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "\u2705 Confirm Gmail")
def confirm_gmail(message):
    uid = str(message.from_user.id)
    if users.get(uid, {}).get("gmail_step") != "confirm":
        return home_menu(message.chat.id)

    gmail_info = users[uid]["gmail"]
    users[uid]["hold"] += 8
    users[uid].pop("gmail_step", None)
    save_data()

    bot.send_message(uid, "✅ Gmail যাচাই হচ্ছে... Hold Balance-এ ৮ টাকা যোগ হয়েছে।")
    username = message.from_user.username or "NoUsername"
    bot.send_message(ADMIN_ID, f"🆕 Gmail Sell:\n👤 @{username} ({uid})\n📧 {gmail_info}")

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"approve_{uid}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{uid}")
    )
    bot.send_message(ADMIN_ID, "⏳ Approve না Reject?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve") or call.data.startswith("reject"))
def handle_admin_action(call):
    action, uid = call.data.split("_")
    if uid not in users:
        return
    uid = str(uid)
    if action == "approve":
        users[uid]["balance"] += 8
        users[uid]["hold"] -= 8
        bot.send_message(uid, "✅ আপনার Gmail Approved হয়েছে। ৮ টাকা Main Balance-এ যোগ হয়েছে।")
    else:
        users[uid]["hold"] -= 8
        bot.send_message(uid, "❌ Gmail Reject হয়েছে। Hold থেকে টাকা কেটে নেওয়া হয়েছে।")
    save_data()

# Gmail Buy
@bot.message_handler(func=lambda m: m.text == "\ud83d\udce5 Gmail Buy")
def gmail_buy(message):
    msg = bot.send_message(message.chat.id, "📦 কতটি Gmail কিনবেন?", reply_markup=back_markup())
    bot.register_next_step_handler(msg, process_gmail_qty)

def process_gmail_qty(message):
    if message.text == "\ud83d\udd19 Back":
        return home_menu(message.chat.id)
    try:
        qty = int(message.text)
        users[str(message.from_user.id)]["buy_qty"] = qty
        save_data()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("\ud83d\udcf2 Bkash", "\ud83d\udcf2 Nagad", "\ud83d\udd19 Back")
        bot.send_message(message.chat.id, f"{qty} টি Gmail এর দাম {qty * 10} টাকা। পেমেন্ট মাধ্যম বাছুন:", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "❌ সঠিক সংখ্যা লিখুন", reply_markup=back_markup())

@bot.message_handler(func=lambda m: m.text in ["📲 Bkash", "📲 Nagad"])
def gmail_payment(message):
    uid = str(message.from_user.id)
    users[uid]["payment_method"] = message.text
    save_data()
    msg = bot.send_message(message.chat.id, f"💳 {message.text} এ টাকা পাঠান: {ADMIN_BKASH_NO}\n📨 তারপর Transaction ID দিন:", reply_markup=back_markup())
    bot.register_next_step_handler(msg, confirm_gmail_buy)

def confirm_gmail_buy(message):
    uid = str(message.from_user.id)
    user = users[uid]
    username = message.from_user.username or "NoUsername"
    qty = user.get("buy_qty", 0)
    method = user.get("payment_method", "N/A")
    trx = message.text

    bot.send_message(ADMIN_ID, f"🛒 Gmail Buy:\n👤 @{username} ({uid})\nQty: {qty}\nMethod: {method}\nTxn: {trx}")
    bot.send_message(message.chat.id, "✅ অর্ডার কনফার্ম। Admin যাচাই করে Gmail পাঠাবেন।")

# Remaining sections: VPN Buy, YouTube Premium, Withdraw, Refer, etc.
# You can ask me to continue with the rest

print("🤖 Bot is running...")
bot.infinity_polling()
