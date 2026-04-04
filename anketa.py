import json
import os
from datetime import datetime

# --- CONFIGURATION & DATA ---
DATA_FILE = "statistics.json"

# Defining "Crazy" questions
SURVEY_QUESTIONS = [
    {
        "id": "name",
        "question": "Как тебя зовут, герой?",
        "type": "text"
    },
    {
        "id": "purple_elephant",
        "question": "Ты когда-нибудь видел фиолетового слона в галстуке?",
        "type": "choice",
        "options": ["Да, он мой сосед", "Нет, только в очках", "Я сам этот слон", "Что за вопросы?!"]
    },
    {
        "id": "cat_day",
        "question": "Если бы ты стал котом на один день, что бы ты сделал первым?",
        "type": "text"
    },
    {
        "id": "reality_check",
        "question": "Этот мир - симуляция?",
        "type": "choice",
        "options": ["Да, и у меня лагает", "Нет, я проверял", "42", "Я - часть кода"]
    },
    {
        "id": "crazy_level",
        "question": "Уровень твоего безумия от 1 до 10?",
        "type": "text" # Could be choice, but let's take input
    }
]

def save_response(responses):
    """Saves a single set of responses to a JSON file."""
    data = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            pass

    responses["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data.append(responses)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_stats():
    """Simple count of responses."""
    if not os.path.exists(DATA_FILE):
        return 0
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return len(data)

def show_analytics():
    """Detailed information about who answered what."""
    if not os.path.exists(DATA_FILE):
        print("📭 Пока никто не прошел анкету.")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n--- 📊 АНАЛИТИКА БЕЗУМИЯ (Опрошено: {len(data)}) ---")
    
    # Process each question
    for q in SURVEY_QUESTIONS:
        print(f"\n🔹 {q['question']}")
        answers = [resp.get(q['id']) for resp in data if q['id'] in resp]
        
        if q["type"] == "choice":
            # Count choices
            from collections import Counter
            counts = Counter(answers)
            for opt in q["options"]:
                count = counts.get(opt, 0)
                percent = (count / len(data) * 100) if len(data) > 0 else 0
                print(f"  [{count:2}] {percent:4.1f}% | {opt}")
        else:
            # Show last few text answers
            print(f"  Последние ответы: {', '.join(map(str, answers[-3:]))}...")

    print("\n" + "="*40 + "\n")

def get_detailed_stats():
    """Returns a string with detailed information about all responses for Telegram."""
    if not os.path.exists(DATA_FILE):
        return "📭 Пока никто не прошел анкету."

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return "❌ Ошибка при чтении данных статистики."

    if not data:
        return "📭 Пока никто не прошел анкету."

    stats_msg = f"📊 *АНАЛИТИКА БЕЗУМИЯ*\nОпрошено героев: {len(data)}\n"
    
    from collections import Counter
    
    for q in SURVEY_QUESTIONS:
        stats_msg += f"\n🔹 *{q['question']}*\n"
        answers = [resp.get(q['id']) for resp in data if q['id'] in resp]
        
        if q["type"] == "choice":
            counts = Counter(answers)
            for opt in q["options"]:
                count = counts.get(opt, 0)
                percent = (count / len(data) * 100) if len(data) > 0 else 0
                stats_msg += f"• `{count:2}` {percent:4.1f}% | {opt}\n"
        else:
            # Show last few text answers
            subset = answers[-5:] if answers else []
            stats_msg += f"Последние ответы: {', '.join(map(str, subset))}\n"

    return stats_msg
