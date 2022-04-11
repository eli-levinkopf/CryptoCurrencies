from .utils import BlockHash, GENESIS_BLOCK_PREV
from .transaction import Transaction
from typing import List
import hashlib


class Block:
    """This class represents a block."""

    def __init__(self, prev_block_hash: BlockHash = GENESIS_BLOCK_PREV,transactions: List[Transaction] = []) -> None:
        self.__transactions: List[Transaction] = transactions
        self.__prev_block_hash: BlockHash = prev_block_hash

    def get_block_hash(self) -> BlockHash:
        """Gets the hash of this block. 
        This function is used by the tests. Make sure to compute the result from the data in the block every time 
        and not to cache the result"""
        block_hash = hashlib.sha256()
        if self.__transactions:
            for tx in self.__transactions:
                block_hash.update(tx.get_txid())
        if self.__prev_block_hash:
            block_hash.update(self.__prev_block_hash)
        return BlockHash(block_hash.digest())


    def get_transactions(self) -> List[Transaction]:
        """
        returns the list of transactions in this block.
        """
        return self.__transactions

    def get_prev_block_hash(self) -> BlockHash:
        """Gets the hash of the previous block"""
        return self.__prev_block_hash


