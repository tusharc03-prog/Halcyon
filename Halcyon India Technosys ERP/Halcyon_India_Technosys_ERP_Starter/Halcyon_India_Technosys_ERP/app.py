import json
import sys
from pathlib import Path
from PySide6.QtCore import QObject, Slot, QUrl
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from database import Database

APP_NAME = "Halcyon India Technosys ERP"

def data_directory():
    base = Path.home() / "AppData" / "Local" / "HalcyonIndiaTechnosys"
    base.mkdir(parents=True, exist_ok=True)
    return base

def ui_directory():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "ui"
    return Path(__file__).resolve().parent / "ui"

class ERPBridge(QObject):
    def __init__(self, database):
        super().__init__()
        self.db = database

    def result(self, fn):
        try:
            return json.dumps({"success": True, "data": fn()})
        except Exception as exc:
            return json.dumps({"success": False, "error": str(exc)})

    @Slot(result=str)
    def get_company(self):
        return self.result(self.db.get_company)

    @Slot(str, str, str, str, result=str)
    def save_company(self, name, address, gstin, msme):
        return self.result(lambda: self.db.save_company(name, address, gstin, msme))

    @Slot(result=str)
    def get_products(self):
        return self.result(self.db.list_products)

    @Slot(str, str, str, str, str, str, result=str)
    def add_product(self, sku, name, category, unit, price, reorder):
        return self.result(lambda: self.db.add_product(
            sku, name, category, unit, float(price or 0), float(reorder or 0)
        ))

    @Slot(str, str, str, str, result=str)
    def stock_movement(self, product_id, movement_type, quantity, note):
        return self.result(lambda: self.db.record_movement(
            int(product_id), movement_type, float(quantity), note
        ))

    @Slot(result=str)
    def get_stock_report(self):
        return self.result(self.db.stock_report)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1440, 900)
        self.setMinimumSize(1050, 700)

        db_path = data_directory() / "halcyon_inventory.db"
        self.database = Database(db_path)

        self.view = QWebEngineView(self)
        self.channel = QWebChannel(self.view.page())
        self.bridge = ERPBridge(self.database)
        self.channel.registerObject("erp", self.bridge)
        self.view.page().setWebChannel(self.channel)
        self.setCentralWidget(self.view)

        index_file = ui_directory() / "index.html"
        if not index_file.exists():
            QMessageBox.critical(self, "Missing UI", f"Cannot find {index_file}")
            return
        self.view.load(QUrl.fromLocalFile(str(index_file.resolve())))

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
