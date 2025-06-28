from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pandas as pd
import random

BACKGROUND_COLOR = "#B1DDC6"
TIMER_DURATION = 10  

current_card = {}
to_learn = []
all_data = []
marked_cards = []
current_deck = []
flip_timer = None
is_paused = False
shuffle_mode = True
remaining_time = TIMER_DURATION
is_flipped = False

# Load data from CSV
def load_data():
    global all_data
    try:
        all_data = pd.read_csv("Q_A.csv", usecols=["Category", "Question", "Answer"]).to_dict(orient="records")
    except Exception as e:
        print("Error loading CSV:", e)
        all_data = []

def filter_by_category(selected_category):
    global to_learn, current_deck
    if selected_category == "All":
        current_deck = all_data.copy()
    else:
        current_deck = [item for item in all_data if item["Category"] == selected_category]
    to_learn = current_deck.copy()
    next_card()

def reset_deck():
    global to_learn
    to_learn = current_deck.copy()

def next_card():
    global current_card, flip_timer, is_paused, remaining_time, is_flipped
    if flip_timer:
        window.after_cancel(flip_timer)

    if not to_learn:
        update_progress_label()
        update_progress_bar()
        should_continue = messagebox.askyesno("Completed", "You've finished this category.\nDo you want to continue?")
        if not should_continue:
            return
        reset_deck()

        if not to_learn:
            messagebox.showinfo("No Cards", "No cards available to show.")
            return


    current_card = random.choice(to_learn) if shuffle_mode else to_learn[0]
    canvas.itemconfig(card_bg, image=front_bg_img)
    canvas.itemconfig(card_question, text="Question", fill="black")
    canvas.itemconfig(card_answer, text=current_card["Question"], fill="black")
    remaining_time = TIMER_DURATION
    is_flipped = False

    if not is_paused:
        update_timer()

    update_progress_label()
    update_progress_bar()


def update_timer():
    global remaining_time, flip_timer
    if remaining_time > 0:
        remaining_time -= 1
        timer_label.config(text=f"Time left: {remaining_time}s", fg="black", font=("Arial", 12, "bold"))
        flip_timer = window.after(1000, update_timer)
    else:
        timer_label.config(text="Time left: 0s", fg="red", font=("Arial", 12, "bold"))
        window.bell()  
        flash_timer_warning()
        flip_card()

        window.bell()

def flash_timer_warning():
    def toggle_flash(count=6):
        if count > 0:
            current_color = timer_label.cget("fg")
            new_color = "red" if current_color == BACKGROUND_COLOR else BACKGROUND_COLOR
            timer_label.config(fg=new_color)
            window.after(250, lambda: toggle_flash(count - 1))
        else:
            timer_label.config(fg="black", font=("Arial", 12, "bold"))  # Reset styling

    toggle_flash()




def flip_card():
    global is_flipped
    is_flipped = True
    canvas.itemconfig(card_bg, image=back_bg_img)
    canvas.itemconfig(card_question, text="Answer", fill="white")
    canvas.itemconfig(card_answer, text=current_card["Answer"], fill="white")
    is_flipped = True


def is_known():
    global is_flipped
    if not is_flipped:
        flip_card()
    else:
        if current_card in to_learn:
            to_learn.remove(current_card)
        next_card()

def is_unknown():
    global is_flipped
    if not is_flipped:
        flip_card()
    else:
        next_card()

def start_game():
    global is_paused
    is_paused = False
    selected = category_var.get()
    if selected == "Categories":  # default prompt
        messagebox.showwarning("Select Category", "Please select a category before starting.")
        return
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
    update_timer()

def toggle_shuffle():
    global shuffle_mode
    shuffle_mode = not shuffle_mode
    shuffle_button.config(text="Shuffle: ON" if shuffle_mode else "Shuffle: OFF")

def mark_for_review():
    if current_card not in marked_cards:
        marked_cards.append(current_card)
        messagebox.showinfo("Marked", "Card marked for review.")

# review card

def review_marked_cards():
    global to_learn, current_deck
    if not marked_cards:
        messagebox.showinfo("Review", "No marked cards to review.")
        return
    current_deck = marked_cards.copy()
    to_learn = current_deck.copy()
    next_card()

def unmark_card():
    if current_card in marked_cards:
        marked_cards.remove(current_card)
        messagebox.showinfo("Unmarked", "Card removed from review list.")
    else:
        messagebox.showinfo("Not Found", "This card is not in the marked list.")

def update_progress_label():
    known = len(current_deck) - len(to_learn)
    total = len(current_deck)
    percent = (known / total * 100) if total > 0 else 0
    progress_label.config(text=f"Cards left: {len(to_learn)} | Known: {known} ({percent:.0f}%)")

def update_progress_bar():
    known = len(current_deck) - len(to_learn)
    total = len(current_deck)
    progress_bar["value"] = known
    progress_bar["maximum"] = total if total > 0 else 1


# --- GUI Setup ---

window = Tk()
window.title("Knowledge-BD")
window.geometry("900x740")  

window.update_idletasks()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
size = tuple(int(_) for _ in window.geometry().split('+')[0].split('x'))
x = (screen_width - size[0]) // 2
y = (screen_height - size[1]) // 2
window.geometry(f"{size[0]}x{size[1]}+{x}+{y}")

window.config(padx=50, pady=40, bg=BACKGROUND_COLOR)  

# Load and resize images for buttons to smaller size (50x50)
def load_and_resize_image(path, size=(50, 50)):
    img = Image.open(path)
    img = img.resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)


front_bg_img = ImageTk.PhotoImage(Image.open("images/b3.PNG"))
back_bg_img = ImageTk.PhotoImage(Image.open("images/b1.PNG"))
cross_image = load_and_resize_image("images/wrong.png")
check_image = load_and_resize_image("images/right.png")
star_image = load_and_resize_image("images/star.png")

# Frames for better layout control
top_frame = Frame(window, bg=BACKGROUND_COLOR)
top_frame.grid(row=0, column=0, pady=(0, 10), sticky='n')

button_frame = Frame(window, bg=BACKGROUND_COLOR)
button_frame.grid(row=1, column=0, pady=(0, 15), sticky='n')

canvas_frame = Frame(window, bg=BACKGROUND_COLOR)
canvas_frame.grid(row=2, column=0, pady=(0, 8), sticky='n')

action_frame = Frame(window, bg=BACKGROUND_COLOR)
action_frame.grid(row=3, column=0, pady=(5, 8), sticky='n')

progress_frame = Frame(window, bg=BACKGROUND_COLOR)
progress_frame.grid(row=4, column=0, pady=(0, 0), sticky='n')

window.grid_columnconfigure(0, weight=1)

# Category Dropdown in top_frame
load_data()
category_var = StringVar()
categories = sorted(set([item["Category"] for item in all_data]))
# Insert "All" at front
dropdown_values = ["All"] + categories


category_dropdown = ttk.Combobox(top_frame, textvariable=category_var, values=dropdown_values, width=20, state="readonly")
category_dropdown.grid(row=0, column=0, padx=(0, 15), sticky='ew')
top_frame.grid_columnconfigure(0, weight=1)

category_var.set("Categories") 

def on_dropdown_click(event):
    if category_var.get() == "Categories":
       
        category_var.set('')
category_dropdown.bind('<Button-1>', on_dropdown_click)


# Control buttons in button_frame
start_button = Button(button_frame, text="Start", command=start_game, width=5)
pause_button = Button(button_frame, text="Pause", command=pause_flip, width=5)
resume_button = Button(button_frame, text="Resume", command=resume_flip, width=6)
shuffle_button = Button(button_frame, text="Shuffle: ON", command=toggle_shuffle, width=10)
review_button = Button(button_frame, text="Review Marked", command=review_marked_cards, width=12)
unmark_button = Button(button_frame, text="Unmark", command=unmark_card,  width=6)

start_button.grid(row=0, column=0, padx=5)
pause_button.grid(row=0, column=1, padx=5)
resume_button.grid(row=0, column=2, padx=5)
shuffle_button.grid(row=0, column=3, padx=5)
review_button.grid(row=0, column=4, padx=5)
unmark_button.grid(row=0, column=5, padx=5)


button_frame.grid_columnconfigure((0,1,2,3), weight=1)

# Canvas
canvas = Canvas(canvas_frame, width=800, height=350, bg=BACKGROUND_COLOR, highlightthickness=0)
canvas.grid(row=0, column=0, sticky='n')
card_bg = canvas.create_image(400, 175, image=front_bg_img)  # updated center y to half height
card_question = canvas.create_text(400, 110, text="", font=("Ariel", 20, "italic"), width=600)
card_answer = canvas.create_text(400, 230, text="", font=("Ariel", 20, "bold"), width=600)

# Action buttons 
unknown_button = Button(action_frame, image=cross_image, command=is_unknown, border=0)
known_button = Button(action_frame, image=check_image, command=is_known, border=0)
mark_button = Button(action_frame, image=star_image, command=mark_for_review, border=0)


unknown_button.grid(row=0, column=0, padx=15, pady=0)
known_button.grid(row=0, column=1, padx=15, pady=0)
mark_button.grid(row=0, column=2, padx=15, pady=0)


action_frame.grid_columnconfigure((0,1,2), weight=1)

# Progress label, bar and timer 
progress_label = Label(progress_frame, text="Cards left: 0 | Known: 0 (0%)", bg=BACKGROUND_COLOR, font=("Arial", 14))
progress_label.grid(row=0, column=0, pady=(0, 4))

progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=1, column=0, pady=(0, 6))

timer_label = Label(progress_frame, text="Time left: 0s", bg=BACKGROUND_COLOR, font=("Arial", 12))
timer_label.grid(row=2, column=0, pady=(0, 0))

progress_frame.grid_columnconfigure(0, weight=1)

window.mainloop()
