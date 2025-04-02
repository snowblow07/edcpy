import unittest
import json
from edc_pre_post_test import EDCSystem, Transaction  # Assuming your file is named edc_pre_post_test.py

class TestEDCSystem(unittest.TestCase):

    def setUp(self):
        self.edc = EDCSystem()
        self.transaction_data = {
            "amount": 100.00,
            "currency": "USD",
            "card_number": "1234567890123456",
            "expiry_date": "12/24",
            "cvv": "123",
            "customer_id": "cust123",
            "var_sheet": {
                "merchant_number": "12345",
                "acquirer_bin": "67890",
                "store_number": "11",
                "terminal_number": "22",
                "mcc": "3333",
                "location_number": "44",
                "vital_number": "55",
                "agent_bank": "66",
            }
        }
        self.transaction = Transaction(**self.transaction_data)

    def test_process_transaction(self):
        processed_transaction = self.edc.process_transaction(self.transaction.copy())
        self.assertIn(processed_transaction.status, ["Approved", "Failed"])
        self.assertIsNotNone(processed_transaction.processor_response)

    def test_reauthorize_transaction(self):
        processed_transaction = self.edc.process_transaction(self.transaction.copy())
        reauthorized_transaction = self.edc.reauthorize_transaction(processed_transaction.copy(), 110.00)
        self.assertIn(reauthorized_transaction.status, ["Re-authorized", "Re-authorization Failed"])
        self.assertIsNotNone(reauthorized_transaction.processor_response)

    def test_post_authorize_transaction(self):
        processed_transaction = self.edc.process_transaction(self.transaction.copy())
        reauthorized_transaction = self.edc.reauthorize_transaction(processed_transaction.copy(), 110.00)
        captured_transaction = self.edc.post_authorize_transaction(reauthorized_transaction.copy())
        self.assertIn(captured_transaction.status, ["Captured", "Capture Failed"])
        self.assertIsNotNone(captured_transaction.processor_response)

    def test_transaction_masking(self):
        masked_card = self.transaction.card_number
        self.assertTrue(masked_card.startswith("X" * 12))
        self.assertTrue(masked_card.endswith("3456"))

    def test_transaction_copy(self):
        copied_transaction = self.transaction.copy()
        self.assertEqual(self.transaction.amount, copied_transaction.amount)
        self.assertNotEqual(self.transaction.cvv, copied_transaction.cvv) #cvv should always be masked.
        self.assertEqual(self.transaction.var_sheet, copied_transaction.var_sheet)

    def test_view_transactions(self):
        self.edc.process_transaction(self.transaction.copy())
        self.edc.process_transaction(self.transaction.copy())
        # Capture stdout to check printed output.
        import io, sys
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        self.edc.view_transactions()
        sys.stdout = sys.__stdout__
        output = capturedOutput.getvalue()
        self.assertTrue(output.count(self.transaction.transaction_id) == 2 ) #make sure two transactions were printed.

    def test_transaction_to_dict(self):
        transaction_dict = self.transaction.to_dict()
        self.assertEqual(transaction_dict["amount"], self.transaction_data["amount"])
        self.assertEqual(transaction_dict["currency"], self.transaction_data["currency"])
        self.assertTrue(transaction_dict["card_number"].startswith("X" * 12))
        self.assertEqual(transaction_dict["expiry_date"], self.transaction_data["expiry_date"])
        self.assertEqual(transaction_dict["var_sheet"], self.transaction_data["var_sheet"])

if __name__ == '__main__':
    unittest.main()