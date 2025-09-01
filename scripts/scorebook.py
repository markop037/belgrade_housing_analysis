# Floor: ground floor ("PR" or "VPR") = 0, last floor = 0, all others = 1
FLOOR_MAP = {"PR": 0, "VPR": 0}

# Parking: both "garaža" and "parking" = 2, none = 0, one of them = 1
PARKING_KEYWORDS = ["garaža", "parking"]

# Type: "Novogradnja" = 1, others = 0
TYPE_MAP = {"Novogradnja": 1}

# Condition: "Lux" = 2, "Renovirano" = 1, others = 0
CONDITION_MAP = {"Lux": 2, "Renovirano": 1}

# Heating: numerical ranking
HEATING_MAP = {"Toplotne pumpe": 4, "Podno": 3, "CG": 2, "Norveški radijatori": 1}

# Roman numerals mapping
ROMAN_MAP = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
    "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10,
    "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15
}
