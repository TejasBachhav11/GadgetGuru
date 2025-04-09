import os
import re
import spacy
from spellchecker import SpellChecker
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    CallbackContext,
)
from typing import Any


from Laptop_Chatbot2 import find_best_laptops, convert_budget_to_number, classify_intent


nlp = spacy.load("en_core_web_sm")
spell = SpellChecker()


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("The TELEGRAM_BOT_TOKEN environment variable is not set.")


(BUDGET, USAGE, TRAVEL, ASK_BATTERY, ASK_BRAND, HANDLE_BRAND) = range(6)


BATTERY_OPTIONS = [
    [InlineKeyboardButton("Yes", callback_data="Yes")],
    [InlineKeyboardButton("No", callback_data="No")]
]


BRAND_OPTIONS = [
    [InlineKeyboardButton("Dell", callback_data="Dell")],
    [InlineKeyboardButton("HP", callback_data="HP")],
    [InlineKeyboardButton("Lenovo", callback_data="Lenovo")],
    [InlineKeyboardButton("Asus", callback_data="Asus")],
    [InlineKeyboardButton("Acer", callback_data="Acer")],
    [InlineKeyboardButton("Other", callback_data="Other")],
    [InlineKeyboardButton("Any", callback_data="Any")]
]

def parse_yes_no(text: str) -> bool:
    """Returns True if the text is affirmative; else False."""
    doc = nlp(text.lower())
    negation = any(tok.dep_ == "neg" for tok in doc)
    affirmative_words = {"yes", "y", "yeah", "yep", "sure", "affirmative"}
    tokens = {token.text for token in doc}
    return bool(tokens.intersection(affirmative_words)) and not negation

def extract_budget_from_text(text: str) -> int:
    """Extracts digits from the text and returns an integer budget."""
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else None

async def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation by asking for the budget."""
    await update.message.reply_text(
        "👋 Hi! I'm your **Laptop Recommendation Bot**. Let's find the best laptop for you!\n\n"
        "💰 **What's your budget range for the laptop?** (Enter in ₹)",
        parse_mode="Markdown"
    )
    return BUDGET

async def budget(update: Update, context: CallbackContext) -> int:
    """Processes the budget input and asks for primary use case."""
    text = update.message.text.strip()
    budget_value = extract_budget_from_text(text)
    if not budget_value:
        await update.message.reply_text("⚠️ Please enter a valid budget amount (e.g., 50000).")
        return BUDGET
    context.user_data["budget"] = budget_value
    await update.message.reply_text(
        "🎯 **What will you primarily use the laptop for?** 🤔💻",
        parse_mode="Markdown"
    )
    return USAGE

async def usage(update: Update, context: CallbackContext) -> int:
    """Stores usage info and asks for travel preference."""
    context.user_data["usage"] = update.message.text.strip()
    await update.message.reply_text(
        "✈️ **Do you travel frequently and need a lightweight laptop?** (Type 'Yes' or 'No')",
        parse_mode="Markdown"
    )
    return TRAVEL

async def travel(update: Update, context: CallbackContext) -> int:
    """Stores travel preference and shows inline keyboard for battery backup."""
    context.user_data["travel"] = parse_yes_no(update.message.text.strip())
    reply_markup = InlineKeyboardMarkup(BATTERY_OPTIONS)
    await update.message.reply_text(
        "🔋 **Do you need a long battery backup for work or studies?**",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return ASK_BATTERY

async def handle_battery_callback(update: Update, context: CallbackContext) -> int:
    """Handles the battery backup inline keyboard callback and asks for brand preference."""
    query = update.callback_query
    await query.answer()
    battery_choice = query.data  # "Yes" or "No"
    context.user_data["battery"] = (battery_choice == "Yes")
    
    reply_markup = InlineKeyboardMarkup(BRAND_OPTIONS)
    await query.message.reply_text(
        "🏷️ **Do you have a preferred laptop brand?**\n",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return ASK_BRAND

async def handle_brand_callback(update: Update, context: CallbackContext) -> int:
    """Handles the brand inline keyboard callback."""
    query = update.callback_query
    await query.answer()
    brand_choice = query.data  # e.g., "Dell", "HP", "Other", "Any"
    if brand_choice == "Other":
        await query.message.reply_text(
            "Please enter your preferred brand manually:",
            reply_markup=ReplyKeyboardRemove()
        )
        return HANDLE_BRAND
    elif brand_choice == "Any":
        context.user_data["brand"] = None  # No brand filtering
    else:
        context.user_data["brand"] = brand_choice.lower()
    await query.message.reply_text(
        "🔍 Searching for the best laptops for you... Please wait!",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    await recommend_laptops(query.message, context)
    return ConversationHandler.END

async def handle_brand_manual(update: Update, context: CallbackContext) -> int:
    """Handles manually entered brand input."""
    text = update.message.text.strip()
    corrected = spell.correction(text)
    context.user_data["brand"] = corrected.lower() if corrected else text.lower()
    await update.message.reply_text(
        "🔍 Searching for the best laptops for you... Please wait!",
        reply_markup=ReplyKeyboardRemove()
    )
    await recommend_laptops(update.message, context)
    return ConversationHandler.END

async def recommend_laptops(message_obj: Update, context: CallbackContext) -> None:
    """
    Uses find_best_laptops from Laptop_Chatbot2.py to fetch recommendations based on user preferences.
    The output is then formatted with Markdown to embed the "Buy Now" links below each laptop.
    """
    user_prefs = {
        "budget": context.user_data.get("budget"),
        "profession": context.user_data.get("usage"),
        "travel": context.user_data.get("travel"),
        "battery": context.user_data.get("battery"),
        "brand": context.user_data.get("brand")
    }
    recommendations = find_best_laptops(user_prefs)
    if not recommendations:
        await message_obj.reply_text("❌ No matching laptops found. Try adjusting your preferences.")
        return
    
    summary_lines = ["✨ **Here are the top laptops for you:**\n"]
    for i, (laptop, _) in enumerate(recommendations, start=1):
        summary_lines.append(
            f"🔹 {i}. **{laptop['Brand']} {laptop['Series']}** - ₹{laptop['Price']}\n"
            f"💻 CPU: {laptop['Processor Type']} | 🎮 GPU: {laptop['Graphics Card Description']}\n"
            f"🔋 Battery: {laptop['battery capacity']}Wh | ⚖️ Weight: {laptop['weight']} kg\n"
            f"[🛒 Buy Now]({laptop['link']})\n"
        )
    
    summary = "\n".join(summary_lines)
    await message_obj.reply_text(summary, parse_mode="Markdown")

async def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Conversation canceled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    app = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, budget)],
            USAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, usage)],
            TRAVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, travel)],
            ASK_BATTERY: [CallbackQueryHandler(handle_battery_callback)],
            ASK_BRAND: [CallbackQueryHandler(handle_brand_callback)],
            HANDLE_BRAND: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_brand_manual)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
