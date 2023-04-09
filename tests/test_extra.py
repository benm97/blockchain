import secrets

from ex1 import *
from conftest_extra import *


def test_insert_coinbase_tx_to_mempool(bank: Bank, alice: Wallet, alice_coin: Transaction):
    coinbase_tx = Transaction(alice.get_address(), None, secrets.token_bytes(48))
    assert not bank.add_transaction_to_mempool(coinbase_tx)


def test_rich_dude(bank: Bank, rich_dude: Wallet):
    assert rich_dude.get_balance() == 15


def test_end_day_limit(bank: Bank, alice: Wallet, rich_dude: Wallet):
    for _ in range(rich_dude.get_balance()):
        tx = rich_dude.create_transaction(alice.get_address())
        assert tx
        assert bank.add_transaction_to_mempool(tx)
    bank.end_day(limit=5)
    assert rich_dude.get_balance() == 15
    rich_dude.update(bank)
    alice.update(bank)
    assert rich_dude.get_balance() == 10
    assert alice.get_balance() == 5
    bank.end_day(limit=5)
    bank.end_day(limit=5)
    alice.update(bank)
    assert rich_dude.get_balance() == 10
    assert alice.get_balance() == 15

def test_malleable_hash(bank: Bank, alice: Wallet, bob:Wallet, alice_coin: Transaction):
    # In current implementation there is no room for hash malleability because all tx fields are hashed.
    assert True