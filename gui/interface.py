import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from scripts.scorebook import ROMAN_MAP
from models.linear_regression import LinearRegressionModel
from models.polynomial_regression import PolynomialRegressionModel


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


def submit_linear_regression():
    if validate_inputs():
        # Invert parking values
        parking_garage_value = 0 if garage_var.get() else 1
        parking_outdoor_value = 0 if parking_var.get() else 1

        # Collect apartment data from inputs
        new_apartment = {
            "Price": 0,
            "Municipality": municipality_var.get(),
            "Area_m2": float(size_var.get()),
            "Rooms": float(rooms_var.get()),
            "Floor": floor_var.get(),
            "Type": building_var.get(),
            "Condition": condition_var.get(),
            "Heating": heating_var.get(),
            "Parking_garage": parking_garage_value,
            "Parking_outdoor": parking_outdoor_value
        }

        # Load the trained linear regression model
        model = LinearRegressionModel()
        prediction = model.predict(new_apartment)

        # Create custom popup window for displaying prediction
        popup = tk.Toplevel(root)
        popup.title("Predicted Price - Linear")

        # Set popup size
        popup_width = 400
        popup_height = 200

        # Center popup relative to main window
        root_x = root.winfo_x()
        root_y = root.winfo_y()
        root_width = root.winfo_width()
        root_height = root.winfo_height()

        pos_x = root_x + (root_width // 2) - (popup_width // 2)
        pos_y = root_y + (root_height // 2) - (popup_height // 2)

        popup.geometry(f"{popup_width}x{popup_height}+{pos_x}+{pos_y}")
        popup.resizable(False, False)

        # Title inside popup
        tk.Label(
            popup, text="Procena vrednosti stana (linearna regresija)",
            font=("Arial", 13, "bold")
        ).pack(pady=(20, 10))

        # Predicted price label
        tk.Label(
            popup, text=f"{prediction} €",
            font=("Arial", 16, "bold"), fg="green"
        ).pack(pady=10)

        # Close button
        tk.Button(
            popup, text="Close", command=popup.destroy, font=default_font
        ).pack(pady=10)


def submit_polynomial_regression():
    if validate_inputs():
        # Invert parking values
        parking_garage_value = 0 if garage_var.get() else 1
        parking_outdoor_value = 0 if parking_var.get() else 1

        # Collect apartment data from inputs
        new_apartment = {
            "Price": 0,
            "Municipality": municipality_var.get(),
            "Area_m2": float(size_var.get()),
            "Rooms": float(rooms_var.get()),
            "Floor": floor_var.get(),
            "Type": building_var.get(),
            "Condition": condition_var.get(),
            "Heating": heating_var.get(),
            "Parking_garage": parking_garage_value,
            "Parking_outdoor": parking_outdoor_value
        }

        # Load the trained polynomial regression model
        model = PolynomialRegressionModel()
        prediction = model.predict(new_apartment)

        # Create custom popup window for displaying prediction
        popup = tk.Toplevel(root)
        popup.title("Predicted Price - Polynomial")

        # Set popup size
        popup_width = 400
        popup_height = 200

        # Center popup relative to main window
        root_x = root.winfo_x()
        root_y = root.winfo_y()
        root_width = root.winfo_width()
        root_height = root.winfo_height()

        pos_x = root_x + (root_width // 2) - (popup_width // 2)
        pos_y = root_y + (root_height // 2) - (popup_height // 2)

        popup.geometry(f"{popup_width}x{popup_height}+{pos_x}+{pos_y}")
        popup.resizable(False, False)

        # Title inside popup
        tk.Label(
            popup, text="Procena vrednosti stana (polinomska regresija)",
            font=("Arial", 13, "bold")
        ).pack(pady=(20, 10))

        # Predicted price label
        tk.Label(
            popup, text=f"{prediction} €",
            font=("Arial", 16, "bold"), fg="blue"
        ).pack(pady=10)

        # Close button
        tk.Button(
            popup, text="Close", command=popup.destroy, font=default_font
        ).pack(pady=10)


# Load data
df = pd.read_csv("../data/processed/serbian_apartments_clean.csv")
municipalities = df["Municipality"].dropna().unique().tolist()
rooms = sorted(df["Rooms"].dropna().astype(float).unique().tolist())
types = df["Type"].dropna().unique().tolist()
condition = df["Condition"].dropna().unique().tolist()
heating = df["Heating"].dropna().unique().tolist()

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

# Checkboxes for parking
garage_var = tk.IntVar()
parking_var = tk.IntVar()
tk.Checkbutton(main_frame, text="Garaža", variable=garage_var, font=default_font).grid(row=10, column=0, pady=5)
tk.Checkbutton(main_frame, text="Parking", variable=parking_var, font=default_font).grid(row=10, column=1, pady=5)

main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)

btn_linear = tk.Button(main_frame, text="Linearna regresija", command=submit_linear_regression, font=default_font)
btn_linear.grid(row=11, column=0, pady=15, sticky="EW", padx=(0, 5))

btn_polynomial = tk.Button(main_frame, text="Polinomska regresija", command=submit_polynomial_regression, font=default_font)
btn_polynomial.grid(row=11, column=1, pady=15, sticky="EW", padx=(5, 0))

# Run GUI
root.mainloop()
