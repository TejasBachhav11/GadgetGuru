from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import os

# Get your bot token from BotFather
TOKEN = "7954651768:AAFBfCbDywpqtix1lC-XIXDA_B7frm5Wiuw"  # Replace with your actual token

# Start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hi! I'm your Laptop Recommendation Bot. Tell me your requirements.")

# Message handler
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    response = f"You said: {user_message}"  # Replace with your NLP response
    await update.message.reply_text(response)

# Main function to run bot
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
