import datetime
import logging
import json
import requests  # For making API calls

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Transaction:
    def __init__(self, amount, currency, card_number, expiry_date, cvv, customer_id=None, transaction_id=None, status="Pending", processor_response=None):
        self.timestamp = datetime.datetime.now()
        self.amount = amount
        self.currency = currency
        self.card_number = self._mask_card_number(card_number) # Mask sensitive data
        self.expiry_date = expiry_date
        self.cvv = "***" # Never store or log full CVV
        self.customer_id = customer_id
        self.transaction_id = transaction_id if transaction_id else self._generate_transaction_id()
        self.status = status
        self.processor_response = processor_response

    def _mask_card_number(self, card_number):
        return "X" * (len(card_number) - 4) + card_number[-4:]

    def _generate_transaction_id(self):
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "transaction_id": self.transaction_id,
            "amount": self.amount,
            "currency": self.currency,
            "card_number": self.card_number,
            "expiry_date": self.expiry_date,
            "customer_id": self.customer_id,
            "status": self.status,
            "processor_response": self.processor_response
        }

    def copy(self):
        return Transaction(
            self.amount,
            self.currency,
            self.card_number.replace("X", ""), # Unmask for potential copying if needed internally
            self.expiry_date,
            "***", # Never copy the real CVV
            self.customer_id,
            self.transaction_id,
            self.status,
            self.processor_response
        )

class PaymentProcessor:
    def process_payment(self, transaction):
        raise NotImplementedError("Subclasses must implement this method")

class TSYSProcessor(PaymentProcessor):
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key

    def process_payment(self, transaction):
        logging.info(f"Attempting to process transaction {transaction.transaction_id} with TSYS")
        payload = {
            "amount": transaction.amount,
            "currency": transaction.currency,
            "card_number": transaction.card_number.replace("X", ""), # Unmask for processing (handle securely!)
            "expiry_date": transaction.expiry_date,
            "cvv": "***", # In a real system, this would be handled very carefully and not logged
            "transaction_id": transaction.transaction_id
            # Add other TSYS specific fields as needed
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        try:
            # In a real application, use proper error handling and security measures
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes
            transaction.status = "Approved"
            transaction.processor_response = response.json()
            logging.info(f"Transaction {transaction.transaction_id} processed successfully by TSYS. Response: {transaction.processor_response}")
        except requests.exceptions.RequestException as e:
            transaction.status = "Failed"
            transaction.processor_response = {"error": str(e)}
            logging.error(f"Error processing transaction {transaction.transaction_id} with TSYS: {e}")
        return transaction

class AnotherPlatformProcessor(PaymentProcessor):
    def __init__(self, api_endpoint, credentials):
        self.api_endpoint = api_endpoint
        self.credentials = credentials

    def process_payment(self, transaction):
        logging.info(f"Attempting to process transaction {transaction.transaction_id} with Another Platform")
        data = {
            "order_total": transaction.amount,
            "payment_method": "credit_card",
            "card": {
                "number": transaction.card_number.replace("X", ""), # Unmask carefully
                "expiry": transaction.expiry_date,
                "cvv": "***" # Handle securely
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

class EDCSystem:
    def __init__(self):
        self.transactions = []
        # In a real system, these configurations would be loaded securely
        self.tsys_processor = TSYSProcessor(
            api_url="https://api.sandbox.tsys.com/v1/payments",  # Example sandbox URL
            api_key="YOUR_TSYS_API_KEY"
        )
        self.another_processor = AnotherPlatformProcessor(
            api_endpoint="https://api.anotherplatform.com/payments", # Example URL
            credentials={"username": "your_username", "password": "your_password"}
        )

    def capture_transaction_data(self):
        amount = float(input("Enter transaction amount: "))
        currency = input("Enter currency (e.g., USD): ").upper()
        card_number = input("Enter card number: ")
        expiry_date = input("Enter expiry date (MM/YY): ")
        cvv = input("Enter CVV: ")
        customer_id = input("Enter optional customer ID: ")
        return Transaction(amount, currency, card_number, expiry_date, cvv, customer_id)

    def process_transaction(self, transaction, platform="tsys"):
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

    def view_transactions(self):
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

    # Capture another transaction
    another_transaction = edc.capture_transaction_data()

    # Process the transaction with the other platform
    processed_other_transaction = edc.process_transaction(another_transaction.copy(), platform="another")
    print("\nAnother Platform Processing Result:")
    print(json.dumps(processed_other_transaction.to_dict(), indent=4))

    # View all captured transactions
    print("\nAll Transactions:")
    edc.view_transactions()