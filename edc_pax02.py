import requests

PAX_IP = "10.0.0.155"
PAX_PORT = 10009
url = f"http://{PAX_IP}:{PAX_PORT}/transaction"

payload = {
    "transactionType": "sale",
    "amount": "0.01"
}

response = requests.post(url, data=payload)

print("Response from terminal:", response.text)
