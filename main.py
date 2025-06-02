import telebot
from telebot import types

TOKEN = '7688861803:AAFUu3Br4kDckYy1SAtWQFFCqDt8Fy0vIo8'
ADMIN_ID = 7004140373
ADMIN_BKASH_NO = '01883020171'

bot = telebot.TeleBot(TOKEN)
users = {}

def home_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📤 Gmail Sell", "📥 Gmail Buy")
    markup.add("💳 Balance", "💵 Withdraw")
    markup.add("🌐 Paid VPN Buy", "🎥 YouTube Premium")
    markup.add("👥 Refer", "🆘 Support")
    bot.send_message(chat_id, "🏠 হোম মেনুতে স্বাগতম!", reply_markup=markup)

def back_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔙 Back")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    users.setdefault(message.from_user.id, {
        "username": message.from_user.username,
        "balance": 0,
        "hold": 0
    })
    home_menu(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "🔙 Back")
def back_to_home(message):
    home_menu(message.chat.id)

# Gmail Sell Section
@bot.message_handler(func=lambda m: m.text == "📤 Gmail Sell")
def gmail_sell(message):
    users.setdefault(message.from_user.id, {"balance": 0, "hold": 0})
    msg = bot.send_message(message.chat.id, "📧 Gmail/Password দিন (example@gmail.com/password):", reply_markup=back_markup())
    bot.register_next_step_handler(msg, process_gmail)

def process_gmail(message):
    if message.text == "🔙 Back":
        return home_menu(message.chat.id)
    
    users[message.from_user.id]["gmail"] = message.text
    users[message.from_user.id]["gmail_step"] = "confirm"
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✅ Confirm Gmail", "🔙 Back")
    bot.send_message(message.chat.id, f"আপনি দিয়েছেন:\n`{message.text}`\n\n✅ নিশ্চিত করতে 'Confirm Gmail' চাপুন।", parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "✅ Confirm Gmail")
def confirm_gmail(message):
    user_id = message.from_user.id
    if users.get(user_id, {}).get("gmail_step") != "confirm":
        return home_menu(message.chat.id)
    
    gmail_info = users[user_id]["gmail"]
    users[user_id]["hold"] += 8
    
    bot.send_message(user_id, "✅ Gmail যাচাই হচ্ছে... Hold Balance-এ ৮ টাকা যোগ হয়েছে।")
    
    username = message.from_user.username or "NoUsername"
    bot.send_message(ADMIN_ID, f"🆕 Gmail Sell:\n👤 @{username} ({user_id})\n📧 {gmail_info}")
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
    )
    bot.send_message(ADMIN_ID, "⏳ Approve না Reject?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith(("approve_", "reject_")))
def handle_admin_response(call):
    user_id = int(call.data.split("_")[1])
    action = call.data.split("_")[0]
    
    if action == "approve":
        users[user_id]["hold"] -= 8
        users[user_id]["balance"] += 8
        bot.send_message(user_id, "✅ আপনার Gmail Approved হয়েছে। ৮ টাকা Main Balance-এ যোগ হয়েছে।")
    else:
        users[user_id]["hold"] -= 8
        bot.send_message(user_id, "❌ Gmail Reject হয়েছে। Hold থেকে টাকা কেটে নেওয়া হয়েছে।")

# Gmail Buy Section
@bot.message_handler(func=lambda m: m.text == "📥 Gmail Buy")
def gmail_buy(message):
    msg = bot.send_message(message.chat.id, "📦 কতটি Gmail কিনবেন?", reply_markup=back_markup())
    bot.register_next_step_handler(msg, process_gmail_qty)

def process_gmail_qty(message):
    if message.text == "🔙 Back":
        return home_menu(message.chat.id)
    
    try:
        qty = int(message.text)
        total_price = qty * 10
        users[message.from_user.id]["buy_qty"] = qty
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📲 Bkash", "📲 Nagad", "🔙 Back")
        bot.send_message(message.chat.id, f"{qty} টি Gmail এর দাম {total_price} টাকা। পেমেন্ট মাধ্যম বাছুন:", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "❌ সঠিক সংখ্যা লিখুন", reply_markup=back_markup())

@bot.message_handler(func=lambda m: m.text in ["📲 Bkash", "📲 Nagad"])
def gmail_payment(message):
    users[message.from_user.id]["payment_method"] = message.text
    msg = bot.send_message(message.chat.id, f"💳 {message.text} এ টাকা পাঠান: {ADMIN_BKASH_NO}\n📨 তারপর Transaction ID দিন:", reply_markup=back_markup())
    bot.register_next_step_handler(msg, confirm_gmail_buy)

def confirm_gmail_buy(message):
    user = users[message.from_user.id]
    username = message.from_user.username or "NoUsername"
    qty = user.get("buy_qty", 0)
    method = user.get("payment_method", "N/A")
    trx = message.text

    bot.send_message(ADMIN_ID, f"🛒 Gmail Buy:\n👤 @{username} ({message.from_user.id})\nQty: {qty}\nMethod: {method}\nTxn: {trx}")
    bot.send_message(message.chat.id, "✅ অর্ডার কনফার্ম। Admin যাচাই করে Gmail পাঠাবেন।")

# VPN Section
@bot.message_handler(func=lambda m: m.text == "🌐 Paid VPN Buy")
def vpn_buy(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("NordVPN 7 Days", "ExpressVPN 7 Days", "🔙 Back")
    bot.send_message(message.chat.id, "VPN নির্বাচন করুন (৭ দিন = ৩০ টাকা):", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text.endswith("7 Days"))
def vpn_selected(message):
    users[message.from_user.id]["vpn"] = message.text
    msg = bot.send_message(message.chat.id, f"{message.text}\n📲 টাকা পাঠান: {ADMIN_BKASH_NO}\nতারপর Transaction ID দিন:", reply_markup=back_markup())
    bot.register_next_step_handler(msg, vpn_confirm)

def vpn_confirm(message):
    vpn = users[message.from_user.id]["vpn"]
    username = message.from_user.username or "NoUsername"
    bot.send_message(ADMIN_ID, f"🔐 VPN Order:\n👤 @{username} ({message.from_user.id})\nVPN: {vpn}\nTxn ID: {message.text}")
    bot.send_message(message.chat.id, "✅ অর্ডার কনফার্ম। Admin যাচাই করে VPN পাঠাবেন।")

# YouTube Premium Section
@bot.message_handler(func=lambda m: m.text == "🎥 YouTube Premium")
def yt_premium(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("1 Month (25TK)", "1 Year (150TK)", "🔙 Back")
    bot.send_message(message.chat.id, "📺 YouTube Premium প্যাকেজ নির্বাচন করুন:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text.startswith("1 "))
def yt_selected(message):
    users[message.from_user.id]["yt_plan"] = message.text
    msg = bot.send_message(message.chat.id, f"{message.text}\n📲 টাকা পাঠান: {ADMIN_BKASH_NO}\nতারপর Transaction ID দিন:", reply_markup=back_markup())
    bot.register_next_step_handler(msg, yt_confirm)

def yt_confirm(message):
    yt_plan = users[message.from_user.id]["yt_plan"]
    username = message.from_user.username or "NoUsername"
    bot.send_message(ADMIN_ID, f"📺 YouTube Premium:\n👤 @{username} ({message.from_user.id})\nPlan: {yt_plan}\nTxn ID: {message.text}")
    bot.send_message(message.chat.id, "✅ অর্ডার কনফার্ম। Admin যাচাই করে Gmail পাঠাবেন।")

# Balance Section
@bot.message_handler(func=lambda m: m.text == "💳 Balance")
def balance(message):
    user = users.get(message.from_user.id, {"balance": 0, "hold": 0})
    bot.send_message(message.chat.id, f"💰 Balance: {user['balance']} টাকা\n⏳ Hold: {user['hold']} টাকা", reply_markup=back_markup())

# Withdraw Section
@bot.message_handler(func=lambda m: m.text == "💵 Withdraw")
def withdraw(message):
    msg = bot.send_message(message.chat.id, "📤 কত টাকা তুলবেন?", reply_markup=back_markup())
    bot.register_next_step_handler(msg, withdraw_amount)

def withdraw_amount(message):
    try:
        amount = int(message.text)
        if amount < 25:
            return bot.send_message(message.chat.id, "❌ মিনিমাম ২৫ টাকা লাগবে।", reply_markup=back_markup())
        
        users[message.from_user.id]["withdraw_amount"] = amount
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Bkash", "Nagad", "🔙 Back")
        bot.send_message(message.chat.id, "🔰 পেমেন্ট মাধ্যম বেছে নিন:", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "❌ সংখ্যা লিখুন!", reply_markup=back_markup())

@bot.message_handler(func=lambda m: m.text in ["Bkash", "Nagad"])
def withdraw_method(message):
    users[message.from_user.id]["withdraw_method"] = message.text
    msg = bot.send_message(message.chat.id, f"📞 {message.text} নাম্বার দিন:", reply_markup=back_markup())
    bot.register_next_step_handler(msg, confirm_withdraw)

def confirm_withdraw(message):
    user = users[message.from_user.id]
    username = message.from_user.username or "NoUsername"
    bot.send_message(ADMIN_ID, f"💵 Withdraw:\n👤 @{username} ({message.from_user.id})\nAmount: {user['withdraw_amount']}\nMethod: {user['withdraw_method']}\nNumber: {message.text}")
    bot.send_message(message.chat.id, "✅ Withdraw অনুরোধ Admin এর কাছে পাঠানো হয়েছে।")

# Refer and Support
@bot.message_handler(func=lambda m: m.text == "👥 Refer")
def refer(message):
    link = f"https://t.me/YOUR_BOT_USERNAME?start={message.from_user.id}"
    bot.send_message(message.chat.id, f"🔗 আপনার রেফার লিঙ্ক:\n{link}", reply_markup=back_markup())

@bot.message_handler(func=lambda m: m.text == "🆘 Support")
def support(message):
    bot.send_message(message.chat.id, "📞 যোগাযোগ করুন: @Riyadbd71", reply_markup=back_markup())

print("🤖 Bot is running...")
bot.infinity_polling()
