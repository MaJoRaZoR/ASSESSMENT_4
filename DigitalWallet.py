import time
from datetime import datetime, timedelta

class DigitalWallet:
    def __init__(self, account_id, owner_name, pin, daily_limit=50000.0, large_tx_threshold=20000.0):
        self.account_id = account_id
        self.owner_name = owner_name
        self.__pin = pin
        self.daily_limit = float(daily_limit)
        self.large_tx_threshold = float(large_tx_threshold)
        
        self.balance = 0.0
        self.is_locked = False
        self.failed_pin_attempts = 0
        self.transactions = []  # List of dicts: {timestamp, type, amount, status, details, flag}

    def verify_pin(self, pin):
        if self.is_locked:
            return False
        if self.__pin == pin:
            self.failed_pin_attempts = 0
            return True
        else:
            self.failed_pin_attempts += 1
            if self.failed_pin_attempts >= 3:
                self.is_locked = True
            return False

    def _get_daily_total(self):
        today = datetime.now().date()
        total = 0.0
        for tx in self.transactions:
            if tx['status'] == 'Success' and tx['type'] in ['Withdrawal', 'Transfer Out']:
                tx_date = datetime.fromtimestamp(tx['timestamp']).date()
                if tx_date == today:
                    total += tx['amount']
        return total

    def _detect_fraud(self, amount, tx_type):
        flags = []
        now = time.time()
        
        # 1. High Velocity Check: More than 5 transactions in last 10 minutes
        ten_mins_ago = now - 600
        recent_txs = [tx for tx in self.transactions if tx['timestamp'] >= ten_mins_ago]
        if len(recent_txs) >= 5:
            flags.append("High Velocity (Count > 5 in 10 mins)")

        # 2. Large Transaction Check
        if amount >= self.large_tx_threshold:
            flags.append(f"Large Transaction (>= {self.large_tx_threshold})")

        # 3. Multiple Failed PIN Attempts Checked outside during authentication
        if self.failed_pin_attempts > 0:
            flags.append(f"Failed PIN Attempts Active ({self.failed_pin_attempts})")

        # 4. Unusual Transaction Amount (e.g., fractional anomalies or negative bounds handled by limits)
        if amount > 0 and amount % 10000 == 999:  # Custom example rule for unusual pattern
            flags.append("Unusual Transaction Pattern Amount")

        return flags

    def deposit(self, amount, pin):
        now = time.time()
        if self.is_locked:
            return False, "Account Locked"
        if not self.verify_pin(pin):
            return False, "Invalid PIN"
        if amount <= 0:
            return False, "Negative or Zero Amount Not Allowed"

        flags = self._detect_fraud(amount, 'Deposit')
        flag_str = ", ".join(flags) if flags else "None"

        self.balance += amount
        self.transactions.append({
            'timestamp': now, 'type': 'Deposit', 'amount': amount,
            'status': 'Success', 'details': 'Cash Deposit', 'flag': flag_str
        })
        return True, f"Deposit Successful. Flag status: {flag_str}"

    def withdraw(self, amount, pin):
        now = time.time()
        if self.is_locked:
            return False, "Account Locked"
        if not self.verify_pin(pin):
            return False, "Invalid PIN"
        if amount <= 0:
            return False, "Negative or Zero Amount Not Allowed"
        if amount > self.balance:
            return False, "Insufficient Balance"

        if self._get_daily_total() + amount > self.daily_limit:
            return False, "Daily Transaction Limit Exceeded"

        flags = self._detect_fraud(amount, 'Withdrawal')
        flag_str = ", ".join(flags) if flags else "None"

        self.balance -= amount
        self.transactions.append({
            'timestamp': now, 'type': 'Withdrawal', 'amount': amount,
            'status': 'Success', 'details': 'ATM Withdrawal', 'flag': flag_str
        })
        return True, f"Withdrawal Successful. Flag status: {flag_str}"

    def transfer(self, target_wallet, amount, pin):
        now = time.time()
        if self.is_locked:
            return False, "Sender Account Locked"
        if target_wallet.is_locked:
            return False, "Target Account Locked"
        if not self.verify_pin(pin):
            return False, "Invalid PIN"
        if amount <= 0:
            return False, "Negative or Zero Amount Not Allowed"
        if amount > self.balance:
            return False, "Insufficient Balance"

        # Check duplicate transaction mitigation (Idempotency lookback within 5 seconds)
        if self.transactions:
            last_tx = self.transactions[-1]
            if (now - last_tx['timestamp'] < 5 and 
                last_tx['type'] == 'Transfer Out' and 
                last_tx['amount'] == amount and 
                last_tx['status'] == 'Success'):
                return False, "Duplicate Transaction Detected"

        if self._get_daily_total() + amount > self.daily_limit:
            return False, "Daily Transaction Limit Exceeded"

        flags = self._detect_fraud(amount, 'Transfer Out')
        flag_str = ", ".join(flags) if flags else "None"

        self.balance -= amount
        target_wallet.balance += amount

        self.transactions.append({
            'timestamp': now, 'type': 'Transfer Out', 'amount': amount,
            'status': 'Success', 'details': f'Transferred to {target_wallet.account_id}', 'flag': flag_str
        })
        target_wallet.transactions.append({
            'timestamp': now, 'type': 'Transfer In', 'amount': amount,
            'status': 'Success', 'details': f'Received from {self.account_id}', 'flag': 'None'
        })
        return True, f"Transfer Successful. Flag status: {flag_str}"

    def get_balance(self, pin):
        if self.is_locked:
            return None, "Account Locked"
        if not self.verify_pin(pin):
            return None, "Invalid PIN"
        return self.balance, "Success"

    def get_history(self):
        return self.transactions
