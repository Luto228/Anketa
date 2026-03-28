import anketa as core

def run_cli():
    print("\n--- 📝 ДОБРО ПОЖАЛОВАТЬ В СУПЕР АНКЕТУ! ---")
    print("Ответь на сумасшедшие вопросы или беги!\n")
    
    user_responses = {}
    
    for q in core.SURVEY_QUESTIONS:
        print(f"[{q['id']}] {q['question']}")
        
        if q["type"] == "choice":
            for idx, opt in enumerate(q["options"], 1):
                print(f"  {idx}. {opt}")
            
            while True:
                choice = input("Выбери номер: ")
                if choice.isdigit():
                    idx = int(choice)
                    if 1 <= idx <= len(q["options"]):
                        user_responses[q["id"]] = q["options"][idx - 1]
                        break
                print("❌ Эй! Введи правильный номер!")
        else:
            answer = input("Твой ответ: ")
            user_responses[q["id"]] = answer
            
        print("-" * 10)

    core.save_response(user_responses)
    print("\n✅ ТВОЁ БЕЗУМИЕ СОХРАНЕНО! Спасибо.")
    print(f"Всего пройдено анкет: {core.get_stats()}")

if __name__ == "__main__":
    run_cli()
    input("\nНажми Enter, чтобы выйти...")
    # Add a small wait for the user to see the output
