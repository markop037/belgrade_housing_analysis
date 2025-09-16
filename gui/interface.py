import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from scripts.scorebook import ROMAN_MAP


def add_row(row, label_text, widget):
    tk.Label(main_frame, text=label_text, font=default_font).grid(row=row, column=0, pady=5, sticky="EW")
    widget.grid(row=row, column=1, pady=5, sticky="EW")


def update_floors(*args):
    try:
        total = int(floor_total_var.get())
        if total < 0:
            total = 0
    except ValueError:
        total = 0

    options = ["PR", "VPR"]
    for roman, value in ROMAN_MAP.items():
        if value <= total:
            options.append(f"{roman}/{total}")

    floor_menu['values'] = options
    if options:
        floor_var.set(options[0])
    else:
        floor_var.set("")


# Validation function
def validate_inputs():
    # Check required fields
    required_fields = {
        "Opština": municipality_var.get(),
        "Kvadratura": size_var.get(),
        "Broj soba": rooms_var.get(),
        "Tip objekta": building_var.get(),
        "Stanje objekta": condition_var.get(),
        "Grejanje": heating_var.get(),
        "Ukupan broj spratova": floor_total_var.get(),
        "Sprat stana": floor_var.get()
    }
    for field_name, value in required_fields.items():
        if not value.strip():
            messagebox.showerror("Greška", f"Polje '{field_name}' ne sme biti prazno!")
            return False

    # Check numeric fields
    try:
        float(size_var.get())
    except ValueError:
        messagebox.showerror("Greška", "Kvadratura mora biti broj!")
        return False

    try:
        int(floor_total_var.get())
    except ValueError:
        messagebox.showerror("Greška", "Ukupan broj spratova mora biti ceo broj!")
        return False

    return True


# Submit button
def submit():
    if validate_inputs():
        messagebox.showinfo("Uspešno", "Podaci su validni!")


# Load data
df = pd.read_csv("../data/processed/serbian_apartments_clean.csv")
municipalities = df["Municipality"].dropna().unique().tolist()
rooms = sorted(df["Rooms"].dropna().astype(float).unique().tolist())
types = df["Type"].dropna().unique().tolist()
types.append("Ostalo")
condition = df["Condition"].dropna().unique().tolist()
condition.append("Ostalo")
heating = df["Heating"].dropna().unique().tolist()
heating.append("Ostalo")

# Main window
root = tk.Tk()
root.title("Belgrade Housing Analysis")
root.resizable(False, False)
window_width = 400
window_height = 550
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

default_font = ("Arial", 11)
main_frame = ttk.Frame(root, padding="15 15 15 15")
main_frame.place(relx=0.5, rely=0.5, anchor="center")

# Title label
title_label = tk.Label(main_frame, text="Unesite nekretninu", font=("Arial", 14, "bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

# Input fields
city_var = tk.StringVar(value="Beograd")
add_row(1, "Grad:", tk.Entry(main_frame, textvariable=city_var, state="readonly", font=default_font))

municipality_var = tk.StringVar()
add_row(2, "Opština:", ttk.Combobox(main_frame, textvariable=municipality_var, values=municipalities, state="readonly", font=default_font))

size_var = tk.StringVar()
add_row(3, "Kvadratura (m²):", tk.Entry(main_frame, textvariable=size_var, font=default_font))

rooms_var = tk.StringVar()
add_row(4, "Broj soba:", ttk.Combobox(main_frame, textvariable=rooms_var, values=rooms, state="readonly", font=default_font))

building_var = tk.StringVar()
add_row(5, "Tip objekta:", ttk.Combobox(main_frame, textvariable=building_var, values=types, state="readonly", font=default_font))

condition_var = tk.StringVar()
add_row(6, "Stanje objekta:", ttk.Combobox(main_frame, textvariable=condition_var, values=condition, state="readonly", font=default_font))

heating_var = tk.StringVar()
add_row(7, "Grejanje:", ttk.Combobox(main_frame, textvariable=heating_var, values=heating, state="readonly", font=default_font))

floor_total_var = tk.StringVar()
add_row(8, "Ukupan broj spratova zgrade:", tk.Entry(main_frame, textvariable=floor_total_var, font=default_font))

floor_var = tk.StringVar()
floor_menu = ttk.Combobox(main_frame, textvariable=floor_var, state="readonly", font=default_font)
floor_menu.grid(row=9, column=1, pady=5, sticky="EW")
tk.Label(main_frame, text="Sprat stana:", font=default_font).grid(row=9, column=0, pady=5, sticky="EW")

floor_total_var.trace_add("write", update_floors)

garage_var = tk.IntVar()
parking_var = tk.IntVar()
tk.Checkbutton(main_frame, text="Garaža", variable=garage_var, font=default_font).grid(row=10, column=0, pady=5)
tk.Checkbutton(main_frame, text="Parking", variable=parking_var, font=default_font).grid(row=10, column=1, pady=5)

main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)

submit_btn = tk.Button(main_frame, text="Predikcija", command=submit, font=default_font)
submit_btn.grid(row=11, column=0, columnspan=2, pady=15)

# Run GUI
root.mainloop()
