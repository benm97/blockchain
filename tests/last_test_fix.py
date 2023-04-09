from ex1 import Wallet, Bank


def test_create_transaction_end_day_and_then_unfreeze_all_without_update(
        alice: Wallet,
        bob: Wallet,
        bank: Bank
):
    bank.create_money(alice.get_address())
    bank.create_money(alice.get_address())
    bank.end_day()
    alice.update(bank)
    assert alice.get_balance() == 2

    tx1 = alice.create_transaction(bob.get_address())
    bank.add_transaction_to_mempool(tx1)
    bank.end_day()
    alice.unfreeze_all()
    assert alice.get_balance() == 2

    tx2 = alice.create_transaction(bob.get_address())
    assert tx2 is not None
    tx3 = alice.create_transaction(bob.get_address())
    assert tx3 is not None

    assert (
            {False, True}
            ==
            {
                bank.add_transaction_to_mempool(tx2),
                bank.add_transaction_to_mempool(tx3),
            }
    )

    bank.end_day()
    alice.update(bank)
    assert not alice.get_balance()
    