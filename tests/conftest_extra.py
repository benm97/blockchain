import pytest
from ex1 import Transaction, Wallet, Bank


@pytest.fixture
def rich_dude(bank) -> Wallet:
    rich_dude = Wallet()
    for _ in range(15):
        bank.create_money(rich_dude.get_address())
        bank.end_day()
        bank.end_day()
        rich_dude.update(bank)
    return rich_dude
