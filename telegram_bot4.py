from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import pandas as pd
import os

# Load the dataset (mimicking chatbot10.py logic)
classified_laptops = pd.read_csv("classified_laptops_output.csv").rename(columns=str.strip)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

user_data = {}

questions = [
    "💰 What's your budget range for the laptop? (Enter in ₹)",
    "🎯 What will you use the laptop for? (e.g., Gaming, Productivity, Business, Budget, etc.)",
    "🏷️ Do you have a preferred laptop brand? (Enter comma-separated or type 'Any')",
    "✈️ Will you travel frequently and need a lightweight laptop? (yes/no)",
    "🔋 Is long battery life a priority for you? (yes/no)"
]

def recommend_laptop(user_prefs):
    budget = user_prefs["budget"]
    categories = user_prefs["categories"]
    travel = user_prefs["travel"]
    battery = user_prefs["battery"]
    brand = user_prefs["brand"]
    flag = "top"

    budget_laptops = classified_laptops[classified_laptops["Price"] <= budget]

    if "Any" not in brand:
        brand_laptops = budget_laptops[budget_laptops["Brand"].isin(brand)]
        filtered_laptops = brand_laptops if not brand_laptops.empty else budget_laptops
        if brand_laptops.empty:
            flag = "nobrand"
    else:
        filtered_laptops = budget_laptops

    filtered_laptops = filtered_laptops[
        filtered_laptops["Laptop Categories"].apply(lambda x: any(cat in eval(x) for cat in categories))
    ]

    if not filtered_laptops.empty:
        filtered_laptops['combined_score'] = filtered_laptops['Laptop Score']
        if travel:
            wr = filtered_laptops['weight'].max() - filtered_laptops['weight'].min()
            if wr > 0:
                filtered_laptops['combined_score'] += ((filtered_laptops['weight'].max() - filtered_laptops['weight']) / wr) * 0.3
        if battery:
            br = filtered_laptops['battery capacity'].max() - filtered_laptops['battery capacity'].min()
            if br > 0:
                filtered_laptops['combined_score'] += ((filtered_laptops['battery capacity'] - filtered_laptops['battery capacity'].min()) / br) * 0.3
        return filtered_laptops.sort_values(by='combined_score', ascending=False).head(3), None, flag
    else:
        flag = "alternative"
        if "Any" not in brand and flag == "nobrand":
            brand_alts = budget_laptops[budget_laptops["Brand"].isin(brand)]
            if not brand_alts.empty:
                general = budget_laptops.sort_values(by="Laptop Score", ascending=False).head(3)
                top_brand = brand_alts.sort_values(by="Laptop Score", ascending=False).head(1)
                return general, top_brand, "alternative_with_brand"
        alt = budget_laptops.sort_values(by="Laptop Score", ascending=False).head(3)
        return None, alt, flag

async def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    user_data[user_id] = {'question_index': 0}
    await update.message.reply_text("👋 Hi! I'm GadgetGuru, your personal laptop advisor. Let's find your perfect laptop!")
    await update.message.reply_text(questions[0])

async def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    message = update.message.text.strip()

    if user_id not in user_data:
        user_data[user_id] = {'question_index': 0}

    q_index = user_data[user_id]['question_index']

    try:
        if q_index == 0:
            if not message.isdigit():
                await update.message.reply_text("❌ Please enter a valid number for budget.")
                return
            user_data[user_id]['budget'] = int(message)

        elif q_index == 1:
            user_data[user_id]['categories'] = [c.strip().title() for c in message.split(',')]

        elif q_index == 2:
            brands = [b.strip().title() for b in message.split(',')]
            user_data[user_id]['brand'] = brands if brands else ["Any"]

        elif q_index == 3:
            if message.lower() not in ["yes", "no"]:
                await update.message.reply_text("Please answer with 'yes' or 'no'.")
                return
            user_data[user_id]['travel'] = 1 if message.lower() == "yes" else 0

        elif q_index == 4:
            if message.lower() not in ["yes", "no"]:
                await update.message.reply_text("Please answer with 'yes' or 'no'.")
                return
            user_data[user_id]['battery'] = 1 if message.lower() == "yes" else 0

        user_data[user_id]['question_index'] += 1

        if user_data[user_id]['question_index'] < len(questions):
            await update.message.reply_text(questions[user_data[user_id]['question_index']])
        else:
            await update.message.reply_text("🔍 Finding the best laptops for you...")

            top_laptops, alt_laptops, flag = recommend_laptop(user_data[user_id])
            response = ""

            intro = {
                "top": "✅ Here are the best laptops based on your preferences:\n\n",
                "nobrand": "⚠️ Couldn’t find your brand, but here are great alternatives:\n\n",
                "alternative": "⚠️ No perfect match, but these come close:\n\n",
                "alternative_with_brand": "⚠️ Here's a mix of general options and one from your preferred brand:\n\n"
            }

            response += intro.get(flag, "")

            def format_laptop(row):
                return (
                    f"💻 *{row['Brand']} {row['Series']} {row['Item model number']}*\n"
                    f"• 💰 Price: ₹{row['Price']}\n"
                    f"• 🧠 CPU: {row['cpu']}\n"
                    f"• 🧮 RAM: {row['RAM']}GB\n"
                    f"• 💾 Storage: {row['Hard Drive Size']} {row['Hard Disk Description']}\n"
                    f"• ⚡ Battery: {row['battery capacity']}mAh\n"
                    f"• ⚖️ Weight: {row['weight']} kg\n"
                    f"• 🔁 Refresh Rate: {row['refresh rate']}Hz\n"
                    f"• 🎮 GPU: {row['gpu']}\n"
                    f"• 🔗 [Amazon Link]({row['link']})" if isinstance(row['link'], str) else ""
                )

            if top_laptops is not None:
                for _, row in top_laptops.iterrows():
                    response += format_laptop(row) + "\n\n"
            elif alt_laptops is not None:
                for _, row in alt_laptops.iterrows():
                    response += format_laptop(row) + "\n\n"
            else:
                response += "😢 Sorry, no laptops found with your criteria."

            await update.message.reply_text(response, parse_mode="Markdown")
            del user_data[user_id]

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")
        del user_data[user_id]

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
