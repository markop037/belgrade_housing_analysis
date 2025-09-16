import tkinter as tk
from tkinter import ttk
import pandas as pd

# Load from CSV file
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

# Center window on the screen
window_width = 400
window_height = 450  # slightly taller to fit the title
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Define a default font
default_font = ("Arial", 11)

# Main frame (centered)
main_frame = ttk.Frame(root, padding="15 15 15 15")
main_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center frame in window

# Title label
title_label = tk.Label(main_frame, text="Unesite nekretninu", font=("Arial", 14, "bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

# Function to create a label + widget in a row
def add_row(row, label_text, widget):
    tk.Label(main_frame, text=label_text, font=default_font).grid(row=row, column=0, pady=5, sticky="EW")
    widget.grid(row=row, column=1, pady=5, sticky="EW")

# City (fixed as Belgrade)
city_var = tk.StringVar(value="Beograd")
add_row(1, "Grad:", tk.Entry(main_frame, textvariable=city_var, state="readonly", font=default_font))

# Municipality
municipality_var = tk.StringVar()
add_row(2, "Opština:", ttk.Combobox(main_frame, textvariable=municipality_var, values=municipalities, state="readonly", font=default_font))

# Size
size_var = tk.StringVar()
add_row(3, "Kvadratura (m²):", tk.Entry(main_frame, textvariable=size_var, font=default_font))

# Rooms
rooms_var = tk.StringVar()
add_row(4, "Broj soba:", ttk.Combobox(main_frame, textvariable=rooms_var, values=rooms, state="readonly", font=default_font))

# Building type
building_var = tk.StringVar()
add_row(5, "Tip objekta:", ttk.Combobox(main_frame, textvariable=building_var, values=types, state="readonly", font=default_font))

# Condition
condition_var = tk.StringVar()
add_row(6, "Stanje objekta:", ttk.Combobox(main_frame, textvariable=condition_var, values=condition, state="readonly", font=default_font))

# Heating
heating_var = tk.StringVar()
add_row(7, "Grejanje:", ttk.Combobox(main_frame, textvariable=heating_var, values=heating, state="readonly", font=default_font))

# Garage & Parking checkboxes (centered)
garage_var = tk.IntVar()
parking_var = tk.IntVar()
tk.Checkbutton(main_frame, text="Garaža", variable=garage_var, font=default_font).grid(row=8, column=0, pady=5)
tk.Checkbutton(main_frame, text="Parking", variable=parking_var, font=default_font).grid(row=8, column=1, pady=5)

# Make columns same width and centered
main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)

root.mainloop()
