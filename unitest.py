import datetime
import logging
import json
import requests  # Import for type hinting, but we will mock it
import unittest
from unittest.mock import patch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Transaction:
    """Represents a financial transaction."""

    def __init__(self, amount, currency, card_number, expiry_date, cvv, customer_id=None, transaction_id=None, status="Pending", processor_response=None, original_transaction_id=None):
        """
        Initializes a Transaction object.

        Args:
            amount (float): The transaction amount.
            currency (str): The transaction currency.
            card_number (str): The card number.
            expiry_date (str): The card expiry date (MM/YY).
            cvv (str): The card CVV.
            customer_id (str, optional): The customer ID.
            transaction_id (str, optional): The transaction ID. If None, it's generated.
            status (str, optional): The transaction status. Defaults to "Pending".
            processor_response (dict, optional): The processor's response.
            original_transaction_id (str, optional): The ID of the original transaction for re-authorizations.
        """
        self.timestamp = datetime.datetime.now()
        self.amount = amount
        self.currency = currency
        self.card_number = self._mask_card_number(card_number)  # Mask sensitive data
        self.expiry_date = expiry_date
        self.cvv = "***"  # Never store or log full CVV
        self.customer_id = customer_id
        self.transaction_id = transaction_id if transaction_id else self._generate_transaction_id()
        self.status = status
        self.processor_response = processor_response
        self.original_transaction_id = original_transaction_id

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
        }

    def copy(self):
        """Creates a copy of the transaction object."""
        return Transaction(
            self.amount,
            self.currency,
            self.card_number.replace("X", ""),  # Unmask for potential copying if needed internally
            self.expiry_date,
            "***",  # Never copy the real CVV
            self.customer_id,
            self.transaction_id,
            self.status,
            self.processor_response,
            self.original_transaction_id
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

class TSYSProcessor(PaymentProcessor):
    """Payment processor for TSYS (mocked for local testing)."""

    def __init__(self, api_url, api_key):
        """Initializes the TSYS payment processor."""
        self.api_url = api_url
        self.api_key = api_key

    def process_payment(self, transaction):
        """Processes a payment transaction with TSYS (mocked)."""
        logging.info(f"Simulating TSYS payment for transaction {transaction.transaction_id}")
        transaction.status = "Approved"
        transaction.processor_response = {"status": "success", "message": "Simulated approval"}
        logging.info(f"Simulated TSYS payment successful. Response: {transaction.processor_response}")
        return transaction

    def reauthorize_payment(self, transaction, new_amount):
        """Re-authorizes a payment with TSYS (mocked)."""
        logging.info(f"Simulating TSYS re-authorization for transaction {transaction.transaction_id}")
        transaction.status = "Re-authorized"
        transaction.processor_response = {"status": "success", "message": "Simulated re-authorization"}
        logging.info(f"Simulated TSYS re-authorization successful. Response: {transaction.processor_response}")
        return transaction

    def post_authorization(self, transaction):
        """Completes a pre-authorized payment with TSYS (mocked)."""
        logging.info(f"Simulating TSYS capture for transaction {transaction.transaction_id}")
        transaction.status = "Captured"
        transaction.processor_response = {"status": "success", "message": "Simulated capture"}
        logging.info(f"Simulated TSYS capture successful. Response: {transaction.processor_response}")
        return transaction

class AnotherPlatformProcessor(PaymentProcessor):
    """Payment processor for Another Platform (mocked for local testing)."""

    def __init__(self, api_endpoint, credentials):
        """Initializes the Another Platform payment processor."""
        self.api_endpoint = api_endpoint
        self.credentials = credentials

    def process_payment(self, transaction):
        """Processes a payment transaction with Another Platform (mocked)."""
        logging.info(f"Simulating Another Platform payment for transaction {transaction.transaction_id}")
        transaction.status = "Processed by Other"
        transaction.processor_response = {"status": "success", "message": "Simulated Other approval"}
        logging.info(f"Simulated Another Platform payment successful. Response: {transaction.processor_response}")
        return transaction

    def reauthorize_payment(self, transaction, new_amount):
        """Re-authorizes a payment with Another Platform (mocked)."""
        logging.info(f"Simulating Another Platform re-authorization for transaction {transaction.transaction_id}")
        transaction.status = "Re-authorized by Other"
        transaction.processor_response = {"status": "success", "message": "Simulated Other re-authorization"}
        logging.info(f"Simulated Another Platform re-authorization successful. Response: {transaction.processor_response}")
        return transaction

    def post_authorization(self, transaction):
        """Completes a pre-authorized payment with Another Platform (mocked)."""
        logging.info(f"Simulating Another Platform capture for transaction {transaction.transaction_id}")
        transaction.status = "Captured by Other"
        transaction.processor_response = {"status": "success", "message": "Simulated Other capture"}
        logging.info(f"Simulated Another Platform capture successful. Response: {transaction.processor_response}")
        return transaction

class EDCSystem:
    """Electronic Data Capture (EDC) system."""

    def __init__(self):
        """Initializes the EDC system."""
        self.transactions = []
        self.tsys_processor = TSYSProcessor(
            api_url="https://api.sandbox.tsys.com/v1/payments",
            api_key="YOUR_TSYS_API_KEY"
        )
        self.another_processor = AnotherPlatformProcessor(
            api_endpoint="https://api.anotherplatform.com/payments",
            credentials={"username": "your_username", "password": "your_password"}
        )

    def capture_transaction_data(self):
        """Captures transaction data from user input."""
        amount = 100.0  # Hardcoded for testing
        currency = "USD"
        card_number = "1234567890123456"
        expiry_date = "12/24"
        cvv = "123"
        customer_id = "cust123"
        return Transaction(amount, currency, card_number, expiry_date, cvv, customer_id)

    def process_transaction(self, transaction, platform="tsys"):
        """Processes a transaction using the specified payment processor."""
        self.transactions.append(transaction)
        if platform.lower() == "tsys":
            processed_transaction = self.tsys_processor.process_payment(transaction)
        elif platform.lower() == "another":
            processed_transaction = self.another_processor.process_payment(transaction)
        else:
            logging.error(f"Invalid platform specified: {platform}")
            processed_transaction = transaction
            processed_transaction.status = "Error: Invalid Platform"
        return processed_transaction

    def reauthorize_transaction(self, transaction, new_amount, platform="tsys"):
        """Re-authorizes a transaction with a new amount."""
        if platform.lower() == "tsys":
            reauthorized_transaction = self.tsys_processor.reauthorize_payment(transaction, new_amount)
        elif platform.lower() == "another":
            reauthorized_transaction = self.another_processor.reauthorize_payment(transaction, new_amount)
        else:
            logging.error(f"Invalid platform specified: {platform}")
            reauthorized_transaction = transaction
            reauthorized_transaction.status = "Error: Invalid Platform"
        return reauthorized_transaction

    def post_authorize_transaction(self, transaction, platform="tsys"):
        """Completes a pre-authorized transaction."""
        if platform.lower() == "tsys":
            captured_transaction = self.tsys_processor.post_authorization(transaction)
        elif platform.lower() == "another":
            captured_transaction = self.another_processor.post_authorization(transaction)
        else:
            logging.error(f"Invalid platform specified: {platform}")
            captured_transaction = transaction
            captured_transaction.status = "Error: Invalid Platform"
        return captured_transaction

    def view_transactions(self):
        """Displays all captured transactions."""
        for trans in self.transactions:
            print(json.dumps(trans.to_dict(), indent=4))

class TestEDCSystem(unittest.TestCase):
    def setUp(self):
        self.edc = EDCSystem()

    def test_preauth_and_postauth(self):
        transaction = self.edc.capture_transaction_data()
        processed_transaction = self.edc.process_transaction(transaction.copy(), platform="tsys")
        self.assertEqual(processed_transaction.status, "Approved")
        reauthorized_transaction = self.edc.reauthorize_transaction(processed_transaction.copy(), processed_transaction.amount * 1.1, platform="tsys")
        self.assertEqual(reauthorized_transaction.status, "Re-authorized")
        captured_transaction = self.edc.post_authorize_transaction(reauthorized_transaction.copy(), platform="tsys")
        self.assertEqual(captured_transaction.status, "Captured")

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)