import tkinter as tk
from PIL import Image, ImageTk
import mss
import numpy as np

class RegionSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes("-alpha", 0.3)
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.config(cursor="cross")
        
        self.canvas = tk.Canvas(self.root, cursor="cross", bg="grey")
        self.canvas.pack(fill="both", expand=True)

        self.start_x = None
        self.start_y = None
        self.rect = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=2)

    def on_move_press(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        end_x, end_y = (event.x, event.y)
        
        top = min(self.start_y, end_y)
        left = min(self.start_x, end_x)
        width = abs(end_x - self.start_x)
        height = abs(end_y - self.start_y)

        print("\nSelected region (MSS format):")
        print(f"\"top\": {top},")
        print(f"\"left\": {left},")
        print(f"\"width\": {width},")
        print(f"\"height\": {height}")
        
        self.root.destroy()

if __name__ == "__main__":
    print("Click and drag to select a region. Press ESC to cancel.")
    app = RegionSelector()
    app.root.mainloop()
