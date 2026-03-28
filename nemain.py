import sys

def main():
    print("Welcome to THE CRAZY ANKETA (СУПЕР АНКЕТА)!")
    print("Choose your destiny (Выберите интерфейс):")
    print("1. CLI (Command Line Interface) - Старая добрая консоль 🐚")
    print("2. GUI (Windows App) - Красивое темное окошко ✨")
    print("3. Telegram Bot - Сила чата 🤖")
    print("4. View Statistics - Посмотреть аналитику 📊")
    
    choice = input("\nYour choice (1/2/3/4): ")
    
    if choice == "1":
        import cli_ui
        cli_ui.run_cli()
    elif choice == "2":
        import gui_ui
        from gui_ui import AnketaGui
        app = AnketaGui()
        app.mainloop()
    elif choice == "3":
        import bot_ui
        bot_ui.run_bot()
    elif choice == "4":
        import anketa
        anketa.show_analytics()
        input("Нажми Enter, чтобы вернуться в меню...")
    else:
        print("Invalid choice! BEGONE!")

if __name__ == "__main__":
    main()
