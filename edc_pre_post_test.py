import datetime
import logging
import json
import requests
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)Message')

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
    """Payment processor for TSYS (simulated for testing)."""

    def __init__(self, api_url, api_key):
        """Initializes the TSYS payment processor."""
        self.api_url = api_url
        self.api_key = api_key

    def _simulate_tsys_response(self, transaction_id, operation="process"):
        """Simulates TSYS API responses for testing."""
        if random.random() < 0.9:  # Simulate 90% success rate
            if operation == "process":
                return {"status": "Approved", "transaction_id": transaction_id, "auth_code": "123456"}
            elif operation == "reauthorize":
                return {"status": "Re-authorized", "transaction_id": transaction_id, "new_auth_code": "789012"}
            elif operation == "capture":
                return {"status": "Captured", "transaction_id": transaction_id, "capture_id": "ABCDEFG"}
        else:
            error_messages = ["Insufficient funds", "Invalid card number", "Transaction declined"]
            error_message = random.choice(error_messages)
            return {"status": "Failed", "transaction_id": transaction_id, "error": error_message}

    def process_payment(self, transaction):
        """Simulates processing a payment transaction with TSYS."""
        logging.info(f"Simulating processing transaction {transaction.transaction_id} with TSYS")
        response = self._simulate_tsys_response(transaction.transaction_id, "process")
        transaction.processor_response = response
        transaction.status = response["status"]
        if transaction.status == "Approved":
            logging.info(f"Transaction {transaction.transaction_id} simulated successfully by TSYS. Response: {response}")
        else:
            logging.error(f"Error simulating transaction {transaction.transaction_id} with TSYS: {response}")
        return transaction

    def reauthorize_payment(self, transaction, new_amount):
        """Simulates re-authorizing a payment with a new amount with TSYS."""
        logging.info(f"Simulating re-authorizing transaction {transaction.transaction_id} with TSYS for new amount: {new_amount}")
        response = self._simulate_tsys_response(transaction.transaction_id, "reauthorize")
        transaction.processor_response = response
        transaction.status = response["status"]
        if transaction.status == "Re-authorized":
            logging.info(f"Transaction {transaction.transaction_id} re-authorized successfully by TSYS. Response: {response}")
        else:
            logging.error(f"Error re-authorizing transaction {transaction.transaction_id} with TSYS: {response}")
        return transaction

    def post_authorization(self, transaction):
        """Simulates completing a pre-authorized payment with TSYS."""
        logging.info(f"Simulating capturing transaction {transaction.transaction_id} with TSYS")
        response = self._simulate_tsys_response(transaction.transaction_id, "capture")
        transaction.processor_response = response
        transaction.status = response["status"]
        if transaction.status == "Captured":
            logging.info(f"Transaction {transaction.transaction_id} captured successfully by TSYS. Response: {response}")
        else:
            logging.error(f"Error capturing transaction {transaction.transaction_id} with TSYS: {response}")
        return transaction

class AnotherPlatformProcessor(PaymentProcessor):
    """Payment processor for Another Platform."""

    def __init__(self, api_endpoint, credentials):
        """Initializes the Another Platform payment processor."""
        self.api_endpoint = api_endpoint
        self.credentials = credentials

    def process_payment(self, transaction):
        """Processes a payment transaction with Another Platform."""
        logging.info(f"Attempting to process transaction {transaction.transaction_id} with Another Platform")
        data = {
            "order_total": transaction.amount,
            "payment_method": "credit_card",
            "card": {
                "number": transaction.card_number.replace("X", ""),  # Unmask carefully
                "expiry": transaction.expiry_date,
                "cvv": "***"  # Handle securely
            },
            "reference_id": transaction.transaction_id
            # Add other platform specific fields
        }
        try:
            # Implement authentication based on the platform's requirements
            auth = requests.auth.HTTPBasicAuth(self.credentials['username'], self.credentials['password'])
            response = requests.post(self.api_endpoint, json=data, auth=auth)
            response.raise_for_status()
            transaction.status = "Processed by Other"
            transaction.processor_response = response.json()
            logging.info(f"Transaction {transaction.transaction_id} processed successfully by Another Platform. Response: {transaction.processor_response}")
        except requests.exceptions.RequestException as e:
            transaction.status = "Failed"
            transaction.processor_response = {"error": str(e)}
            logging.error(f"Error processing transaction {transaction.transaction_id} with Another Platform: {e}")
        return transaction
    def reauthorize_payment(self, transaction, new_amount):
        """Re-authorizes a payment with a new amount with Another Platform."""
        logging.info(f"Attempting to re-authorize transaction {transaction.transaction_id} with Another Platform for new amount: {new_amount}")
        data = {
            "original_reference_id": transaction.transaction_id,
            "order_total": new_amount,
            # Add other platform specific fields
        }
        try:
            auth = requests.auth.HTTPBasicAuth(self.credentials['username'], self.credentials['password'])
            response = requests.post(f"{self.api_endpoint}/reauthorize", json=data, auth=auth)
            response.raise_for_status()
            transaction.status = "Re-authorized by Other"
            transaction.processor_response = response.json()
            logging.info(f"Transaction {transaction.transaction_id} re-authorized successfully by Another Platform. Response: {transaction.processor_response}")
        except requests.exceptions.RequestException as e:
            transaction.status = "Re-authorization Failed"
            transaction.processor_response = {"error": str(e)}
            logging.error(f"Error re-authorizing transaction {transaction.transaction_id} with Another Platform: {e}")
        return transaction

    def post_authorization(self, transaction):
        """Completes a pre-authorized payment with Another Platform."""
        logging.info(f"Attempting to post-authorize transaction {transaction.transaction_id} with Another Platform")
        data = {
            "original_reference_id": transaction.transaction_id,
            # Add other platform specific fields
        }
        try:
            auth = requests.auth.HTTPBasicAuth(self.credentials['username'], self.credentials['password'])
            response = requests.post(f"{self.api_endpoint}/capture", json=data, auth=auth)
            response.raise_for_status()
            transaction.status = "Captured by Other"
            transaction.processor_response = response.json()
            logging.info(f"Transaction {transaction.transaction_id} captured successfully by Another Platform. Response: {transaction.processor_response}")
        except requests.exceptions.RequestException as e:
            transaction.status = "Capture Failed"
            transaction.processor_response = {"error": str(e)}
            logging.error(f"Error capturing transaction {transaction.transaction_id} with Another Platform: {e}")
        return transaction
class EDCSystem:
    """Electronic Data Capture (EDC) system."""

    def __init__(self):
        """Initializes the EDC system."""
        self.transactions = []
        # In a real system, these configurations would be loaded securely
        self.tsys_processor = TSYSProcessor(
            api_url="https://api.sandbox.tsys.com/v1/payments",  # Example sandbox URL
            api_key="YOUR_TSYS_API_KEY"
        )
        self.another_processor = AnotherPlatformProcessor(
            api_endpoint="https://api.anotherplatform.com/payments",  # Example URL
            credentials={"username": "your_username", "password": "your_password"}
        )

    def capture_transaction_data(self):
        """Captures transaction data from user input."""
        amount = float(input("Enter transaction amount: "))
        currency = input("Enter currency (e.g., USD): ").upper()
        card_number = input("Enter card number: ")
        expiry_date = input("Enter expiry date (MM/YY): ")
        cvv = input("Enter CVV: ")
        customer_id = input("Enter optional customer ID: ")
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

# Example Usage:
if __name__ == "__main__":
    edc = EDCSystem()

    # Capture transaction data
    new_transaction = edc.capture_transaction_data()

    # Process the transaction with TSYS
    processed_tsys_transaction = edc.process_transaction(new_transaction.copy(), platform="tsys")
    print("\nTSYS Processing Result:")
    print(json.dumps(processed_tsys_transaction.to_dict(), indent=4))

    # Re-authorize the transaction
    reauthorized_transaction = edc.reauthorize_transaction(processed_tsys_transaction.copy(), processed_tsys_transaction.amount * 1.1, platform="tsys")
    print("\nTSYS Re-authorization Result:")
    print(json.dumps(reauthorized_transaction.to_dict(), indent=4))

    # Post-authorize the transaction
    captured_tsys_transaction = edc.post_authorize_transaction(reauthorized_transaction.copy(), platform="tsys")
    print("\nTSYS Capture Result:")
    print(json.dumps(captured_tsys_transaction.to_dict(), indent=4))

    # Capture another transaction
    another_transaction = edc.capture_transaction_data()

    # Process the transaction with the other platform
    processed_other_transaction = edc.process_transaction(another_transaction.copy(), platform="another")
    print("\nAnother Platform Processing Result:")
    print(json.dumps(processed_other_transaction.to_dict(), indent=4))

    # View all captured transactions
    print("\nAll Transactions:")
    edc.view_transactions()