import hashlib
import json
from typing import List, cast

from .transaction import Transaction
from .utils import BlockHash


class Block:
    # implement __init__ as you see fit.
    def __init__(self, transactions: List[Transaction], prev_block_hash: BlockHash) -> None:
        self.__transactions: List[Transaction] = transactions
        self.__prev_block_hash: BlockHash = prev_block_hash

    def get_block_hash(self) -> BlockHash:
        """returns hash of this block"""
        block_json = json.dumps(self, sort_keys=True).encode()
        return cast(BlockHash, hashlib.sha256(block_json).digest())

    def get_transactions(self) -> List[Transaction]:
        """returns the list of transactions in this block."""
        return self.__transactions

    def get_prev_block_hash(self) -> BlockHash:
        """Gets the hash of the previous block in the chain"""
        return self.__prev_block_hash
