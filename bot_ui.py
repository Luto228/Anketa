import logging
import sys
import os

# Prevent Python from creating __pycache__ folders
sys.dont_write_bytecode = True
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,
)
import anketa as core
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- States for ConversationHandler ---
# We'll use question indices as states
STATES = list(range(len(core.SURVEY_QUESTIONS)))
END_STATE = -1

# Main Menu Keyboard
MAIN_MENU_KEYBOARD = [
    ["🚀 Начать Анкету", "📊 Статистика"],
]

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the main menu with buttons."""
    reply_markup = ReplyKeyboardMarkup(
        MAIN_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False
    )
    await update.message.reply_text(
        "👋 Привет! Добро пожаловать в СУПЕР АНКЕТУ!\n"
        "Выбери действие ниже:",
        reply_markup=reply_markup
    )

async def start_survey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the first question."""
    context.user_data["responses"] = {}
    context.user_data["current_q"] = 0
    await update.message.reply_text(
        "🔥 Начинаем наше сумасшествие! Отвечай честно (или нет).",
        reply_markup=ReplyKeyboardRemove()
    )
    return await ask_question(update, context, 0)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE, q_idx: int) -> int:
    """Asks a question based on its index."""
    q = core.SURVEY_QUESTIONS[q_idx]
    
    if q["type"] == "choice":
        # Options in rows of 2
        reply_keyboard = [q["options"][i:i+2] for i in range(0, len(q["options"]), 2)]
        # Add special Cancel row
        reply_keyboard.append(["❌ Отмена"])
        
        await update.message.reply_text(
            f"❓ {q['question']}",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )
    else:
        # Show a "Cancel" button for text inputs
        await update.message.reply_text(
            f"❓ {q['question']}",
            reply_markup=ReplyKeyboardMarkup([["❌ Отмена"]], resize_keyboard=True),
        )
    
    return q_idx

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the answer and determines the next step."""
    q_idx = context.user_data.get("current_q", 0)
    q = core.SURVEY_QUESTIONS[q_idx]
    
    answer = update.message.text
    
    # Handle "Cancel" button if it arrived here
    if answer == "❌ Отмена":
        return await cancel(update, context)

    # Validation for choices
    if q["type"] == "choice" and answer not in q["options"]:
        await update.message.reply_text(
            f"❌ Эй, выбери вариант из меню!\n"
            f"Твой ответ «{answer}» не подходит.",
            reply_markup=ReplyKeyboardMarkup([q["options"][i:i+2] for i in range(0, len(q["options"]), 2)] + [["❌ Отмена"]], resize_keyboard=True)
        )
        return q_idx

    context.user_data["responses"][q["id"]] = answer
    
    next_q_idx = q_idx + 1
    if next_q_idx < len(core.SURVEY_QUESTIONS):
        context.user_data["current_q"] = next_q_idx
        return await ask_question(update, context, next_q_idx)
    else:
        # Save results
        core.save_response(context.user_data["responses"])
        await update.message.reply_text(
            f"✅ ТВОЁ БЕЗУМИЕ СОХРАНЕНО!\n"
            f"Спасибо за участие! Пройденная анкета: {core.get_stats()}\n"
            "Нажми кнопку ниже, чтобы увидеть аналитику или начать заново!",
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True)
        )
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation and returns to menu."""
    await update.message.reply_text(
        "Эх, ты решил сбежать от безумия! Ну пока.", 
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True)
    )
    return ConversationHandler.END

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the general statistics to the user."""
    detailed_stats = core.get_detailed_stats()
    await update.message.reply_text(detailed_stats, parse_mode="Markdown")

def run_bot():
    # Load token from .env file
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not TOKEN or TOKEN == "ТВОЙ_ТОКЕН_ТУТ":
        print("❌ ОШИБКА: Укажите токен бота в файле .env!")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    # Build states dynamically based on number of questions
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🚀 Начать Анкету$"), start_survey),
            CommandHandler("start_anketa", start_survey)
        ],
        states={
            i: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^❌ Отмена$"), handle_answer)] 
            for i in range(len(core.SURVEY_QUESTIONS))
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.Regex("^❌ Отмена$"), cancel)
        ],
    )

    app.add_handler(CommandHandler("start", show_menu))
    app.add_handler(CommandHandler("menu", show_menu))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.Regex("^📊 Статистика$"), stats))
    
    print("🤖 Бот запущен! Меню с кнопками активно.")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
