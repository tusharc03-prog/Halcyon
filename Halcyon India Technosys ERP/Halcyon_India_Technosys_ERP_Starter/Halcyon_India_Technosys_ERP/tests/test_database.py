import tempfile
import unittest
from pathlib import Path
from database import Database

class InventoryDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temp.name) / "test.db")

    def tearDown(self):
        self.temp.cleanup()

    def test_company_defaults(self):
        self.assertEqual(self.db.get_company()["name"], "HALCYON INDIA TECHNOSYS")

    def test_product_and_stock_balance(self):
        p = self.db.add_product("CAM-001", "IP Camera", "CCTV", "Nos", 2500, 2)
        self.db.record_movement(p["id"], "IN", 10, "Opening stock")
        self.db.record_movement(p["id"], "OUT", 3, "Project issue")
        self.assertEqual(self.db.get_product(p["id"])["balance"], 7)

    def test_prevent_negative_stock(self):
        p = self.db.add_product("SW-001", "POE Switch", "Networking", "Nos", 4000, 1)
        with self.assertRaises(ValueError):
            self.db.record_movement(p["id"], "OUT", 1, "Should fail")

if __name__ == "__main__":
    unittest.main()
