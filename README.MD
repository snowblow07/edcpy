# Electronic Data Capture (EDC) System

This project implements a basic Electronic Data Capture (EDC) system for processing financial transactions. It supports multiple payment processors, including TSYS and a generic "Another Platform" for demonstration purposes.

## Features

-   **Transaction Management:**
    -      Captures transaction details such as amount, currency, card number, expiry date, and CVV.
    -      Generates unique transaction IDs.
    -      Masks sensitive card data for security.
    -      Stores transaction status and processor responses.
    -      Supports re-authorization and post-authorization (capture) of transactions.
-   **Payment Processor Abstraction:**
    -      Provides a base `PaymentProcessor` class for implementing different payment gateways.
    -      Includes concrete implementations for TSYS (`TSYSProcessor`) and a generic platform (`AnotherPlatformProcessor`).
    -      Allows easy addition of new payment processors.
-   **API Integration:**
    -      Uses the `requests` library to interact with payment processor APIs.
    -      Handles API requests, responses, and error handling.
-   **Logging:**
    -      Uses the `logging` module to record transaction processing and errors.
-   **Data Serialization:**
    -      Converts transaction objects to dictionaries for easy serialization and display using `json`.
-   **Security:**
    -   Masks card numbers and never stores or logs the CVV.

## Requirements

-      Python 3.x
-      `requests` library (`pip install requests`)

## Usage

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install dependencies:**

    ```bash
    pip install requests
    ```

3.  **Configure Payment Processors:**
    -   Modify the `EDCSystem` class in the script to include your specific API keys, URLs, and any other necessary credentials for the payment processors you wish to use.
    -   **Important:** Handle API keys and credentials securely. Do not store them directly in the code. Use environment variables or secure configuration files.

4.  **Run the script:**

    ```bash
    python <your_script_name>.py
    ```

5.  **Interact with the system:**
    -   The script will prompt you to enter transaction details.
    -   You can choose to process transactions using TSYS or another platform.
    -   The script will display the transaction results and log the process.

## Example

```python
if __name__ == "__main__":
    edc = EDCSystem()

    # Capture transaction data
    new_transaction = edc.capture_transaction_data()

    # Process the transaction with TSYS
    processed_tsys_transaction = edc.process_transaction(new_transaction.copy(), platform="tsys")
    print("\nTSYS Processing Result:")
    print(json.dumps(processed_tsys_transaction.to_dict(), indent=4))

    # View all captured transactions
    print("\nAll Transactions:")
    edc.view_transactions()