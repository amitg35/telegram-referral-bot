import telebot
import os
import uuid
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("8517864682:AAEx4QpsV1NRRQh1mMfjrC382hUbN4GckTk")
bot = telebot.TeleBot(BOT_TOKEN)

# ===== FORCE JOIN CHANNELS (username only) =====
FORCE_CHANNELS = [
    "1ZMyGGyTb1s0MzM1",
    "Db38DSH0iR1iMDc1",
    "ZlHW_ZUS6yQ1NDA9",
    "imnY9aNAt9A1YzNl"
]

user_messages = {}
special_links = {}

# ===== FORCE JOIN CHECK =====
def is_joined(user_id):
    for ch in FORCE_CHANNELS:
        try:
            status = bot.get_chat_member(f"@{ch}", user_id).status
            if status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# ===== START COMMAND =====
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()

    if len(args) > 1:
        code = args[1]
        if code in special_links:
            for msg in special_links[code]:
                bot.send_message(message.chat.id, msg)
            return

    if not is_joined(user_id):
        markup = InlineKeyboardMarkup()
        for ch in FORCE_CHANNELS:
            markup.add(
                InlineKeyboardButton(f"Join @{ch}", url=f"https://t.me/{ch}")
            )
        markup.add(
            InlineKeyboardButton("✅ CHECK JOIN", callback_data="check_join")
        )
        bot.send_message(
            message.chat.id,
            "🚫 Bot use karne ke liye pehle channels join karo:",
            reply_markup=markup
        )
    else:
        bot.send_message(message.chat.id, "✅ Welcome! Auto reply active hai.")

# ===== CHECK JOIN BUTTON =====
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    if is_joined(call.from_user.id):
        bot.edit_message_text(
            "✅ Join verified! Ab bot use kar sakte ho.",
            call.message.chat.id,
            call.message.message_id
        )
    else:
        bot.answer_callback_query(call.id, "❌ Pehle join karo!", show_alert=True)

# ===== AUTO REPLY =====
@bot.message_handler(func=lambda m: is_joined(m.from_user.id))
def auto_reply(message):
    bot.reply_to(message, f"🤖 Auto Reply:\n{message.text}")

# ================= SPECIAL LINK =================

@bot.message_handler(commands=["special_link"])
def special_link(message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("➕ CREATE", callback_data="create"),
        InlineKeyboardButton("✏️ MODIFY", callback_data="modify"),
        InlineKeyboardButton("🗑 DELETE", callback_data="delete"),
        InlineKeyboardButton("❌ CLOSE", callback_data="close")
    )
    bot.send_message(
        message.chat.id,
        "Do you want to create a new special link, or modify an existing one, or delete it?",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = call.from_user.id

    if call.data == "create":
        user_messages[uid] = []
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🔗 GENERATE LINK", callback_data="generate"),
            InlineKeyboardButton("❌ CANCEL", callback_data="cancel")
        )
        bot.send_message(
            call.message.chat.id,
            "Send me the message you want to store\n\nStored Messages: 0\nWant to add another message? Just send it!",
            reply_markup=markup
        )

    elif call.data == "generate":
        if uid not in user_messages or not user_messages[uid]:
            bot.answer_callback_query(call.id, "❌ No message stored", show_alert=True)
            return

        code = str(uuid.uuid4())[:8]
        special_links[code] = user_messages[uid]

        link = f"https://t.me/{bot.get_me().username}?start={code}"
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("📤 SHARE URL", url=f"https://t.me/share/url?url={link}")
        )
        bot.send_message(
            call.message.chat.id,
            f"Here is your special link:\n\n{link}",
            reply_markup=markup
        )

    elif call.data == "cancel":
        user_messages.pop(uid, None)
        bot.send_message(call.message.chat.id, "❌ Cancelled")

    elif call.data == "close":
        bot.edit_message_text(
            "Closed ❌",
            call.message.chat.id,
            call.message.message_id
        )

# ===== STORE SPECIAL MESSAGES =====
@bot.message_handler(func=lambda m: m.from_user.id in user_messages)
def store_message(message):
    uid = message.from_user.id
    user_messages[uid].append(message.text)
    bot.reply_to(
        message,
        f"✅ Stored Messages: {len(user_messages[uid])}\nWant to add another message? Just send it!"
    )

bot.infinity_polling()
