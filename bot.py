import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, date
from config import *
from database import users, special_links

bot = telebot.TeleBot(BOT_TOKEN)

# ================= FORCE JOIN =================
def is_joined(user_id):
    for ch in FORCE_CHANNELS:
        try:
            s = bot.get_chat_member(ch, user_id).status
            if s not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

def join_markup():
    m = InlineKeyboardMarkup()
    for i, l in enumerate(JOIN_LINKS, 1):
        m.add(InlineKeyboardButton(f"Join {i}", url=l))
    m.add(InlineKeyboardButton("✅ Joined", callback_data="check"))
    return m

# ================= START =================
@bot.message_handler(commands=["start"])
def start(msg):
    user_id = msg.from_user.id
    args = msg.text.split()

    if not users.find_one({"user_id": user_id}):
        ref = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
        users.insert_one({
            "user_id": user_id,
            "coins": 0,
            "referrals": 0,
            "daily": str(date.today()),
            "ref_by": ref
        })
        if ref:
            users.update_one({"user_id": ref}, {"$inc": {"referrals": 1, "coins": 10}})

    if not is_joined(user_id):
        bot.send_message(msg.chat.id, "🚫 Please join all channels", reply_markup=join_markup())
        return

    bot.send_message(
        msg.chat.id,
        f"👋 Welcome\n\n💰 Coins: {users.find_one({'user_id': user_id})['coins']}\n"
        f"🔗 Referral:\nhttps://t.me/{bot.get_me().username}?start={user_id}"
    )

# ================= DAILY BONUS =================
@bot.message_handler(commands=["daily"])
def daily(msg):
    u = users.find_one({"user_id": msg.from_user.id})
    if u["daily"] == str(date.today()):
        bot.send_message(msg.chat.id, "❌ Aaj already claim kar chuke ho")
    else:
        users.update_one({"user_id": msg.from_user.id},
                         {"$set": {"daily": str(date.today())}, "$inc": {"coins": DAILY_BONUS}})
        bot.send_message(msg.chat.id, f"🎁 Daily bonus +{DAILY_BONUS} coins")

# ================= SPECIAL LINK =================
@bot.message_handler(commands=["special_link"])
def special_link(msg):
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("CREATE", callback_data="sp_create"),
        InlineKeyboardButton("MODIFY", callback_data="sp_modify"),
        InlineKeyboardButton("DELETE", callback_data="sp_delete"),
        InlineKeyboardButton("CLOSE", callback_data="sp_close")
    )
    bot.send_message(msg.chat.id, "🔗 Special Link Panel", reply_markup=m)

# ===== CREATE FLOW =====
@bot.callback_query_handler(func=lambda c: c.data == "sp_create")
def create_link(c):
    bot.send_message(c.message.chat.id, "✍️ Send me the message you want to store")
    bot.register_next_step_handler(c.message, save_message)

def save_message(msg):
    data = special_links.insert_one({
        "owner": msg.from_user.id,
        "messages": [msg.text],
        "created": datetime.now()
    })
    m = InlineKeyboardMarkup()
    m.add(
        InlineKeyboardButton("GENERATE LINK", callback_data=f"gen_{data.inserted_id}"),
        InlineKeyboardButton("CANCEL", callback_data="cancel")
    )
    bot.send_message(
        msg.chat.id,
        "📦 Stored Messages: 1\nWant to add another message? Just send it!",
        reply_markup=m
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("gen_"))
def generate_link(c):
    link_id = c.data.split("_")[1]
    link = f"https://t.me/{bot.get_me().username}?start=sp{link_id}"

    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("SHARE URL", url=f"https://t.me/share/url?url={link}"))

    bot.send_message(c.message.chat.id, f"🔗 Here is your special link:\n{link}", reply_markup=m)

# ================= AUTO REPLY =================
@bot.message_handler(func=lambda m: True)
def auto(m):
    if not is_joined(m.from_user.id):
        bot.send_message(m.chat.id, "⚠️ Join all channels first")
        return
    bot.send_message(m.chat.id, "🤖 Commands:\n/start\n/daily\n/special_link")

print("Bot Running...")
bot.infinity_polling()
