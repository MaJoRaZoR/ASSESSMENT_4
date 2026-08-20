import unittest
import time
import threading
from DigitalWallet import DigitalWallet

class TestWalletSecurity(unittest.TestCase):
    def setUp(self):
        self.wallet_a = DigitalWallet(account_id="W001", owner_name="Alice", pin="1234", daily_limit=1000.0, large_tx_threshold=500.0)
        self.wallet_b = DigitalWallet(account_id="W002", owner_name="Bob", pin="5678")
        # Pre-seed balance for operations
        self.wallet_a.balance = 800.0

    def test_normal_transaction(self):
        success, msg = self.wallet_a.withdraw(100.0, "1234")
        self.assertTrue(success)
        self.assertEqual(self.wallet_a.balance, 700.0)

    def test_insufficient_balance(self):
        success, msg = self.wallet_a.withdraw(900.0, "1234")
        self.assertFalse(success)
        self.assertEqual(msg, "Insufficient Balance")

    def test_daily_limit(self):
        # Exceed daily limit of 1000
        self.wallet_a.balance = 2000.0
        success, msg = self.wallet_a.withdraw(1100.0, "1234")
        self.assertFalse(success)
        self.assertEqual(msg, "Daily Transaction Limit Exceeded")

    def test_multiple_failed_pins(self):
        self.wallet_a.verify_pin("9999")
        self.wallet_a.verify_pin("8888")
        success, msg = self.wallet_a.withdraw(10.0, "7777") # 3rd structural failure
        self.assertFalse(success)
        self.assertTrue(self.wallet_a.is_locked)

    def test_suspicious_transaction(self):
        # Test large transaction threshold warning tag
        success, msg = self.wallet_a.withdraw(600.0, "1234")
        self.assertTrue(success)
        tx_history = self.wallet_a.get_history()
        self.assertIn("Large Transaction", tx_history[-1]['flag'])

        # Test rapid execution block (Velocity Check)
        for _ in range(5):
            self.wallet_a.deposit(10.0, "1234")
        success, msg = self.wallet_a.deposit(10.0, "1234")
        tx_history = self.wallet_a.get_history()
        self.assertIn("High Velocity", tx_history[-1]['flag'])

    def test_duplicate_transaction(self):
        # Rapid successive execution identical tracking block
        success1, msg1 = self.wallet_a.transfer(self.wallet_b, 50.0, "1234")
        success2, msg2 = self.wallet_a.transfer(self.wallet_b, 50.0, "1234")
        self.assertTrue(success1)
        self.assertFalse(success2)
        self.assertEqual(msg2, "Duplicate Transaction Detected")

    def test_negative_amount(self):
        success, msg = self.wallet_a.deposit(-50.0, "1234")
        self.assertFalse(success)
        self.assertEqual(msg, "Negative or Zero Amount Not Allowed")

    def test_concurrent_transactions(self):
        # Stress test race condition checks via python thread executors
        self.wallet_a.balance = 100.0
        errors = []

        def race_withdraw():
            success, msg = self.wallet_a.withdraw(60.0, "1234")
            if not success:
                errors.append(msg)

        t1 = threading.Thread(target=race_withdraw)
        t2 = threading.Thread(target=race_withdraw)
        
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Balance cannot fall negative under any condition state race
        self.assertGreaterEqual(self.wallet_a.balance, 0.0)

if __name__ == '__main__':
    unittest.main()
