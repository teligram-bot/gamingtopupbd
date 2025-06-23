import telebot
from telebot import types

TOKEN = '7688861803:AAFUu3Br4kDckYy1SAtWQFFCqDt8Fy0vIo8'
ADMIN_ID = '7004140373'
ADMIN_BKASH_NO = '01883020171'
BOT_USERNAME = "digitalbuysellbdbot"

bot = telebot.TeleBot(TOKEN)
users = {}
pending_gmails = {}

# Changed logo to BD
LOGO = """
██████╗ ██████╗ 
██╔══██╗██╔══██╗
██████╔╝██║  ██║
██╔══██╗██║  ██║
██████╔╝██████╔╝
╚═════╝ ╚═════╝ 

Digital Buy Sell BD Bot
"""

def home_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "📤 Gmail Sell", "📥 Gmail Buy",
        "💳 Balance", "💵 Withdraw",
        "🌐 Paid VPN Buy", "🎥 YouTube Premium",
        "👥 Refer", "🆘 Support"
    ]
    markup.add(*buttons)
    bot.send_message(chat_id, "🏠 হোম মেনুতে স্বাগতম!", reply_markup=markup)

def back_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔙 Back")
    return markup

def payment_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📲 Bkash", "📲 Nagad", "🔙 Back")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, LOGO)

    if len(message.text.split()) > 1:
        referrer_id = message.text.split()[1]
        try:
            referrer_id = int(referrer_id)
            if referrer_id in users and referrer_id != message.from_user.id:
                users[referrer_id]["balance"] += 2
                users[referrer_id]["referral_count"] += 1
                bot.send_message(referrer_id, f"🎉 আপনি ২ টাকা পেয়েছেন রেফার বোনাস হিসেবে! নতুন ইউজার: @{message.from_user.username or 'NoUsername'}")
        except ValueError:
            pass

    users.setdefault(message.from_user.id, {
        "username": message.from_user.username,
        "balance": 0,
        "hold": 0,
        "referral_count": 0
    })

    welcome_msg = """
🎉 স্বাগতম আমাদের ডিজিটাল সার্ভিসে!

🔹 Gmail বিক্রি/ক্রয়
🔹 VPN সার্ভিস
🔹 YouTube Premium
🔹 রেফার প্রোগ্রাম

💰 আপনার ব্যালেন্স: ০ টাকা
👥 রেফার্ড ইউজার: ০ জন

নিচের মেনু থেকে সেবা নির্বাচন করুন:
"""
    home_menu(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "🔙 Back")
def back_to_home(message):
    home_menu(message.chat.id)

# Gmail Sell Section
@bot.message_handler(func=lambda m: m.text == "📤 Gmail Sell")
def gmail_sell(message):
    msg = bot.send_message(message.chat.id, "📧 বিক্রির জন্য Gmail আইডি দিন (ফরম্যাট: example@gmail.com:password):", reply_markup=back_markup())
    bot.register_next_step_handler(msg, process_gmail)

def process_gmail(message):
    if message.text == "🔙 Back":
        return home_menu(message.chat.id)

    if ":" not in message.text or "@" not in message.text:
        msg = bot.send_message(message.chat.id, "❌ ভুল ফরম্যাট! সঠিক ফরম্যাটে দিন (example@gmail.com:password):", reply_markup=back_markup())
        bot.register_next_step_handler(msg, process_gmail)
        return

    user_id = message.from_user.id
    pending_gmails[user_id] = message.text
    users[user_id]["hold"] += 8

    bot.send_message(message.chat.id, "✅ Gmail জমা দেওয়া হয়েছে! Admin চেক করে টাকা দিবেন। আপনার ৮ টাকা হোল্ড করা হয়েছে।")

    username = message.from_user.username or "NoUsername"
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
    )
    bot.send_message(ADMIN_ID, f"📧 নতুন Gmail:\n👤 @{username}\nID: {user_id}\n\n{message.text}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if str(call.from_user.id) != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ অনুমতি denied!")
        return

    data = call.data.split('_')
    action = data[0]
    user_id = int(data[1])

    if action == "approve":
        if user_id in pending_gmails:
            gmail = pending_gmails[user_id]
            users[user_id]["hold"] -= 8
            users[user_id]["balance"] += 8
            bot.send_message(user_id, f"✅ আপনার Gmail অনুমোদিত হয়েছে! ৮ টাকা যোগ করা হয়েছে।\nGmail: {gmail}")
            del pending_gmails[user_id]
            bot.answer_callback_query(call.id, "✅ Approved")

    elif action == "reject":
        if user_id in pending_gmails:
            users[user_id]["hold"] -= 8
            bot.send_message(user_id, "❌ আপনার Gmail রিজেক্ট হয়েছে! ৮ টাকা হোল্ড থেকে সরানো হয়েছে।")
            del pending_gmails[user_id]
            bot.answer_callback_query(call.id, "❌ Rejected")

    elif action == "pay":
        amount = int(data[2])
        users[user_id]["hold"] -= amount
        bot.send_message(user_id, f"✅ আপনার উত্তোলনের অনুরোধ অনুমোদিত হয়েছে! {amount} TK পাঠানো হয়েছে।")
        bot.answer_callback_query(call.id, "✅ Payment sent")
    
    elif action == "deliver":
        service = data[1]
        if service == "gmail":
            quantity = users[user_id].get("gmail_quantity", 1)
            gmail_type = users[user_id].get("gmail_type", "Gmail")
            bot.send_message(ADMIN_ID, f"📩 User {user_id} কে {quantity}টি {gmail_type} পাঠান:\n\n/delivery_{user_id}")
        elif service == "vpn":
            vpn = users[user_id].get("vpn", "VPN")
            bot.send_message(ADMIN_ID, f"📩 User {user_id} কে {vpn} পাঠান:\n\n/delivery_{user_id}")
        elif service == "yt":
            yt_plan = users[user_id].get("yt_plan", "YouTube Premium")
            bot.send_message(ADMIN_ID, f"📩 User {user_id} কে {yt_plan} পাঠান:\n\n/delivery_{user_id}")
        bot.answer_callback_query(call.id, "✅ Delivery instructions sent")

# Gmail Buy Section
@bot.message_handler(func=lambda m: m.text == "📥 Gmail Buy")
def gmail_buy(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🇺🇸 USA Gmail (15TK)", "🇧🇩 BD Gmail (10TK)", "🔙 Back")
    bot.send_message(message.chat.id, "🎯 Gmail টাইপ নির্বাচন করুন:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["🇺🇸 USA Gmail (15TK)", "🇧🇩 BD Gmail (10TK)"])
def select_gmail_type(message):
    users[message.from_user.id]["gmail_type"] = message.text
    msg = bot.send_message(message.chat.id, "🔢 কতগুলো Gmail চান? (সংখ্যা লিখুন):", reply_markup=back_markup())
    bot.register_next_step_handler(msg, process_gmail_quantity)

def process_gmail_quantity(message):
    if message.text == "🔙 Back":
        return home_menu(message.chat.id)

    try:
        quantity = int(message.text)
        if quantity <= 0:
            raise ValueError

        user_id = message.from_user.id    
        users[user_id]["gmail_quantity"] = quantity    
        gmail_type = users[user_id]["gmail_type"]    
        
        price = 15 * quantity if "USA" in gmail_type else 10 * quantity    
        users[user_id]["gmail_price"] = price    
        
        bot.send_message(message.chat.id,     
                        f"📝 অর্ডার সারাংশ:\n\n{gmail_type}\nপরিমাণ: {quantity}\nমোট মূল্য: {price} TK\n\nপেমেন্ট মাধ্যম:",     
                        reply_markup=payment_markup())

    except:
        msg = bot.send_message(message.chat.id, "❌ অবৈধ সংখ্যা! শুধুমাত্র সংখ্যা লিখুন:", reply_markup=back_markup())
        bot.register_next_step_handler(msg, process_gmail_quantity)

@bot.message_handler(func=lambda m: m.text in ["📲 Bkash", "📲 Nagad"] and "gmail_price" in users.get(m.from_user.id, {}))
def process_gmail_payment(message):
    user_id = message.from_user.id
    user_data = users[user_id]

    method = "Bkash" if "Bkash" in message.text else "Nagad"
    price = user_data["gmail_price"]
    gmail_type = user_data["gmail_type"]
    quantity = user_data["gmail_quantity"]

    msg = bot.send_message(message.chat.id,
    f"💳 {method} এ টাকা পাঠান: {ADMIN_BKASH_NO}\n"
    f"💰 Amount: {price} TK\n"
    f"📨 Transaction ID লিখুন:",
    reply_markup=back_markup())
    bot.register_next_step_handler(msg, lambda m: confirm_gmail_order(m, method, price, gmail_type, quantity))

def confirm_gmail_order(message, method, price, gmail_type, quantity):
    if message.text == "🔙 Back":
        return home_menu(message.chat.id)

    txn_id = message.text
    user_id = message.from_user.id

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Deliver", callback_data=f"deliver_gmail_{user_id}"))

    bot.send_message(
        ADMIN_ID,
        f"📧 নতুন Gmail অর্ডার:\n\n"
        f"👤 User: @{message.from_user.username or 'N/A'}\n"
        f"🆔 ID: {user_id}\n"
        f"📧 Type: {gmail_type}\n"
        f"🔢 Quantity: {quantity}\n"
        f"💰 Amount: {price} TK\n"
        f"💳 Method: {method}\n"
        f"📝 Txn ID: {txn_id}",
        reply_markup=markup
    )

    bot.send_message(message.chat.id, "✅ আপনার অর্ডার কনফার্ম হয়েছে! Admin ডেলিভারি দিবেন।")
    home_menu(message.chat.id)

# Balance Section
@bot.message_handler(func=lambda m: m.text == "💳 Balance")
def check_balance(message):
    user_id = message.from_user.id
    if user_id in users:
        balance = users[user_id]["balance"]
        hold = users[user_id]["hold"]
        ref_count = users[user_id]["referral_count"]

        msg = f"""
💰 আপনার একাউন্ট বিবরণী:

💵 Available: {balance} TK
⏳ Hold: {hold} TK
👥 Referrals: {ref_count} জন
"""
        bot.send_message(message.chat.id, msg)
    else:
        bot.send_message(message.chat.id, "❌ একাউন্ট খুঁজে পাওয়া যায়নি! /start লিখুন")

# Withdraw Section
@bot.message_handler(func=lambda m: m.text == "💵 Withdraw")
def withdraw(message):
    user_id = message.from_user.id
    if user_id in users:
        balance = users[user_id]["balance"]

        if balance < 50:
            bot.send_message(message.chat.id, f"❌ সর্বনিম্ন উত্তোলন ৫০ টাকা\nআপনার ব্যালেন্স: {balance} TK")
            return

        msg = bot.send_message(message.chat.id, f"💵 উত্তোলনের পরিমাণ লিখুন (৫০-{balance} TK):", reply_markup=back_markup())    
        bot.register_next_step_handler(msg, process_withdraw_amount)

def process_withdraw_amount(message):
    if message.text == "🔙 Back":
        return home_menu(message.chat.id)

    try:
        amount = int(message.text)
        user_id = message.from_user.id
        balance = users[user_id]["balance"]

        if amount < 50:    
            msg = bot.send_message(message.chat.id, "❌ সর্বনিম্ন ৫০ টাকা উত্তোলন করতে পারবেন!", reply_markup=back_markup())    
            bot.register_next_step_handler(msg, process_withdraw_amount)    
            return    
            
        if amount > balance:    
            msg = bot.send_message(message.chat.id, f"❌ আপনার একাউন্টে পর্যাপ্ত টাকা নেই!\nব্যালেন্স: {balance} TK", reply_markup=back_markup())    
            bot.register_next_step_handler(msg, process_withdraw_amount)    
            return    
            
        users[user_id]["balance"] -= amount    
        users[user_id]["hold"] += amount    
        
        msg = bot.send_message(message.chat.id, "📲 উত্তোলনের মাধ্যম নির্বাচন করুন:", reply_markup=payment_markup())    
        bot.register_next_step_handler(msg, lambda m: process_withdraw_method(m, amount))

    except:
        msg = bot.send_message(message.chat.id, "❌ অবৈধ পরিমাণ! শুধুমাত্র সংখ্যা লিখুন:", reply_markup=back_markup())
        bot.register_next_step_handler(msg, process_withdraw_amount)

def process_withdraw_method(message, amount):
    if message.text == "🔙 Back":
        users[message.from_user.id]["balance"] += amount
        users[message.from_user.id]["hold"] -= amount
        return home_menu(message.chat.id)

    method = "Bkash" if "Bkash" in message.text else "Nagad"
    msg = bot.send_message(message.chat.id, f"📱 আপনার {method} নম্বর লিখুন:", reply_markup=back_markup())
    bot.register_next_step_handler(msg, lambda m: complete_withdraw(m, amount, method))

def complete_withdraw(message, amount, method):
    if message.text == "🔙 Back":
        users[message.from_user.id]["balance"] += amount
        users[message.from_user.id]["hold"] -= amount
        return home_menu(message.chat.id)

    number = message.text
    user_id = message.from_user.id

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Pay", callback_data=f"pay_{user_id}_{amount}"))

    bot.send_message(
        ADMIN_ID,
        f"💸 নতুন উত্তোলনের অনুরোধ:\n\n"
        f"👤 User: @{message.from_user.username or 'N/A'}\n"
        f"🆔 ID: {user_id}\n"
        f"💰 Amount: {amount} TK\n"
        f"📱 Method: {method}\n"
        f"📞 Number: {number}",
        reply_markup=markup
    )

    bot.send_message(message.chat.id, "✅ আপনার উত্তোলনের অনুরোধ পাঠানো হয়েছে! Admin অনুমোদন করলে টাকা পাঠানো হবে।")

# VPN Section
@bot.message_handler(func=lambda m: m.text == "🌐 Paid VPN Buy")
def vpn_buy(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("NordVPN 7 Days (30TK)", "ExpressVPN 7 Days (30TK)", "🔙 Back")
    bot.send_message(message.chat.id, "🔒 VPN প্যাকেজ নির্বাচন করুন:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["NordVPN 7 Days (30TK)", "ExpressVPN 7 Days (30TK)"])
def select_vpn(message):
    users[message.from_user.id]["vpn"] = message.text
    bot.send_message(message.chat.id,
    f"📝 অর্ডার সারাংশ:\n\n{message.text}\nমূল্য: 30 TK\n\nপেমেন্ট মাধ্যম:",
    reply_markup=payment_markup())
    bot.register_next_step_handler(message, process_vpn_payment)

def process_vpn_payment(message):
    if message.text == "🔙 Back":
        return home_menu(message.chat.id)

    method = "Bkash" if "Bkash" in message.text else "Nagad"
    msg = bot.send_message(message.chat.id, f"💳 {method} এ টাকা পাঠান: {ADMIN_BKASH_NO}\n📨 Transaction ID লিখুন:", reply_markup=back_markup())
    bot.register_next_step_handler(msg, lambda m: confirm_vpn_order(m, method))

def confirm_vpn_order(message, method):
    if message.text == "🔙 Back":
        return home_menu(message.chat.id)

    txn_id = message.text
    user_id = message.from_user.id
    vpn = users[user_id]["vpn"]

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Deliver", callback_data=f"deliver_vpn_{user_id}"))

    bot.send_message(
        ADMIN_ID,
        f"🔐 নতুন VPN অর্ডার:\n\n"
        f"👤 User: @{message.from_user.username or 'N/A'}\n"
        f"🆔 ID: {user_id}\n"
        f"🔒 VPN: {vpn}\n"
        f"💳 Method: {method}\n"
        f"📝 Txn ID: {txn_id}",
        reply_markup=markup
    )

    bot.send_message(message.chat.id, "✅ আপনার অর্ডার কনফার্ম হয়েছে! Admin ডেলিভারি দিবেন।")
    home_menu(message.chat.id)

# YouTube Premium Section
@bot.message_handler(func=lambda m: m.text == "🎥 YouTube Premium")
def yt_premium(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("1 Month (25TK)", "1 Year (150TK)", "🔙 Back")
    bot.send_message(message.chat.id, "🎬 YouTube Premium প্যাকেজ:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["1 Month (25TK)", "1 Year (150TK)"])
def select_yt_plan(message):
    users[message.from_user.id]["yt_plan"] = message.text
    bot.send_message(message.chat.id,
    f"📝 অর্ডার সারাংশ:\n\n{message.text}\n\nপেমেন্ট মাধ্যম:",
    reply_markup=payment_markup())
    bot.register_next_step_handler(message, process_yt_payment)

def process_yt_payment(message):
    if message.text == "🔙 Back":
        return home_menu(message.chat.id)

    method = "Bkash" if "Bkash" in message.text else "Nagad"
    msg = bot.send_message(message.chat.id, f"💳 {method} এ টাকা পাঠান: {ADMIN_BKASH_NO}\n📨 Transaction ID লিখুন:", reply_markup=back_markup())
    bot.register_next_step_handler(msg, lambda m: confirm_yt_order(m, method))

def confirm_yt_order(message, method):
    if message.text == "🔙 Back":
        return home_menu(message.chat.id)

    txn_id = message.text
    user_id = message.from_user.id
    yt_plan = users[user_id]["yt_plan"]

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Deliver", callback_data=f"deliver_yt_{user_id}"))

    bot.send_message(
        ADMIN_ID,
        f"📺 নতুন YouTube Premium:\n\n"
        f"👤 User: @{message.from_user.username or 'N/A'}\n"
        f"🆔 ID: {user_id}\n"
        f"🎬 Plan: {yt_plan}\n"
        f"💳 Method: {method}\n"
        f"📝 Txn ID: {txn_id}",
        reply_markup=markup
    )

    bot.send_message(message.chat.id, "✅ আপনার অর্ডার কনফার্ম হয়েছে! Admin ডেলিভারি দিবেন।")
    home_menu(message.chat.id)

# Refer Section
@bot.message_handler(func=lambda m: m.text == "👥 Refer")
def refer(message):
    user_id = message.from_user.id
    if user_id in users:
        ref_count = users[user_id]["referral_count"]
        ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

        msg = f"""
📢 রেফার প্রোগ্রাম:

🔗 আপনার রেফার লিংক:
{ref_link}

🎉 প্রতিটি রেফারেলের জন্য পাবেন ২ টাকা
👥 আপনার রেফার্ড ইউজার: {ref_count} জন

বন্ধুদের সাথে শেয়ার করুন এবং টাকা উপার্জন করুন!
"""
        bot.send_message(message.chat.id, msg)
    else:
        bot.send_message(message.chat.id, "❌ একাউন্ট খুঁজে পাওয়া যায়নি! /start লিখুন")

# Support Section
@bot.message_handler(func=lambda m: m.text == "🆘 Support")
def support(message):
    support_msg = """
🆘 সাপোর্ট সেন্টার:

যেকোনো সমস্যা বা প্রশ্নের জন্য যোগাযোগ করুন:

🆔 টেলিগ্রাম: @Riyadbd71
📧 ইমেইল: raimahmed1424@gmail.com
🕒 সময়: 24/7

আমরা ২৪ ঘন্টার মধ্যে আপনার সমস্যা সমাধান করার চেষ্টা করব।
"""
    bot.send_message(message.chat.id, support_msg)

# Simplified Delivery System
@bot.message_handler(func=lambda m: m.from_user.id == int(ADMIN_ID) and m.text.startswith('/delivery_'))
def delivery_command(message):
    try:
        parts = message.text.split('_')
        user_id = int(parts[1])
        delivery_text = ' '.join(parts[2:]) if len(parts) > 2 else None
        
        if delivery_text:
            # If delivery text is included in the command
            bot.send_message(user_id, f"✅ আপনার অর্ডার ডেলিভারি:\n\n{delivery_text}")
            bot.send_message(ADMIN_ID, f"✔️ ডেলিভারি সম্পন্ন হয়েছে user {user_id} কে")
        else:
            # If just /delivery_userid is sent, ask for delivery details
            msg = bot.send_message(ADMIN_ID, f"📩 User {user_id} কে কি পাঠাবেন? ডিটেইলস লিখুন:")
            bot.register_next_step_handler(msg, lambda m: send_delivery(m, user_id))
    except:
        bot.send_message(ADMIN_ID, "⚠️ শুধুমাত্র এই ফরম্যাটে লিখুন:\n/delivery_123456789 details_here")

def send_delivery(message, user_id):
    try:
        delivery_text = f"""
✅ আপনার অর্ডার ডেলিভারি:

{message.text}

ধন্যবাদান্তে,
Digital Buy Sell BD
"""
        bot.send_message(user_id, delivery_text)
        bot.send_message(ADMIN_ID, f"✔️ ডেলিভারি সম্পন্ন হয়েছে user {user_id} কে")
    except:
        bot.send_message(ADMIN_ID, f"❌ User {user_id} কে মেসেজ পাঠানো যায়নি (বট ব্লক করেছে)")

print("🤖 Bot is running...")
bot.infinity_polling()
