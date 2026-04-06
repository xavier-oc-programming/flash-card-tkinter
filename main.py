# main.py
from tkinter import *
import pandas
import random
import os

# -------------------- CONSTANTS --------------------
BACKGROUND_COLOR = "#B1DDC6"
CARD_W, CARD_H = 800, 526
LANG_FONT = ("Ariel", 40, "italic")
WORD_FONT = ("Ariel", 60, "bold")

# -------------------- PATHS (robust across run locations) --------------------
HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(HERE, "data")
IMG_DIR = os.path.join(HERE, "images")
DATA_SAVED = os.path.join(DATA_DIR, "words_to_learn.csv")
DATA_ORIG = os.path.join(DATA_DIR, "french_words.csv")

# -------------------- DATA --------------------
current_card = {}
to_learn = []

try:
    data = pandas.read_csv(DATA_SAVED)
except FileNotFoundError:
    original_data = pandas.read_csv(DATA_ORIG)
    to_learn = original_data.to_dict(orient="records")
else:
    to_learn = data.to_dict(orient="records")

# -------------------- TIMER STATE --------------------
flip_timer = None          # stores id from window.after(...)
is_front = True            # True: French/front, False: English/back

# -------------------- FUNCTIONS --------------------
def cancel_timer_if_any():
    """Cancel pending auto-flip safely and clear the timer id."""
    global flip_timer
    if flip_timer:
        try:
            window.after_cancel(flip_timer)
        except Exception:
            pass
        flip_timer = None

def next_card():
    """Pick a new random French word and schedule an auto-flip to English."""
    global current_card, flip_timer, is_front

    cancel_timer_if_any()

    # Finished deck handling
    if not to_learn:
        canvas.itemconfig(card_background, image=card_front_img)
        canvas.itemconfig(card_title, text="🎉 All done!", fill="black", font=LANG_FONT)
        canvas.itemconfig(card_word, text="You learned every word.", fill="black", font=WORD_FONT)
        canvas.unbind("<Button-1>")
        known_button.config(state=DISABLED)
        unknown_button.config(state=DISABLED)
        return

    current_card = random.choice(to_learn)
    is_front = True
    canvas.itemconfig(card_title, text="French", fill="black")
    canvas.itemconfig(card_word, text=current_card["French"], fill="black")
    canvas.itemconfig(card_background, image=card_front_img)

    # schedule auto-flip after 3s
    flip_timer = window.after(3000, flip_card)

def flip_card(event=None):
    """
    Toggle the card between French (front) and English (back).
    If this was a manual click before the auto timer fired, cancel that timer.
    """
    global is_front, flip_timer

    # Manual click before auto-flip? cancel it.
    if event is not None and is_front and flip_timer:
        cancel_timer_if_any()

    if is_front:
        canvas.itemconfig(card_title, text="English", fill="white")
        canvas.itemconfig(card_word, text=current_card["English"], fill="white")
        canvas.itemconfig(card_background, image=card_back_img)
        is_front = False
    else:
        canvas.itemconfig(card_title, text="French", fill="black")
        canvas.itemconfig(card_word, text=current_card["French"], fill="black")
        canvas.itemconfig(card_background, image=card_front_img)
        is_front = True

    # If flip was triggered by auto timer, clear the stored id
    if event is None and flip_timer:
        flip_timer = None

def is_known():
    """User knows the word: remove it, save progress, and advance."""
    cancel_timer_if_any()
    try:
        to_learn.remove(current_card)
    except ValueError:
        pass
    pandas.DataFrame(to_learn).to_csv(DATA_SAVED, index=False)
    next_card()

def is_unknown():
    """User doesn't know the word: just move on to a new one."""
    next_card()

# -------------------- UI SETUP --------------------
window = Tk()
window.title("Flashy")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)

canvas = Canvas(width=CARD_W, height=CARD_H, bg=BACKGROUND_COLOR, highlightthickness=0)
card_front_img = PhotoImage(file=os.path.join(IMG_DIR, "card_front.png"))
card_back_img  = PhotoImage(file=os.path.join(IMG_DIR, "card_back.png"))
card_background = canvas.create_image(CARD_W // 2, CARD_H // 2, image=card_front_img)

card_title = canvas.create_text(CARD_W // 2, 150, text="", font=LANG_FONT, fill="black")
card_word  = canvas.create_text(CARD_W // 2, 263, text="", font=WORD_FONT, fill="black")

canvas.grid(row=0, column=0, columnspan=2)

# Click anywhere on the card to flip manually
canvas.bind("<Button-1>", flip_card)

# Buttons
cross_image = PhotoImage(file=os.path.join(IMG_DIR, "wrong.png"))
unknown_button = Button(image=cross_image, highlightthickness=0, borderwidth=0,
                        bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR,
                        command=is_unknown)
unknown_button.grid(row=1, column=0)

check_image = PhotoImage(file=os.path.join(IMG_DIR, "right.png"))
known_button = Button(image=check_image, highlightthickness=0, borderwidth=0,
                      bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR,
                      command=is_known)
known_button.grid(row=1, column=1)

# -------------------- START --------------------
next_card()
window.mainloop()
