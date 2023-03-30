import json
from typing import Optional, List

from .block import Block
from .bank import Bank
from .transaction import Transaction
from .utils import *


class Wallet:
    def __init__(self) -> None:
        """This function generates a new wallet with a new private key."""
        keys: Tuple[PrivateKey, PublicKey] = gen_keys()
        self.__private_key: PrivateKey = keys[0]
        self.__public_key: PublicKey = keys[1]
        self.__unspent_transactions: List[Transaction] = []
        self.__last_updated_block_hash: BlockHash = GENESIS_BLOCK_PREV
        self.__frozen_transactions: List[Transaction] = []

    def update(self, bank: Bank) -> None:
        """
        This function updates the balance allocated to this wallet by querying the bank.
        Don't read all of the bank's utxo, but rather process the blocks since the last update one at a time.
        For this exercise, there is no need to validate all transactions in the block.
        """

        new_blocks: List[Block] = self.__get_new_blocks(bank)
        for block in new_blocks:
            self.__update_unspent_transactions_with_block(block)

    def create_transaction(self, target: PublicKey) -> Optional[Transaction]:
        """
        This function returns a signed transaction that moves an unspent coin to the target.
        It chooses the coin based on the unspent coins that this wallet had since the last update.
        If the wallet already spent a specific coin, but that transaction wasn't confirmed by the
        bank just yet (it still wasn't included in a block) then the wallet  should'nt spend it again
        until unfreeze_all() is called. The method returns None if there are no unspent outputs that can be used.
        """
        available_coin: Optional[Transaction] = next(
            (transaction for transaction in self.__unspent_transactions if
             transaction not in self.__frozen_transactions), None)
        if available_coin is None:
            return None
        signature: Signature = sign(json.dumps(self.__build_message(available_coin, target), sort_keys=True).encode(), self.__private_key)
        self.__frozen_transactions.append(available_coin)
        return Transaction(target, available_coin.get_txid(), signature)

    def unfreeze_all(self) -> None:
        """
        Allows the wallet to try to re-spend outputs that it created transactions for (unless these outputs made it into the blockchain).
        """
        self.__frozen_transactions.clear()

    def get_balance(self) -> int:
        """
        This function returns the number of coins that this wallet has.
        It will return the balance according to information gained when update() was last called.
        Coins that the wallet owned and sent away will still be considered as part of the balance until the spending
        transaction is in the blockchain.
        """
        return len(self.__unspent_transactions)

    def get_address(self) -> PublicKey:
        """
        This function returns the public address of this wallet (see the utils module for generating keys).
        """
        return self.__public_key

    def __get_new_blocks(self, bank: Bank) -> List[Block]:
        new_blocks: List[Block] = []
        current_block_hash: BlockHash = bank.get_latest_hash()
        while current_block_hash != self.__last_updated_block_hash:
            current_block: Block = bank.get_block(current_block_hash)
            new_blocks.append(current_block)
            current_block_hash = current_block.get_prev_block_hash()
        self.__last_updated_block_hash = bank.get_latest_hash()
        return new_blocks

    def __update_unspent_transactions_with_block(self, block: Block) -> None:
        inbound_transactions: List[Transaction] = [transaction for transaction in block.get_transactions() if
                                                   transaction.output == self.get_address()]
        self.__unspent_transactions.extend(inbound_transactions)

        new_transactions_input: List[Optional[TxID]] = [transaction.input for transaction in block.get_transactions()]
        self.__unspent_transactions = [unspent_transaction for unspent_transaction in self.__unspent_transactions if
                                       unspent_transaction.get_txid() not in new_transactions_input]

    @staticmethod
    def __build_message(input, output):
        return {"input": str(input.get_txid()),
                "output": str(output)}
