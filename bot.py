import sqlite3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ===== CONFIG =====

TOKEN = "8415057162:AAH_yK72905HzTtJYQ90lpLwLkA5BKHlzHw"
ADMIN_ID =  8246209948

IMAGE_URL = "https://i.imgur.com/abcd123.jpg"

DM_LINK = "https://t.me/yourcontact"
OPINIE_LINK = "https://t.me/yourreviews"
BACKUP_LINK = "https://t.me/yourbackup"

# ===== LOGS =====

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ===== DATABASE =====

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
user_id INTEGER PRIMARY KEY
)
""")

conn.commit()

# ===== MENU =====

def menu_keyboard():

    keyboard = [

        [
            InlineKeyboardButton("DM", url=DM_LINK),
            InlineKeyboardButton("Opinie", url=OPINIE_LINK)
        ],

        [
            InlineKeyboardButton("Backup", url=BACKUP_LINK)
        ]

    ]

    return InlineKeyboardMarkup(keyboard)

# ===== START =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )

    conn.commit()

    text = (
        "Welcome\n\n"
        "Here you can find:\n"
        "- contact\n"
        "- reviews\n"
        "- backup group\n\n"
        "Choose option below"
    )

    await context.bot.send_photo(

        chat_id=update.effective_chat.id,
        photo=IMAGE_URL,
        caption=text,
        reply_markup=menu_keyboard()

    )

# ===== ADMIN PANEL =====

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    await update.message.reply_text(

        f"ADMIN PANEL\n\n"
        f"Users: {count}\n\n"
        "/broadcast - send message\n"
        "/offer - send photo offer\n"
        "/backup - send backup link\n"
        "/export - export users"

    )

# ===== BROADCAST =====

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    context.user_data["mode"] = "broadcast"

    await update.message.reply_text("Send text to broadcast")

# ===== OFFER =====

async def offer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    context.user_data["mode"] = "offer_photo"

    await update.message.reply_text("Send offer photo")

# ===== BACKUP =====

async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    sent = 0

    for user in users:

        try:

            await context.bot.send_message(
                chat_id=user[0],
                text=f"Backup link:\n{BACKUP_LINK}"
            )

            sent += 1

        except:
            pass

    await update.message.reply_text(f"Backup sent to {sent} users")

# ===== EXPORT USERS =====

async def export_users(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    filename = "users.txt"

    with open(filename, "w") as file:

        for user in users:
            file.write(str(user[0]) + "\n")

    await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=open(filename, "rb")
    )

# ===== MESSAGE HANDLER =====

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    mode = context.user_data.get("mode")

    # BROADCAST

    if mode == "broadcast":

        text = update.message.text

        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()

        sent = 0

        for user in users:

            try:

                await context.bot.send_message(
                    chat_id=user[0],
                    text=text
                )

                sent += 1

            except:
                pass

        context.user_data["mode"] = None

        await update.message.reply_text(f"Message sent to {sent} users")

    # OFFER PHOTO

    elif mode == "offer_photo":

        photo = update.message.photo[-1].file_id

        context.user_data["offer_photo"] = photo
        context.user_data["mode"] = "offer_text"

        await update.message.reply_text("Send offer description")

    # OFFER TEXT

    elif mode == "offer_text":

        text = update.message.text
        photo = context.user_data["offer_photo"]

        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()

        sent = 0

        for user in users:

            try:

                await context.bot.send_photo(
                    chat_id=user[0],
                    photo=photo,
                    caption=text
                )

                sent += 1

            except:
                pass

        context.user_data["mode"] = None

        await update.message.reply_text(f"Offer sent to {sent} users")

# ===== START BOT =====

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("panel", panel))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("offer", offer))
    app.add_handler(CommandHandler("backup", backup))
    app.add_handler(CommandHandler("export", export_users))

    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_messages))

    logging.info("Bot started")

    app.run_polling()

if __name__ == "__main__":
    main()

