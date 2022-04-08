from .utils import BlockHash, PublicKey, TxID, Signature, verify
from .transaction import Transaction
from .block import Block
from typing import List
import secrets


class Bank:
    def __init__(self) -> None:
        """Creates a bank with an empty blockchain and an empty mempool."""
        self.__blockchain: List[Block] = []
        self.__mempool: List[Transaction] = []
        self.__utxo: List[Transaction] = []
        self.__inputs: List[TxID] = []

    def get_blockchain(self):
        return self.__blockchain

    def get_inputs(self):
        return self.__inputs

    def add_transaction_to_mempool(self, transaction: Transaction) -> bool:
        """
        This function inserts the given transaction to the mempool.
        It will return False iff one of the following conditions hold:
        (i) the transaction is invalid (the signature fails) V
        (ii) the source doesn't have the coin that he tries to spend
        (iii) there is contradicting tx in the mempool. V
        (iv) there is no input (i.e., this is an attempt to create money from nothing) V
        """
        if not self.__check_transaction(transaction):
            return False

        input = transaction.get_input()
        if input:
            self.__inputs.append(input)

        # remove from utxo the tx that transaction spend
        txid = transaction.get_input()
        for tx in self.__utxo:
            if txid == tx.get_txid():
                self.__utxo.remove(tx)

        self.__mempool.append(transaction)
        if transaction not in self.__inputs:
            self.__utxo.append(transaction)
        return True

    def end_day(self, limit: int = 10) -> BlockHash:
        """
        This function tells the bank that the day ended,
        and that the first `limit` transactions in the mempool should be committed to the blockchain.
        If there are fewer than 'limit' transactions in the mempool, a smaller block is created.
        If there are no transactions, an empty block is created. The hash of the block is returned.
        """
        self.__update_utxo()

        prev_block_hash = self.__blockchain[-1].get_block_hash(
        ) if self.__blockchain else None

        if len(self.__mempool) >= limit:
            new_block = Block(self.__mempool[:limit], prev_block_hash)
            del self.__mempool[:limit]

        elif len(self.__mempool):
            new_block = Block(self.__mempool[::], prev_block_hash)
            del self.__mempool[::]

        else:
            new_block = Block(prev_block_hash=prev_block_hash)

        self.__blockchain.append(new_block)

        return new_block.get_block_hash()

    def get_block(self, block_hash: BlockHash) -> Block:
        """
        This function returns a block object given its hash. If the block doesnt exist, an exception is thrown..
        """
        for block in self.__blockchain:
            if block.get_block_hash() == block_hash:
                return block
        raise ValueError("block hash does not exist in blockchain")

    def get_latest_hash(self) -> BlockHash:
        """
        This function returns the hash of the last Block that was created by the bank.
        """
        try:
            return self.__blockchain[-1].get_block_hash()
        except:
            raise ValueError("The blockchain does not contain any blocks")

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
        signature = Signature(secrets.token_bytes(48))
        new_transactions = Transaction(
            output=target, input=None, signature=signature)
        self.__mempool.append(new_transactions)

    def __check_transaction(self, transaction: Transaction) -> bool:
        sender = None
        for tx in self.__utxo:
            if tx.get_txid() == transaction.get_input():
                sender = tx

        if not sender:
            return False

        if not verify(transaction.get_message(), transaction.get_signature(), sender.get_output()):
            return False

        if transaction.get_input() in self.__inputs:
            return False

        if not transaction.get_input():
            return False

        return True

    def __update_utxo(self) -> None:
        for tx in self.__mempool:
            if tx not in self.__inputs and tx not in self.__utxo:
                self.__utxo.append(tx)
