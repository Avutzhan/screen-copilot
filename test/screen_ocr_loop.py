import mss
import cv2
import pytesseract
import numpy as np
import time
from openai import OpenAI

client = OpenAI()

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

monitor = {
    "top": 94,
    "left": 297,
    "width": 1603,
    "height": 361
}

last_text = ""


def clean_text(text):

    lines = text.split("\n")

    lines = [l.strip() for l in lines if len(l.strip()) > 5]

    return " ".join(lines)


def ask_gpt(question):

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "Ты помощник для технического интервью. Отвечай ТОЛЬКО на русском языке. Ответ максимум 1-2 предложения."
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )

    return response.choices[0].message.content


with mss.mss() as sct:

    while True:

        img = np.array(sct.grab(monitor))

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        gray = cv2.resize(gray, None, fx=2, fy=2)

        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        text = pytesseract.image_to_string(thresh, config="--psm 6")

        text = clean_text(text)

        if text != last_text and len(text) > 15:

            print("\nDetected question:")
            print(text)

            answer = ask_gpt(text)

            print("\nGPT answer:")
            print(answer)

            last_text = text

        time.sleep(1)