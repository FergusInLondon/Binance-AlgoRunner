import unittest
import json
from account import Account

def get_payload(fixture):
    with open(f"test/fixtures/{fixture}.json") as json_file:
        data = json.load(json_file)
    return data

class TestAccount(unittest.TestCase):
    def test_account_init(self):
        acc = Account(get_payload("account"))

        self.assertTrue(acc.capability_trade())
        self.assertTrue(acc.capability_withdraw())
        self.assertFalse(acc.capability_deposit())

        self.assertIsNone(acc.balance("NONEXISTANT"), None)
        self.assertEqual(acc.balance("BTC"), (
            float("4723846.89208129"), float(0)))
        self.assertEqual(acc.balance("LTC"), (
            float("4763368.68006011"), float(0)))

    def test_account_update(self):
        acc = Account(get_payload("account"))
        acc(get_payload("outbound_account_info"))

        self.assertTrue(acc.capability_trade())
        self.assertTrue(acc.capability_withdraw())
        self.assertTrue(acc.capability_deposit())

        self.assertIsNone(acc.balance("NONEXISTANT"), None)
        self.assertEqual(acc.balance("BTC"), (
            float("10537.85314051"), float("2.19464093")))
        self.assertEqual(acc.balance("LTC"), (
            float("17366.18538083"), float(0)))
        self.assertEqual(acc.balance("ETH"), (
            float("17902.35190619"), float(0)))
        self.assertEqual(acc.balance("BNC"), (
            float("1114503.29769312"), float(0))) 
        self.assertEqual(acc.balance("NEO"), (
            float(0), float(0)))

    def test_position_update(self):
        acc = Account(get_payload("account"))
        acc(get_payload("outbound_account_info"))
        acc(get_payload("outbound_account_position"))

        self.assertEqual(acc.balance("ETH"), (
            float("10000.000000"), float(0)
        ))

    def test_balance_update(self):
        acc = Account(get_payload("account"))
        acc(get_payload("outbound_account_info"))
        acc(get_payload("balance_update"))

        self.assertEqual(acc.balance("BTC"), (
            (float("10537.85314051") + float("100.00000000")),
            float("2.19464093")))

if __name__ == "__main__":
    unittest.main()
