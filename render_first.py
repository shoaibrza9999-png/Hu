import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters


# Enable logging to see errors and status updates in your console
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I'm a bot, please talk to me!"
    )

# Function to handle normal text messages (The Echo)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    received_text = update.message.text
    # Reply with the same text
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=received_text
    )

if __name__ == '__main__':
    # REPLACE 'YOUR_TOKEN' with the token you got from BotFather
    TOKEN = "8103639461:AAF_F1lLwqKWUWUIuR-erBVzsODz1W37DYM"
    
    # Create the Application
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Add handlers
    start_handler = CommandHandler('start', start)
    # filters.TEXT & (~filters.COMMAND) ensures we only echo text, not commands
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    
    # Run the bot
    print("Bot is polling...")
    application.run_polling()
