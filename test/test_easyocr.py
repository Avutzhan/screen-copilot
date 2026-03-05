import easyocr
import mss
import numpy as np

reader = easyocr.Reader(['ru','en'])

monitor = {
    "top": 320,
    "left": 410,
    "width": 900,
    "height": 250
}

with mss.mss() as sct:

    img = np.array(sct.grab(monitor))

results = reader.readtext(img)

text = " ".join([res[1] for res in results])

print("\nDetected text:")
print(text)