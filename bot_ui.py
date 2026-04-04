import logging
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the first question."""
    context.user_data["responses"] = {}
    await update.message.reply_text(
        "👋 Привет! Добро пожаловать в СУПЕР АНКЕТУ!\n"
        "Давай начнем наше сумасшествие!\n\n"
        "📝 Хочешь посмотреть общую статистику? Нажми /stats"
    )
    return await ask_question(update, context, 0)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE, q_idx: int) -> int:
    """Asks a question based on its index."""
    q = core.SURVEY_QUESTIONS[q_idx]
    
    if q["type"] == "choice":
        reply_keyboard = [q["options"][i:i+2] for i in range(0, len(q["options"]), 2)]
        await update.message.reply_text(
            f"❓ {q['question']}",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )
    else:
        await update.message.reply_text(
            f"❓ {q['question']}",
            reply_markup=ReplyKeyboardRemove(),
        )
    
    return q_idx

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the answer and determines the next step."""
    q_idx = context.user_data.get("current_q", 0)
    q = core.SURVEY_QUESTIONS[q_idx]
    
    answer = update.message.text
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
            "Напиши /stats чтобы увидеть общую аналитику!",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(
        "Эх, ты решил сбежать от безумия! Ну пока.", reply_markup=ReplyKeyboardRemove()
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
        entry_points=[CommandHandler("start", start)],
        states={
            i: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)] 
            for i in range(len(core.SURVEY_QUESTIONS))
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("stats", stats))
    
    print("🤖 Бот запущен! Иди в Telegram и нажми /start.")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
