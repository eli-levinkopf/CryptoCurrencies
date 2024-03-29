from .utils import PublicKey, Signature, TxID
from typing import Optional
import hashlib


class Transaction:
    """Represents a transaction that moves a single coin
    A transaction with no source creates money. It will only be created by the miner of a block."""

    def __init__(self, output: PublicKey, tx_input: Optional[TxID], signature: Signature) -> None:
        # DO NOT change these field names.
        self.output: PublicKey = output
        # DO NOT change these field names.
        self.input: Optional[TxID] = tx_input
        # DO NOT change these field names.
        self.signature: Signature = signature
        self._message = output
        # self._message = self.output + self.input if self.input else self.output
        if tx_input: 
            self._message += tx_input
            self.__minner_tx = False
        else: 
            self.__minner_tx = True
        

    def get_output(self) -> PublicKey:
        return self.output

    def get_input(self) -> Optional[TxID]:
        return self.input

    def get_signature(self) -> Signature:
        return self.signature

    def get_message(self) -> bytes:
        return self._message

    def get_minner_tx(self):
        return self.__minner_tx

    def get_txid(self) -> TxID:
        """
        Returns the identifier of this transaction. This is the sha256 of the transaction contents.
        This function is used by the tests to compute the tx hash. Make sure to compute this every time 
        directly from the data in the transaction object, and not cache the result
        """
        txid = hashlib.sha256()
        txid.update(self._message + self.signature)
        return TxID(txid.digest())
    