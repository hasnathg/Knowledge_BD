from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd
import random



BACKGROUND_COLOR = "#B1DDC6"
flip_time_ms = 5000  

current_card = {}
to_learn = []
all_data = []
flip_timer = None
is_paused = False


def load_data():
    global all_data
    try:
        all_data = pd.read_csv("Q_A.csv", usecols=["Category", "Question", "Answer"]).to_dict(orient="records")
    except Exception as e:
        print("Error loading CSV:", e)
        all_data = []



def filter_by_category(selected_category):
    global to_learn
    if selected_category == "All":
        to_learn = all_data.copy()
    else:
        to_learn = [item for item in all_data if item["Category"] == selected_category]
    next_card()



def reset_deck():
    global to_learn
    to_learn = all_data.copy()



def next_card():
    global current_card, flip_timer, is_paused
    if flip_timer:
        window.after_cancel(flip_timer)

    if not to_learn:
        reset_deck()

    current_card = random.choice(to_learn)
    canvas.itemconfig(card_bg, image=front_bg_img)
    canvas.itemconfig(card_question, text="Question", fill="black")
    canvas.itemconfig(card_answer, text=current_card["Question"], fill="black")

    if not is_paused:
        start_flip_timer()

    update_progress_label()



def start_flip_timer():
    global flip_timer
    flip_timer = window.after(flip_time_ms, flip_card)



def flip_card():
    canvas.itemconfig(card_bg, image=back_bg_img)
    canvas.itemconfig(card_question, text="Answer", fill="white")
    canvas.itemconfig(card_answer, text=current_card["Answer"], fill="white")



def is_known():
    if current_card in to_learn:
        to_learn.remove(current_card)
    next_card()



def is_unknown():
    next_card()



def start_game():
    global is_paused
    is_paused = False
    selected = category_var.get()
    filter_by_category(selected)



def pause_flip():
    global is_paused, flip_timer
    if flip_timer:
        window.after_cancel(flip_timer)
    is_paused = True



def resume_flip():
    global is_paused
    if not is_paused:
        return
    is_paused = False
    start_flip_timer()



def update_progress_label():
    known = len(all_data) - len(to_learn)
    total = len(all_data)
    percent = (known / total * 100) if total > 0 else 0
    progress_label.config(text=f"Cards left: {len(to_learn)} | Known cards: {known} ({percent:.0f}%)")



window = Tk()
window.title("Knowledge-BD")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)


front_bg_img = ImageTk.PhotoImage(Image.open("images/b3.PNG"))
back_bg_img = ImageTk.PhotoImage(Image.open("images/b1.PNG"))
cross_image = ImageTk.PhotoImage(Image.open("images/wrong.png"))
check_image = ImageTk.PhotoImage(Image.open("images/right.png"))


canvas = Canvas(window, width=800, height=400, bg=BACKGROUND_COLOR, highlightthickness=0)
card_bg = canvas.create_image(400, 200, image=front_bg_img)
card_question = canvas.create_text(400, 120, text="", font=("Ariel", 20, "italic"), width=600)
card_answer = canvas.create_text(400, 250, text="", font=("Ariel", 20, "bold"), width=600)
canvas.grid(row=2, column=0, columnspan=3)


load_data()


category_var = StringVar()
categories = sorted(set([item["Category"] for item in all_data]))
category_dropdown = ttk.Combobox(window, textvariable=category_var, width=20)
category_dropdown['values'] = ["All"] + categories
category_dropdown.current(0)
category_dropdown.grid(row=0, column=0, sticky="w", padx=10)


review_var = StringVar()
review_dropdown = ttk.Combobox(window, textvariable=review_var, width=15)
review_dropdown['values'] = ["All", "Known", "Unknown"] 
review_dropdown.current(0)
review_dropdown.grid(row=0, column=1, padx=10)


search_var = StringVar()
search_entry = Entry(window, textvariable=search_var, width=30)
search_entry.grid(row=0, column=2, padx=10)
search_entry.insert(0, "Search...")

def clear_search(event):
    if search_entry.get() == "Search...":
        search_entry.delete(0, END)

search_entry.bind("<FocusIn>", clear_search)


button_frame = Frame(window, bg=BACKGROUND_COLOR)
button_frame.grid(row=1, column=0, columnspan=3, pady=(10, 20))

start_button = Button(button_frame, text="Start", command=start_game, width=10)
start_button.grid(row=0, column=0, padx=5)

pause_button = Button(button_frame, text="Pause", command=pause_flip, width=10)
pause_button.grid(row=0, column=1, padx=5)

resume_button = Button(button_frame, text="Resume", command=resume_flip, width=10)
resume_button.grid(row=0, column=2, padx=5)


action_button_frame = Frame(window, bg=BACKGROUND_COLOR)
action_button_frame.grid(row=3, column=0, columnspan=3, pady=10)

unknown_button = Button(action_button_frame, image=cross_image, highlightthickness=0, border=0, command=is_unknown)
unknown_button.grid(row=0, column=0, padx=50)

known_button = Button(action_button_frame, image=check_image, highlightthickness=0, border=0, command=is_known)
known_button.grid(row=0, column=1, padx=50)


progress_label = Label(window, text="Cards left: 0 | Known cards: 0 (0%)", bg=BACKGROUND_COLOR, font=("Arial", 14))
progress_label.grid(row=4, column=0, columnspan=3, pady=10)

window.mainloop()

