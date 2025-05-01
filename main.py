from tkinter import *
from PIL import Image, ImageTk
import pandas as pd
import random

BACKGROUND_COLOR = "#B1DDC6"
current_card = {}
to_learn={}


try:
    data = pd.read_csv("answer_to_learn.csv", usecols=["Question", "Answer"])
except FileNotFoundError:
    original_data = pd.read_csv("Q_A.csv")
    to_learn = original_data.to_dict(orient="records")
else:
    to_learn = data.to_dict(orient="records")


window = Tk()
window.title("Knowledge-BD")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)


front_bg_img = ImageTk.PhotoImage(Image.open("images/b3.PNG"))  
back_bg_img = ImageTk.PhotoImage(Image.open("images/b1.PNG"))   

canvas = Canvas(window, width=800, height=400, bg=BACKGROUND_COLOR, highlightthickness=0)
card_bg = canvas.create_image(400, 200, image=front_bg_img)  
card_question = canvas.create_text(400, 120, text="", font=("Ariel", 20, "italic"), width=600)
card_answer = canvas.create_text(400, 250, text="", font=("Ariel", 20, "bold"),width=600)
canvas.grid(row=0, column=0, columnspan=2)

flip_timer=None


def next_card():
    global current_card, flip_timer
    if flip_timer:
        window.after_cancel(flip_timer)

    current_card = random.choice(to_learn)
    canvas.itemconfig(card_bg, image=front_bg_img)
    canvas.itemconfig(card_question, text="Question", fill="black")
    canvas.itemconfig(card_answer, text=current_card["Question"], fill="black")

    flip_timer=window.after(3000,flip_card)


def flip_card():
    canvas.itemconfig(card_bg, image=back_bg_img)
    canvas.itemconfig(card_question, text="Answer",fill="white")
    canvas.itemconfig(card_answer, text=current_card["Answer"], fill="white")

def is_known():
    to_learn.remove(current_card)
    data=pd.DataFrame(to_learn)
    data.to_csv("answer_to_learn.csv", index=False)
    next_card()


cross_image = ImageTk.PhotoImage(Image.open("images/wrong.png"))
unknown_button = Button(image=cross_image, highlightthickness=0, border=0, command=next_card)
unknown_button.grid(row=1, column=0)

check_image = ImageTk.PhotoImage(Image.open("images/right.png"))
known_button = Button(image=check_image, highlightthickness=0, border=0, command=is_known)
known_button.grid(row=1, column=1)


next_card()
window.mainloop()
