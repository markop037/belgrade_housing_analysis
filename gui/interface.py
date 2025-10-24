from PySide6 import QtCore, QtGui, QtWidgets
import sys
import pandas as pd
from PySide6.QtCore import Qt

from scripts.scorebook import ROMAN_MAP
from models.polynomial_regression import PolynomialRegressionModel


class ApartmentApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Belgrade Apartment Price Estimator")
        self.setFixedSize(460, 580)
        self._load_data()
        self._build_ui()
        self._apply_styles()

    def _load_data(self):
        df = pd.read_csv("../data/processed/serbian_apartments_clean.csv")
        self.municipalities = df["Municipality"].dropna().unique().tolist()
        self.rooms = sorted(df["Rooms"].dropna().astype(float).unique().tolist())
        self.types = df["Type"].dropna().unique().tolist()
        self.condition = df["Condition"].dropna().unique().tolist()
        self.heating = df["Heating"].dropna().unique().tolist()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QtWidgets.QLabel("Enter Apartment Details")
        title.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Weight.Bold))
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QtWidgets.QLabel("All fields are required for an accurate prediction.")
        subtitle.setStyleSheet("color: #666;")
        subtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        # City (readonly)
        self.city_le = QtWidgets.QLineEdit("Belgrade")
        self.city_le.setStyleSheet("color: black")
        self.city_le.setReadOnly(True)
        form.addRow("City:", self.city_le)

        # Municipality
        self.municipality_cb = QtWidgets.QComboBox()
        self.municipality_cb.addItems(self.municipalities)
        self.municipality_cb.setEditable(False)
        form.addRow("Municipality:", self.municipality_cb)

        # Size
        self.size_le = QtWidgets.QLineEdit()
        self.size_le.setStyleSheet("color: black;")
        self.size_le.setPlaceholderText("e.g. 65")
        form.addRow("Area (m²):", self.size_le)

        # Rooms
        self.rooms_cb = QtWidgets.QComboBox()
        self.rooms_cb.addItems([str(r) for r in self.rooms])
        self.rooms_cb.setEditable(False)
        form.addRow("Number of Rooms:", self.rooms_cb)

        # Type
        self.type_cb = QtWidgets.QComboBox()
        self.type_cb.addItems(self.types)
        self.type_cb.setEditable(False)
        form.addRow("Building Type:", self.type_cb)

        # Condition
        self.condition_cb = QtWidgets.QComboBox()
        self.condition_cb.addItems(self.condition)
        self.condition_cb.setEditable(False)
        form.addRow("Condition:", self.condition_cb)

        # Heating
        self.heating_cb = QtWidgets.QComboBox()
        self.heating_cb.addItems(self.heating)
        self.heating_cb.setEditable(False)
        form.addRow("Heating:", self.heating_cb)

        # Total floors
        self.floor_total_le = QtWidgets.QLineEdit()
        self.floor_total_le.setStyleSheet("color: black;")
        self.floor_total_le.setPlaceholderText("Enter total floors")
        form.addRow("Total Floors in Building:", self.floor_total_le)

        # Floor (combobox updated dynamically)
        self.floor_cb = QtWidgets.QComboBox()
        self.floor_cb.setEditable(False)
        form.addRow("Apartment Floor:", self.floor_cb)

        layout.addLayout(form)

        # Connect floor_total change to update
        self.floor_total_le.textChanged.connect(self.update_floors)

        # Parking checkboxes
        park_layout = QtWidgets.QHBoxLayout()
        self.garage_cb = QtWidgets.QCheckBox("Garage")
        self.parking_cb = QtWidgets.QCheckBox("Outdoor Parking")
        park_layout.addWidget(self.garage_cb)
        park_layout.addWidget(self.parking_cb)
        layout.addLayout(park_layout)

        btn_layout = QtWidgets.QHBoxLayout()
        self.poly_btn = QtWidgets.QPushButton("Calculate Price")
        self.poly_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_layout.addWidget(self.poly_btn)
        layout.addLayout(btn_layout)

        self.poly_btn.clicked.connect(self.submit_polynomial_regression)

        # Initialize floors
        self.update_floors()

    def _apply_styles(self):
        # Refined modern style
        self.setStyleSheet(r"""
            QWidget {
                font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
                font-size: 11pt;
                background-color: #f7f8fa;
            }

            QComboBox {
                color: black;
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 3px;
            }

            QComboBox:hover {
                border: 1px solid #888;
            }

            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #f0f0f0;
                selection-color: black;
            }

            QComboBox QAbstractItemView::item:hover {
                background-color: #e6f2ff;
                color: black;
            }

            QLineEdit, QComboBox {
                padding: 6px 8px;
                border: 1px solid #c0c0c0;
                border-radius: 6px;
                background: white;
            }

            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #4a90e2;
                box-shadow: 0 0 4px rgba(74,144,226,0.5);
            }

            QPushButton {
                padding: 8px 12px;
                border-radius: 8px;
                border: 1px solid #2c7bd9;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #4aa3ff, stop:1 #2c7bd9);
                color: white;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #66b2ff, stop:1 #3a8ef0);
                border: 1px solid #1f5cb8;
            }

            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #2c7bd9, stop:1 #1a63b3);
            }

            QLabel {
                color: #222;
            }
            
            QCheckBox {
                color: black;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid black;
                border-radius: 3px;
                background: transparent;
            }
            
            QCheckBox::indicator:checked {
                background-color: black; /* makes the checkmark visible */
                image: none;
            }
        """)

    def update_floors(self):
        text = self.floor_total_le.text().strip()
        try:
            total = int(text) if text else 0
            if total < 0:
                total = 0
        except ValueError:
            total = 0

        options = [f"PR/{total}", f"VPR/{total}"]
        for roman, value in ROMAN_MAP.items():
            if value <= total:
                options.append(f"{roman}/{total}")

        self.floor_cb.clear()
        if options:
            self.floor_cb.addItems(options)
            self.floor_cb.setCurrentIndex(0)

    def validate_inputs(self):
        required = {
            "Municipality": self.municipality_cb.currentText(),
            "Area": self.size_le.text(),
            "Rooms": self.rooms_cb.currentText(),
            "Building Type": self.type_cb.currentText(),
            "Condition": self.condition_cb.currentText(),
            "Heating": self.heating_cb.currentText(),
            "Total Floors": self.floor_total_le.text(),
            "Apartment Floor": self.floor_cb.currentText(),
        }
        for name, val in required.items():
            if not val or not str(val).strip():
                QtWidgets.QMessageBox.critical(self, "Error", f"Field '{name}' cannot be empty!")
                return False

        try:
            size = float(self.size_le.text())
            if size < 0:
                QtWidgets.QMessageBox.critical(self, "Error", "Area cannot be negative!")
                return False
        except ValueError:
            QtWidgets.QMessageBox.critical(self, "Error", "Area must be a number!")
            return False

        try:
            total_floors = int(self.floor_total_le.text())
            if total_floors < 0:
                QtWidgets.QMessageBox.critical(self, "Error", "Total floors cannot be negative!")
                return False
        except ValueError:
            QtWidgets.QMessageBox.critical(self, "Error", "Total floors must be an integer!")
            return False

        return True

    def _collect_apartment(self):
        parking_garage_value = 0 if self.garage_cb.isChecked() else 1
        parking_outdoor_value = 0 if self.parking_cb.isChecked() else 1

        new_apartment = {
            "Price": 0,
            "Municipality": self.municipality_cb.currentText(),
            "Area_m2": float(self.size_le.text()),
            "Rooms": float(self.rooms_cb.currentText()),
            "Floor": self.floor_cb.currentText(),
            "Type": self.type_cb.currentText(),
            "Condition": self.condition_cb.currentText(),
            "Heating": self.heating_cb.currentText(),
            "Parking_garage": parking_garage_value,
            "Parking_outdoor": parking_outdoor_value,
        }
        return new_apartment

    def _show_prediction_popup(self, title, prediction, color="green"):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle(title)
        dlg.setFixedSize(420, 200)

        v = QtWidgets.QVBoxLayout(dlg)
        lbl_title = QtWidgets.QLabel("Estimated Apartment Value")
        lbl_title.setFont(QtGui.QFont("Arial", 13, QtGui.QFont.Weight.Bold))
        lbl_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        v.addWidget(lbl_title)

        lbl_price = QtWidgets.QLabel(f"{prediction} €")
        lbl_price.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Weight.Bold))
        lbl_price.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        lbl_price.setStyleSheet(f"color: {color};")
        v.addWidget(lbl_price)

        btn = QtWidgets.QPushButton("Close")
        btn.clicked.connect(dlg.accept)
        btn.setFixedWidth(100)
        h = QtWidgets.QHBoxLayout()
        h.addStretch()
        h.addWidget(btn)
        h.addStretch()
        v.addLayout(h)

        dlg.exec()

    def submit_polynomial_regression(self):
        if not self.validate_inputs():
            return
        new_apartment = self._collect_apartment()
        model = PolynomialRegressionModel()
        prediction = model.predict(new_apartment)
        self._show_prediction_popup("Predicted Price", prediction, color="#1b63d6")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ApartmentApp()
    screen = app.primaryScreen().availableGeometry()
    x = (screen.width() - window.width()) // 2
    y = (screen.height() - window.height()) // 2
    window.move(x, y)
    window.show()
    sys.exit(app.exec())
