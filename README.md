# Electronic Data Capture (EDC) System

This project implements a basic Electronic Data Capture (EDC) system for processing financial transactions. It supports multiple payment processors (TSYS and another platform) and includes functionality for capturing transaction data, processing payments, re-authorizing transactions, and completing pre-authorized payments. It also incorporates Value-Added Reseller (VAR) sheet parameters for more detailed transaction information.

## Features

* **Transaction Management:**
    * Captures transaction details (amount, currency, card number, expiry, CVV, customer ID).
    * Generates unique transaction IDs.
    * Stores transaction history.
    * Masks sensitive card data for security.
* **Payment Processing:**
    * Supports multiple payment processors (TSYS and Another Platform).
    * Processes payment transactions through specified processors.
    * Handles transaction status updates (Approved, Failed, etc.).
    * Includes VAR sheet parameters in the transaction flow.
* **Transaction Operations:**
    * Re-authorizes transactions with new amounts.
    * Completes pre-authorized transactions (post-authorization/capture).
    * Logs all transaction process using the logging module.
* **VAR Sheet Support:**
    * Includes VAR sheet parameters (Merchant Number, Acquirer BIN, Store Number, Terminal Number, MCC, Location Number, Vital Number, Agent Bank, Agent Chain).
    * Stores and processes VAR sheet data with transactions.
* **Extensibility:**
    * Modular design allows for easy addition of new payment processors.

## Getting Started

### Prerequisites

* Python 3.x
* `requests` library (`pip install requests`)

### Installation

1.  Clone the repository:

    ```bash
    git clone <repository_url>
    cd edc-system
    ```

2.  Install the required dependencies:

    ```bash
    pip install requests
    ```

3.  Configure the payment processor credentials:

    * Update the `EDCSystem` class in `edc_system.py` with your TSYS API key and Another Platform credentials.
    * Replace the placeholder URLs with your actual payment processor API endpoints.

4. Run the program:

    ```bash
    python edc_system.py
    ```

### Usage

The application will prompt you to enter transaction details. Follow the on-screen instructions to process transactions, re-authorize payments, and view transaction history.

## Code Structure

* **`edc_system.py`:** Contains the main application logic, including the `Transaction`, `PaymentProcessor`, `TSYSProcessor`, `AnotherPlatformProcessor`, and `EDCSystem` classes.

* **`Transaction` class:** Represents a financial transaction and its associated data.

* **`PaymentProcessor` class:** Base class for payment processors.

* **`TSYSProcessor` and `AnotherPlatformProcessor` classes:** Implement specific payment processing logic for TSYS and another platform.

* **`EDCSystem` class:** Manages transactions and interacts with payment processors.

## VAR Sheet Parameters

The VAR sheet parameters are included in the `Transaction` class and processed by the payment processors. These parameters provide detailed information about the transaction, such as:

* **Merchant Number (MID)**
* **Acquirer BIN**
* **Store Number**
* **Terminal Number**
* **Merchant Category Code (MCC)**
* **Location Number**
* **Vital Number**
* **Agent Bank**
* **Agent Chain**

## Logging

The application uses the `logging` module to record transaction processing events and errors. Logs are output to the console.

## Security Considerations

* Sensitive data, such as card numbers and CVV, is masked and never stored or logged in full.
* In a production environment, payment processor credentials and sensitive data should be handled securely using environment variables or secure configuration management.
* The payment processor API calls should be implemented with proper error handling and security measures.

## Future Enhancements

* Implement a user interface for easier transaction management.
* Add support for more payment processors.
* Implement data persistence (e.g., database storage).
* Add more robust error handling and input validation.
* Implement unit tests.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues to suggest improvements or report bugs.