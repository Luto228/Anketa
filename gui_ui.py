import tkinter as tk
from tkinter import ttk, messagebox
import anketa as core

class AnketaGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🔥 СУПЕР АНКЕТА 🔥")
        self.geometry("600x650")
        self.configure(bg="#1e1e2e") # Dark theme for "Premium" feel
        
        self.questions = core.SURVEY_QUESTIONS
        self.current_q_idx = 0
        self.user_responses = {}

        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure("TLabel", background="#1e1e2e", foreground="white", font=("Helvetica", 12))
        self.style.configure("TButton", background="#3e3d5c", foreground="white", font=("Helvetica", 11, "bold"))
        self.style.configure("TRadiobutton", background="#1e1e2e", foreground="white", font=("Helvetica", 10))

        self.main_container = tk.Frame(self, bg="#1e1e2e", padx=40, pady=40)
        self.main_container.pack(expand=True, fill="both")

        self.title_label = tk.Label(self.main_container, text="📝 СУПЕР АНКЕТА", font=("Helvetica", 20, "bold"), bg="#1e1e2e", fg="#cba6f7")
        self.title_label.pack(pady=(0, 20))

        self.question_frame = tk.Frame(self.main_container, bg="#1e1e2e")
        self.question_frame.pack(expand=True, fill="both")

        self.q_label = tk.Label(self.question_frame, text="", wraplength=500, justify="center", font=("Helvetica", 14), bg="#1e1e2e", fg="white")
        self.q_label.pack(pady=20)

        self.input_frame = tk.Frame(self.question_frame, bg="#1e1e2e")
        self.input_frame.pack(pady=20)

        self.next_btn = tk.Button(self.main_container, text="СЛЕДУЮЩИЙ ➡️", command=self.handle_next, 
                                  bg="#89b4fa", fg="#1e1e2e", font=("Helvetica", 12, "bold"), relief="flat", padx=20, pady=10)
        self.next_btn.pack(pady=40)

        self.show_question()

    def show_question(self):
        # Clear previous inputs
        for widget in self.input_frame.winfo_children():
            widget.destroy()

        if self.current_q_idx < len(self.questions):
            q = self.questions[self.current_q_idx]
            self.q_label.config(text=f"Вопрос {self.current_q_idx + 1}:\n{q['question']}")
            
            if q["type"] == "text":
                self.entry = tk.Entry(self.input_frame, font=("Helvetica", 12), width=30, bg="#313244", fg="white", insertbackground="white", relief="flat")
                self.entry.pack(pady=10)
                self.entry.focus_set()
            elif q["type"] == "choice":
                self.choice_var = tk.StringVar(value=q["options"][0])
                for opt in q["options"]:
                    rb = tk.Radiobutton(self.input_frame, text=opt, variable=self.choice_var, value=opt, 
                                      bg="#1e1e2e", fg="white", selectcolor="#313244", activebackground="#1e1e2e", 
                                      activeforeground="white", font=("Helvetica", 11))
                    rb.pack(anchor="w", pady=5)
        else:
            self.finish()

    def handle_next(self):
        q = self.questions[self.current_q_idx]
        if q["type"] == "text":
            val = self.entry.get().strip()
            if not val:
                messagebox.showwarning("Эй!", "Напиши хоть что-нибудь!")
                return
            self.user_responses[q["id"]] = val
        elif q["type"] == "choice":
            self.user_responses[q["id"]] = self.choice_var.get()
        
        self.current_q_idx += 1
        self.show_question()

    def finish(self):
        core.save_response(self.user_responses)
        self.q_label.config(text="✅ БЕЗУМИЕ СОХРАНЕНО!")
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        
        self.next_btn.config(text="ВЫЙТИ", command=self.destroy, bg="#a6e3a1")
        
        stats = core.get_stats()
        tk.Label(self.input_frame, text=f"Спасибо за участие!\n{stats}", font=("Helvetica", 12), bg="#1e1e2e", fg="#f5e0dc").pack(pady=20)

if __name__ == "__main__":
    app = AnketaGui()
    app.mainloop()
