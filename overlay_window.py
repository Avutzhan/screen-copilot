class Overlay:

    def __init__(self):

        self.root = tk.Tk()

        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.6)

        width = 1300
        height = 420

        # важно
        self.root.update_idletasks()

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        x = (screen_w - width) // 2
        y = (screen_h - height) // 2

        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.root.configure(bg="#000")

        self.question = tk.Label(
            self.root,
            text="Waiting for question...",
            fg="white",
            bg="#000",
            font=("Arial", 22, "bold"),
            wraplength=860,
            justify="center"
        )

        self.question.pack(pady=20)

        self.answer = tk.Label(
            self.root,
            text="",
            fg="#7CFC00",
            bg="#000",
            font=("Arial", 20),
            wraplength=860,
            justify="center"
        )

        self.answer.pack(pady=10)

    def update(self, question, answer):

        self.question.config(text=question)
        self.answer.config(text=answer)

        self.root.update()