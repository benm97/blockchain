import json
import secrets
from typing import List, cast, Optional

from .block import Block
from .transaction import Transaction
from .utils import BlockHash, PublicKey, Signature, GENESIS_BLOCK_PREV, TxID, verify


class Bank:
    def __init__(self) -> None:
        """Creates a bank with an empty blockchain and an empty mempool."""
        self.__blockchain: List[Block] = []
        self.__mempool: List[Transaction] = []
        self.__utxo: List[Transaction] = []

    def add_transaction_to_mempool(self, transaction: Transaction) -> bool:
        """
        This function inserts the given transaction to the mempool.
        It will return False iff one of the following conditions hold:
        (i) the transaction is invalid (the signature fails)
        (ii) the source doesn't have the coin that he tries to spend
        (iii) there is contradicting tx in the mempool.
        (iv) there is no input (i.e., this is an attempt to create money from nothing)
        """
        if self.__is_transaction_valid(transaction):
            self.__mempool.append(transaction)
            return True
        return False

    def end_day(self, limit: int = 10) -> BlockHash:
        """
        This function tells the bank that the day ended,
        and that the first `limit` transactions in the mempool should be committed to the blockchain.
        If there are fewer than 'limit' transactions in the mempool, a smaller block is created.
        If there are no transactions, an empty block is created. The hash of the block is returned.
        """
        last_index = limit if len(self.__mempool) > limit else len(self.__mempool)
        new_block: Block = Block(self.__mempool[:last_index], self.get_latest_hash())
        self.__blockchain.append(new_block)
        self.__mempool = self.__mempool[last_index:]
        self.__update_utxo_with_last_block()
        return self.get_latest_hash()

    def get_block(self, block_hash: BlockHash) -> Block:
        """
        This function returns a block object given its hash. If the block doesnt exist, an exception is thrown..
        """
        for block in self.__blockchain:
            if block.get_block_hash() == block_hash:
                return block
        raise Exception("Non-existing block")  # TODO create exception

    def get_latest_hash(self) -> BlockHash:
        """
        This function returns the hash of the last Block that was created by the bank.
        """
        if len(self.__blockchain) == 0:
            return GENESIS_BLOCK_PREV
        return self.__blockchain[-1].get_block_hash()

    def get_mempool(self) -> List[Transaction]:
        """
        This function returns the list of transactions that didn't enter any block yet.
        """
        return self.__mempool

    def get_utxo(self) -> List[Transaction]:
        """
        This function returns the list of unspent transactions.
        """
        return self.__utxo

    def create_money(self, target: PublicKey) -> None:
        """
        This function inserts a transaction into the mempool that creates a single coin out of thin air. Instead of a signature,
        this transaction includes a random string of 48 bytes (so that every two creation transactions are different).
        This function is a secret function that only the bank can use (currently for tests, and will make sense in a later exercise).
        """
        self.__mempool.append(Transaction(target, None, cast(Signature, secrets.token_bytes(48))))

    def __update_utxo_with_last_block(self) -> None:
        new_transactions: List[Transaction] = self.__blockchain[-1].get_transactions()
        self.__utxo.extend(new_transactions)
        new_transactions_input: List[Optional[TxID]] = [transaction.input for transaction in new_transactions]
        self.__utxo = [unspent_transaction for unspent_transaction in self.__utxo if
                       unspent_transaction.get_txid() not in new_transactions_input]

    @staticmethod
    def __build_message(transaction: Transaction) -> bytes:
        return json.dumps({"input": str(transaction.input), "output": str(transaction.output)}, sort_keys=True).encode()

    def __is_transaction_valid(self, transaction: Transaction) -> bool:
        if transaction.input is None:
            return False
        if transaction.input in [transaction.input for transaction in self.__mempool]:
            return False
        input_transaction: Optional[Transaction] = next(
            (unspent_transaction for unspent_transaction in self.get_utxo() if
             unspent_transaction.get_txid() == transaction.input), None)
        if input_transaction is None:
            return False
        if not verify(self.__build_message(transaction), transaction.signature, input_transaction.output):
            return False
        return True
