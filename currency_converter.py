
import sys
import json
import requests
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class CurrencyConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_key = "YOUR_API_KEY_HERE"  # Замените на ваш ключ
        self.base_url = "https://v6.exchangerate-api.com/v6"
        self.history_file = "conversion_history.json"
        self.history = []
        
        self.init_ui()
        self.load_history()
        
    def init_ui(self):
        self.setWindowTitle("Currency Converter")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Заголовок
        title_label = QLabel("Currency Converter")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        main_layout.addWidget(title_label)
        
        # Конвертер
        converter_group = QGroupBox("Convert Currency")
        converter_layout = QGridLayout(converter_group)
        
        # Сумма
        converter_layout.addWidget(QLabel("Amount:"), 0, 0)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount...")
        converter_layout.addWidget(self.amount_input, 0, 1, 1, 3)
        
        # Из валюты
        converter_layout.addWidget(QLabel("From:"), 1, 0)
        self.from_currency = QComboBox()
        self.populate_currencies(self.from_currency)
        converter_layout.addWidget(self.from_currency, 1, 1)
        
        # Кнопка обмена
        swap_btn = QPushButton("⇄")
        swap_btn.setFixedWidth(50)
        swap_btn.clicked.connect(self.swap_currencies)
        converter_layout.addWidget(swap_btn, 1, 2)
        
        # В валюту
        converter_layout.addWidget(QLabel("To:"), 1, 3)
        self.to_currency = QComboBox()
        self.populate_currencies(self.to_currency)
        converter_layout.addWidget(self.to_currency, 1, 4)
        
        # Кнопка конвертации
        convert_btn = QPushButton("Convert")
        convert_btn.clicked.connect(self.convert_currency)
        converter_layout.addWidget(convert_btn, 2, 0, 1, 5)
        
        # Результат
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        converter_layout.addWidget(self.result_label, 3, 0, 1, 5)
        
        main_layout.addWidget(converter_group)
        
        # История
        history_group = QGroupBox("Conversion History")
        history_layout = QVBoxLayout(history_group)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Date", "Amount", "From", "To", "Result"])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setAlternatingRowColors(True)
        history_layout.addWidget(self.history_table)
        
        # Кнопки истории
        history_buttons = QHBoxLayout()
        
        clear_history_btn = QPushButton("Clear History")
        clear_history_btn.clicked.connect(self.clear_history)
        history_buttons.addWidget(clear_history_btn)
        
        export_history_btn = QPushButton("Export History")
        export_history_btn.clicked.connect(self.export_history)
        history_buttons.addWidget(export_history_btn)
        
        import_history_btn = QPushButton("Import History")
        import_history_btn.clicked.connect(self.import_history)
        history_buttons.addWidget(import_history_btn)
        
        history_layout.addLayout(history_buttons)
        main_layout.addWidget(history_group)
        
        # Статус бар
        self.status_label = QLabel("Ready")
        self.statusBar().addWidget(self.status_label)
        
    def populate_currencies(self, combo_box):
        currencies = [
            "USD", "EUR", "GBP", "JPY", "RUB", "CNY", "INR", "BRL",
            "CAD", "AUD", "CHF", "KRW", "MXN", "TRY", "SEK", "NOK"
        ]
        combo_box.addItems(currencies)
        
    def validate_amount(self, amount_text):
        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            return amount
        except ValueError:
            return None
            
    def swap_currencies(self):
        from_idx = self.from_currency.currentIndex()
        to_idx = self.to_currency.currentIndex()
        self.from_currency.setCurrentIndex(to_idx)
        self.to_currency.setCurrentIndex(from_idx)
        
    def convert_currency(self):
        amount_text = self.amount_input.text().strip()
        amount = self.validate_amount(amount_text)
        
        if amount is None:
            QMessageBox.warning(self, "Invalid Input", 
                              "Please enter a valid positive number")
            return
            
        from_curr = self.from_currency.currentText()
        to_curr = self.to_currency.currentText()
        
        if from_curr == to_curr:
            QMessageBox.warning(self, "Invalid Selection", 
                              "Please select different currencies")
            return
            
        try:
            rate = self.get_exchange_rate(from_curr, to_curr)
            if rate is None:
                return
                
            result = amount * rate
            self.result_label.setText(f"{amount:.2f} {from_curr} = {result:.2f} {to_curr}")
            
            # Сохраняем в историю
            conversion = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "amount": amount,
                "from_currency": from_curr,
                "to_currency": to_curr,
                "rate": rate,
                "result": result
            }
            self.history.append(conversion)
            self.update_history_table()
            self.save_history()
            
            self.status_label.setText(f"Converted: {amount:.2f} {from_curr} → {result:.2f} {to_curr}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Conversion failed: {str(e)}")
            
    def get_exchange_rate(self, from_curr, to_curr):
        try:
            url = f"{self.base_url}/{self.api_key}/latest/{from_curr}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("result") == "success":
                rates = data.get("conversion_rates", {})
                if to_curr in rates:
                    return rates[to_curr]
                else:
                    QMessageBox.warning(self, "Error", f"Currency {to_curr} not found")
                    return None
            else:
                QMessageBox.warning(self, "API Error", "Failed to get exchange rates")
                return None
                
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Network Error", 
                               f"Failed to connect to API: {str(e)}")
            return None
            
    def update_history_table(self):
        self.history_table.setRowCount(len(self.history))
        for i, conv in enumerate(self.history):
            self.history_table.setItem(i, 0, QTableWidgetItem(conv["date"]))
            self.history_table.setItem(i, 1, QTableWidgetItem(f"{conv['amount']:.2f}"))
            self.history_table.setItem(i, 2, QTableWidgetItem(conv["from_currency"]))
            self.history_table.setItem(i, 3, QTableWidgetItem(conv["to_currency"]))
            self.history_table.setItem(i, 4, QTableWidgetItem(f"{conv['result']:.2f}"))
            
    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to save history: {str(e)}")
            
    def load_history(self):
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
            self.update_history_table()
        except FileNotFoundError:
            self.history = []
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to load history: {str(e)}")
            self.history = []
            
    def clear_history(self):
        reply = QMessageBox.question(self, "Clear History", 
                                    "Are you sure you want to clear all history?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.history = []
            self.update_history_table()
            self.save_history()
            self.status_label.setText("History cleared")
            
    def export_history(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export History", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.history, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, "Success", f"History exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")
                
    def import_history(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import History", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_history = json.load(f)
                self.history.extend(imported_history)
                self.update_history_table()
                self.save_history()
                QMessageBox.information(self, "Success", f"Imported {len(imported_history)} records")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import: {str(e)}")
                
def main():
    app = QApplication(sys.argv)
    converter = CurrencyConverter()
    converter.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()

