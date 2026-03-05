import time
import re
import difflib
import mss
import cv2
import pytesseract
import numpy as np
from openai import OpenAI
import tkinter as tk
import threading
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

monitor = {
    "top": 124,
    "left": 322,
    "width": 1589,
    "height": 107
}
last_hash = None
# --- Настройки анти-спама ---
POLL_SECONDS = 0.5
STABLE_HITS = 2
MIN_LEN = 2
COOLDOWN_SEC = 2.0
SIMILARITY_SAME = 0.92

last_sent_at = 0.0

# ------------------ OVERLAY ------------------

class Overlay:

    def __init__(self):

        self.root = tk.Tk()

        self.root.title("Interview Helper")

        width = 720  # 600 + 20%
        height = 264 # 220 + 20%
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.root.configure(bg="#111")

        self.root.attributes("-topmost", True)

        self.root.overrideredirect(True)

        self.root.attributes("-alpha", 0.5)

        self.question = tk.Label(
            self.root,
            text="Waiting for question...",
            fg="white",
            bg="#111",
            font=("Arial", 14),
            wraplength=width - 20,
            justify="left"
        )

        self.question.pack(pady=10, padx=10)

        self.answer = tk.Label(
            self.root,
            text="",
            fg="#7CFC00",
            bg="#111",
            font=("Arial", 13),
            wraplength=width - 20,
            justify="left"
        )

        self.answer.pack(pady=10, padx=10)

    def update(self, question, answer):

        self.question.config(text=question)

        self.answer.config(text=answer)

        self.root.update()


overlay = Overlay()

# ------------------ OCR HELPERS ------------------


def clean_text(raw: str) -> str:

    s = raw.replace("\n", " ").replace("\r", " ")

    s = re.sub(r"[@©®™•■□◆◇▶►◄✓✔✕✖]+", " ", s)

    s = re.sub(r"[^0-9A-Za-zА-Яа-я_().,:;?!\-\s]", " ", s)

    s = re.sub(r"\s+", " ", s).strip()

    return s


def normalize(s: str) -> str:

    s = s.lower()

    s = re.sub(r"[,:;!?\-]+", " ", s)

    s = re.sub(r"\s+", " ", s).strip()

    return s


def similarity(a: str, b: str) -> float:

    if not a or not b:
        return 0.0

    return difflib.SequenceMatcher(None, a, b).ratio()


# ------------------ GPT ------------------


def ask_gpt(question_ocr: str) -> str:

    resp = client.chat.completions.create(
        model="gpt-5.2",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты помощник для технического бекенд интервью.\n"
                    "Отвечай ТОЛЬКО на русском.\n"
                    "Формат: Короткое определение (1 предложение). Краткое объяснение (2-3 предложения). При необходимости упомяни пример, инструмент или архитектурный аспект.\n"
                    "Ответ должен быть ёмким, понятным, демонстрировать понимание темы, 40–80 слов максимум\n"
                )
            },
            {"role": "user", "content": question_ocr}
        ],
    )

    return resp.choices[0].message.content.strip()


# ------------------ MAIN LOOP ------------------


def main_loop():

    global last_sent_at
    global last_hash

    with mss.mss() as sct:

        while True:

            img = np.array(sct.grab(monitor))

            current_hash = hashlib.md5(img.tobytes()).hexdigest()

            if current_hash == last_hash:
                time.sleep(POLL_SECONDS)
                continue
            
            print(f"[*] Screen changed (hash: {current_hash[:8]}...)")

            last_hash = current_hash

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            gray = cv2.resize(gray, None, fx=2, fy=2)

            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

            try:
                raw = pytesseract.image_to_string(thresh, config="--psm 6")
            except:
                time.sleep(0.5)
                continue

            cleaned = clean_text(raw)
            print(f"[*] OCR result: '{cleaned[:50]}...'")

            if len(cleaned) < MIN_LEN:
                print(f"[!] Text too short ({len(cleaned)} < {MIN_LEN}), skipping GPT.")
                continue

            now = time.time()
            if (now - last_sent_at) < COOLDOWN_SEC:
                # If the screen changed but we are on cooldown, we should NOT update last_hash yet
                # so that we catch it on the next loop after cooldown expires.
                # However, your request is "immediate". Let's lower cooldown to 2s.
                print(f"[-] Cooldown active ({now - last_sent_at:.1f}s < {COOLDOWN_SEC}s)")
                last_hash = None # Reset last_hash so we try this screen again immediately after cooldown
                time.sleep(0.2)
                continue

            print("[!!!] Screen changed + length OK. Sending to GPT...")

            try:
                answer = ask_gpt(cleaned)
            except Exception as e:
                answer = f"API error: {e}"

            overlay.update(cleaned, answer)
            last_sent_at = now

            time.sleep(POLL_SECONDS)


threading.Thread(target=main_loop, daemon=True).start()

try:
    overlay.root.mainloop()
except KeyboardInterrupt:
    print("\n[!] Exiting...")