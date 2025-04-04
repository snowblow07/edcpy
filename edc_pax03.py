import socket
import time

def send_transaction(ip, port, amount):
    try:
        # Connect to the PAX S300 terminal
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, port))
            
            # Format the transaction request (Example: Sale transaction with amount $10.00)
            transaction_request = (
                "\x02"  # Start of text (STX)
                "T00"  # Transaction type: Sale
                "000000000001"  # Amount: $0.01 (in cents)
                "\x03"  # End of text (ETX)
            )
            
            # Calculate LRC (Longitudinal Redundancy Check) for data integrity
            lrc = 0
            for char in transaction_request[1:]:  # Exclude STX
                lrc ^= ord(char)
            
            # Append LRC to the transaction request
            transaction_request += chr(lrc)
            
            # Send the request to the terminal
            s.sendall(transaction_request.encode('latin1'))
            
            # Wait for response
            time.sleep(2)
            response = s.recv(1024)
            
            print("Response from terminal:", response.decode('latin1'))
            
    except Exception as e:
        print("Error communicating with PAX S300:", e)

if __name__ == "__main__":
    PAX_IP = "10.0.0.155"
    PAX_PORT = 10009  # Default PAX S300 port
    AMOUNT = 0.01  # Amount in dollars
    
    send_transaction(PAX_IP, PAX_PORT, AMOUNT)

# 
# CONNECTION ESTABLISHED SUCCESSFULLY!!
# URRA!!!