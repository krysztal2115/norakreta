import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "TU_WSTAW_TOKEN_BOTA"
ADMIN_ID = 123456789  # <-- Wstaw swój Telegram ID
BACKUP_LINK = "https://t.me/twoja_grupa_backupowa"

# ====== BAZA DANYCH ======
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")
conn.commit()


# ====== /start ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    await update.message.reply_text(
        "? Zosta³eœ zapisany do systemu backupu.\n"
        "Jeœli grupa padnie — dostaniesz nowy link."
    )


# ====== WYSY£ANIE LINKU BACKUPU ======
async def send_backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    sent = 0
    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user[0],
                text=f"?? G³ówna grupa zosta³a usuniêta.\n\nNowy link:\n{BACKUP_LINK}"
            )
            sent += 1
        except:
            pass

    await update.message.reply_text(f"Wys³ano backup do {sent} osób.")


# ====== START APLIKACJI ======
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("backup", send_backup))

print("Bot dzia³a...")
app.run_polling()