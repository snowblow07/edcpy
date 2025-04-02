import datetime
import logging
import json
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Transaction:
    """Represents a financial transaction."""

    def __init__(self, amount, currency, card_number, expiry_date, cvv, customer_id=None, transaction_id=None, status="Pending", processor_response=None, original_transaction_id=None, var_sheet=None):
        """
        Initializes a Transaction object.
        """
        self.timestamp = datetime.datetime.now()
        self.amount = amount
        self.currency = currency
        self.card_number = self._mask_card_number(card_number)
        self.expiry_date = expiry_date
        self.cvv = "***"
        self.customer_id = customer_id
        self.transaction_id = transaction_id if transaction_id else self._generate_transaction_id()
        self.status = status
        self.processor_response = processor_response
        self.original_transaction_id = original_transaction_id
        self.var_sheet = var_sheet or {}

    def _mask_card_number(self, card_number):
        """Masks the card number for security."""
        return "X" * (len(card_number) - 4) + card_number[-4:]

    def _generate_transaction_id(self):
        """Generates a unique transaction ID based on the current timestamp."""
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    def to_dict(self):
        """Converts the transaction object to a dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "transaction_id": self.transaction_id,
            "amount": self.amount,
            "currency": self.currency,
            "card_number": self.card_number,
            "expiry_date": self.expiry_date,
            "customer_id": self.customer_id,
            "status": self.status,
            "processor_response": self.processor_response,
            "original_transaction_id": self.original_transaction_id,
            "var_sheet": self.var_sheet,
        }

    def copy(self):
        """Creates a copy of the transaction object."""
        return Transaction(
            self.amount,
            self.currency,
            self.card_number.replace("X", ""),
            self.expiry_date,
            "***",
            self.customer_id,
            self.transaction_id,
            self.status,
            self.processor_response,
            self.original_transaction_id,
            self.var_sheet.copy() if self.var_sheet else None,
        )

class PaymentProcessor:
    """Base class for payment processors."""

    def process_payment(self, transaction):
        """Processes a payment transaction. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement this method")

    def reauthorize_payment(self, transaction, new_amount):
        """Re-authorizes a payment with a new amount."""
        raise NotImplementedError("Subclasses must implement this method")

    def post_authorization(self, transaction):
        """Completes a pre-authorized payment."""
        raise NotImplementedError("Subclasses must implement this method")

class LocalEmulationProcessor(PaymentProcessor):
    """Local emulation of a payment processor."""

    def process_payment(self, transaction):
        """Processes a payment transaction locally."""
        logging.info(f"Emulating processing transaction {transaction.transaction_id}")
        if random.random() < 0.9:  # Simulate success 90% of the time
            transaction.status = "Approved"
            transaction.processor_response = {"result": "Success", "transaction_reference": f"local-{transaction.transaction_id}"}
            logging.info(f"Transaction {transaction.transaction_id} emulated success.")
        else:
            transaction.status = "Failed"
            transaction.processor_response = {"result": "Failure", "error": "Simulated processing error"}
            logging.error(f"Transaction {transaction.transaction_id} emulated failure.")
        return transaction

    def reauthorize_payment(self, transaction, new_amount):
        """Re-authorizes a payment locally."""
        logging.info(f"Emulating re-authorizing transaction {transaction.transaction_id} for {new_amount}")
        if random.random() < 0.9:
            transaction.status = "Re-authorized"
            transaction.processor_response = {"result": "Success", "new_amount": new_amount}
            logging.info(f"Transaction {transaction.transaction_id} emulated re-authorization success.")
        else:
            transaction.status = "Re-authorization Failed"
            transaction.processor_response = {"result": "Failure", "error": "Simulated re-authorization error"}
            logging.error(f"Transaction {transaction.transaction_id} emulated re-authorization failure.")
        return transaction

    def post_authorization(self, transaction):
        """Completes a pre-authorized payment locally."""
        logging.info(f"Emulating post-authorizing transaction {transaction.transaction_id}")
        if random.random() < 0.9:
            transaction.status = "Captured"
            transaction.processor_response = {"result": "Success", "capture_reference": f"capture-{transaction.transaction_id}"}
            logging.info(f"Transaction {transaction.transaction_id} emulated capture success.")
        else:
            transaction.status = "Capture Failed"
            transaction.processor_response = {"result": "Failure", "error": "Simulated capture error"}
            logging.error(f"Transaction {transaction.transaction_id} emulated capture failure.")
        return transaction

class EDCSystem:
    """Electronic Data Capture (EDC) system."""

    def __init__(self):
        """Initializes the EDC system."""
        self.transactions = []
        self.local_processor = LocalEmulationProcessor()

    def capture_transaction_data(self):
        """Captures transaction data from user input."""
        amount = float(input("Enter transaction amount: "))
        currency = input("Enter currency (e.g., USD): ").upper()
        card_number = input("Enter card number: ")
        expiry_date = input("Enter expiry date (MM/YY): ")
        cvv = input("Enter CVV: ")
        customer_id = input("Enter optional customer ID: ")

        var_sheet = {
            "merchant_number": input("Enter Merchant Number (MID): "),
            "acquirer_bin": input("Enter Acquirer BIN: "),
            "store_number": input("Enter Store Number: "),
            "terminal_number": input("Enter Terminal Number: "),
            "mcc": input("Enter Merchant Category Code (MCC): "),
            "location_number": input("Enter Location Number: "),
            "vital_number": input("Enter Vital Number: "),
            "agent_bank": input("Enter Agent Bank: ")
        }
        return Transaction(amount, currency, card_number, expiry_date, cvv, customer_id, var_sheet=var_sheet)

    def process_transaction(self, transaction):
        """Processes a transaction using the local payment processor."""
        self.transactions.append(transaction)
        processed_transaction = self.local_processor.process_payment(transaction)
        return processed_transaction

    def reauthorize_transaction(self, transaction, new_amount):
        """Re-authorizes a transaction with a new amount."""
        reauthorized_transaction = self.local_processor.reauthorize_payment(transaction, new_amount)
        return reauthorized_transaction

    def post_authorize_transaction(self, transaction):
        """Completes a pre-authorized transaction."""
        captured_transaction = self.local_processor.post_authorization(transaction)
        return captured_transaction

    def view_transactions(self):
        """Displays all captured transactions."""
        for trans in self.transactions:
            print(json.dumps(trans.to_dict(), indent=4))

# Example Usage:
if __name__ == "__main__":
    edc = EDCSystem()

    new_transaction = edc.capture_transaction_data()

    processed_transaction = edc.process_transaction(new_transaction.copy())
    print("\nProcessing Result:")
    print(json.dumps(processed_transaction.to_dict(), indent=4))

    reauthorized_transaction = edc.reauthorize_transaction(processed_transaction.copy(), processed_transaction.amount * 1.1)
    print("\nRe-authorization Result:")
    print(json.dumps(reauthorized_transaction.to_dict(), indent=4))

    captured_transaction = edc.post_authorize_transaction(reauthorized_transaction.copy())
    print("\nCapture Result:")
    print(json.dumps(captured_transaction.to_dict(), indent=4))

    print("\nAll Transactions:")
    edc.view_transactions()