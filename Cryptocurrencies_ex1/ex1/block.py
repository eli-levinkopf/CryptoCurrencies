from .utils import BlockHash, Encoding, GENESIS_BLOCK_PREV
from .transaction import Transaction
from typing import List, Optional
import hashlib


class Block:
    # implement __init__ as you see fit.

    def __init__(self, transactions: Optional[List[Transaction]] = [], prev_block_hash: Optional[BlockHash] = None) -> None:
        self.__transactions: Optional[List[Transaction]] = transactions
        self.__prev_block_hash: Optional[BlockHash] = prev_block_hash
        if prev_block_hash:
            self.__first_block = False
        else:
            self.__prev_block_hash = GENESIS_BLOCK_PREV
            self.__first_block = True

    def get_block_hash(self) -> BlockHash:
        """
        calculate the block hash according to all TxID of transactions
        in the block and the previous block hash (if exists).
        returns hash of this block.
        """
        block_hash = hashlib.sha256()
        if self.__transactions:
            for tx in self.__transactions:
                block_hash.update(tx.get_txid())
            if self.__prev_block_hash:
                block_hash.update(self.__prev_block_hash)
        return BlockHash(block_hash.digest())

    def get_transactions(self) -> Optional[List[Transaction]]:
        """returns the list of transactions in this block."""
        return self.__transactions

    def get_prev_block_hash(self) -> Optional[BlockHash]:
        """Gets the hash of the previous block in the chain"""
        return self.__prev_block_hash
