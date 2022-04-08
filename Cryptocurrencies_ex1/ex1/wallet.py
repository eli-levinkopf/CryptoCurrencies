from ast import Break
from tkinter import FIRST
from tkinter.messagebox import NO
from .utils import *
from .transaction import Transaction
from .bank import Bank
from typing import Optional, List
from .block import Block

UTXO = 0
NOT_IN_BLOCK = 1
FIRST_TX = 0

class Wallet:
    def __init__(self) -> None:
        """This function generates a new wallet with a new private key."""
        self.__private_key, self.__public_key = gen_keys()
        self.__latest_update: Optional[Block] = None
        self.__balance: int = 0
        # List[List[TxID], List[TxID]] = [[unspend txid], [not in block yet txid]]
        self.__txid: List[List[TxID], List[TxID]] = [[], []]

    def update(self, bank: Bank) -> None:
        """
        This function updates the balance allocated to this wallet by querying the bank.
        Don't read all of the bank's utxo, but rather process the blocks since the last update one at a time.
        For this exercise, there is no need to validate all transactions in the block.
        """
        latest_block = bank.get_block(bank.get_latest_hash())
        block_to_update = latest_block
        while self.__latest_update != latest_block:
            for tx in latest_block.get_transactions():
                txid = tx.get_txid()
                if tx.get_output() == self.__public_key and txid not in self.__txid[UTXO] and txid not in self.__txid[NOT_IN_BLOCK]:
                    self.__balance += 1
                    self.__txid[UTXO].append(txid)
                elif tx.get_input() in self.__txid[1] or tx.get_input() in self.__txid[UTXO]:
                    self.__balance -= 1
                    self.__txid[NOT_IN_BLOCK].remove(tx.get_input())
            latest_hash = latest_block.get_prev_block_hash()
            if latest_hash is GENESIS_BLOCK_PREV:
                self.__latest_update = latest_block
                break
            if type(latest_hash) == bytes:
                latest_block = bank.get_block(latest_hash)
        self.__latest_update = block_to_update

    def create_transaction(self, target: PublicKey) -> Optional[Transaction]:
        """
        This function returns a signed transaction that moves an unspent coin to the target.
        It chooses the coin based on the unspent coins that this wallet had since the last update.
        If the wallet already spent a specific coin, but that transaction wasn't confirmed by the
        bank just yet (it still wasn't included in a block) then the wallet should'nt spend it again
        until unfreeze_all() is called. The method returns None if there are no unspent outputs that can be used.
        """
        if not self.__balance or not self.__txid[UTXO]:
            return None
        signature = sign(target + self.__txid[UTXO][FIRST_TX], self.__private_key)
        tx = Transaction(
            output=target, input=self.__txid[UTXO][FIRST_TX], signature=signature)
        self.__txid[1].append(self.__txid[UTXO][FIRST_TX])
        del self.__txid[UTXO][FIRST_TX]
        return tx
        
    def unfreeze_all(self) -> None:
        """
        Allows the wallet to try to re-spend outputs that it created transactions for (unless these outputs made it into the blockchain).
        """
        for txid in self.__txid[NOT_IN_BLOCK]:
            self.__txid[UTXO].append(txid)
        self.__txid[NOT_IN_BLOCK] = []

    def get_balance(self) -> int:
        """
        This function returns the number of coins that this wallet has.
        It will return the balance according to information gained when update() was last called.
        Coins that the wallet owned and sent away will still be considered as part of the balance until the spending
        transaction is in the blockchain.
        """
        return self.__balance

    def get_address(self) -> PublicKey:
        """
        This function returns the public address of this wallet (see the utils module for generating keys).
        """
        return self.__public_key
