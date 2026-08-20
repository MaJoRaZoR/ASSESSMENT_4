"""
QA Automation Test Suite
Filename: InventoryQA.py
Validates stock conditions, error thresholds, multi-warehouse allocations, and concurrency.
"""

import unittest
import threading
from InventoryManagement import InventorySystem

class TestInventorySupplyChain(unittest.TestCase):
    def setUp(self):
        self.system = InventorySystem()
        # Setup initial supplier and items
        self.system.add_supplier("SUP01", "Global Logistics Corp", "supply@global.com")
        self.system.add_product_definition(
            product_id="PROD01",
            name="Wireless Mouse",
            reorder_threshold=10,
            reorder_quantity=50,
            supplier_id="SUP01"
        )

    def test_stock_availability(self):
        """Test initial stock addition and verified availability."""
        self.system.add_stock("Warehouse A", "PROD01", 30)
        self.assertEqual(self.system.get_total_stock("PROD01"), 30)

    def test_insufficient_inventory(self):
        """Test that removing more stock than available raises a ValueError."""
        self.system.add_stock("Warehouse A", "PROD01", 5)
        with self.assertRaises(ValueError):
            self.system.remove_stock("Warehouse A", "PROD01", 10)

    def test_warehouse_transfer(self):
        """Test moving inventory successfully between warehouses."""
        self.system.add_stock("Warehouse A", "PROD01", 20)
        self.system.transfer_stock("Warehouse A", "Warehouse B", "PROD01", 15)
        
        self.assertEqual(self.system.warehouses["Warehouse A"].inventory["PROD01"], 5)
        self.assertEqual(self.system.warehouses["Warehouse B"].inventory["PROD01"], 15)

    def test_concurrent_orders(self):
        """Test thread safety during concurrent order fulfillment executions."""
        self.system.add_stock("Warehouse A", "PROD01", 100)
        
        def place_order():
            try:
                self.system.fulfill_order("PROD01", 10)
            except Exception:
                pass

        threads = [threading.Thread(target=place_order) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(self.system.get_total_stock("PROD01"), 0)

    def test_reorder_threshold_and_detection(self):
        """Test low-stock detection triggering automatic replenishments."""
        self.system.add_stock("Warehouse A", "PROD01", 12)
        self.assertFalse(self.system.check_low_stock("PROD01"))
        
        # Bring stock down to threshold (10 units)
        self.system.remove_stock("Warehouse A", "PROD01", 2)
        self.assertTrue(self.system.check_low_stock("PROD01"))
        
        # Trigger explicit reorder action
        reorder_receipt = self.system.trigger_reorder("PROD01", "Warehouse A")
        self.assertIsNotNone(reorder_receipt)
        self.assertEqual(reorder_receipt["ordered_quantity"], 50)
        self.assertEqual(self.system.warehouses["Warehouse A"].inventory["PROD01"], 60)

    def test_invalid_product(self):
        """Test exceptions raised when manipulating unregistered items."""
        with self.assertRaises(ValueError):
            self.system.add_stock("Warehouse A", "FAKE_PROD", 10)
        with self.assertRaises(ValueError):
            self.system.fulfill_order("FAKE_PROD", 1)

    def test_negative_inventory(self):
        """Verify constraints against entering negative stock modifications."""
        with self.assertRaises(ValueError):
            self.system.add_stock("Warehouse A", "PROD01", -5)
        with self.assertRaises(ValueError):
            self.system.fulfill_order("PROD01", -10)

    def test_multiple_warehouses_and_selection(self):
        """Verify automatic routing picks the correct warehouse based on supply chains."""
        self.system.add_stock("Warehouse A", "PROD01", 5)   # Can't fulfill order of 15
        self.system.add_stock("Warehouse B", "PROD01", 20)  # Has enough
        self.system.add_stock("Warehouse C", "PROD01", 30)  # Also has enough
        
        # Order of 15 should skip Warehouse A and consume from Warehouse B
        allocated_wh = self.system.fulfill_order("PROD01", 15)
        self.assertEqual(allocated_wh, "Warehouse B")
        self.assertEqual(self.system.warehouses["Warehouse B"].inventory["PROD01"], 5)
        self.assertEqual(self.system.warehouses["Warehouse A"].inventory["PROD01"], 5)

if __name__ == "__main__":
    unittest.main()
