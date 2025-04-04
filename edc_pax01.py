import socket
import json

def send_payment_request(ip_address, amount, currency="USD", transaction_type="SALE"):
    """
    Sends a payment request to a PAX S300 terminal.

    Args:
        ip_address (str): The IP address of the PAX S300 terminal.
        amount (float): The payment amount.
        currency (str): The currency code (e.g., "USD", "EUR").
        transaction_type (str): The transaction type (e.g., "SALE", "REFUND").

    Returns:
        dict: The response from the PAX S300 terminal, or None if an error occurred.
    """

    try:
        # Construct the payment request message
        request = {
            "TransactionType": transaction_type,
            "Amount": "{:.2f}".format(amount), #Format to 2 decimal places
            "Currency": currency,
            "RequestType": "PAYMENT",
            "Version": "1.0" # Example version, adjust as needed.
        }

        # Convert the request to a JSON string
        request_json = json.dumps(request)

        # Create a socket connection to the PAX S300 terminal
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip_address, 10009)) # Default PAX port is 10009. Adjust if needed.

            # Send the request
            s.sendall(request_json.encode())

            # Receive the response (adjust buffer size as needed)
            response_data = s.recv(4096)
            response_json = response_data.decode()

            # Parse the response JSON
            response = json.loads(response_json)
            return response

    except (socket.error, json.JSONDecodeError, Exception) as e:
        print(f"Error: {e}")
        return None

# Example usage:
ip_address = "10.0.0.155"
amount = 0.01

response = send_payment_request(ip_address, amount)

if response:
    print("PAX S300 Response:")
    print(json.dumps(response, indent=4)) #Pretty print the Json

    if response.get("ResponseCode") == "00": #Example of success code, check your PAX documentation.
        print("Payment successful!")
    else:
        print(f"Payment failed: {response.get('ResponseText')}")
else:
    print("Failed to communicate with the PAX S300 terminal.")