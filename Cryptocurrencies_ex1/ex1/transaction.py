from .utils import PublicKey, TxID, Signature
from typing import Optional
import hashlib


class Transaction:
    """Represents a transaction that moves a single coin
    A transaction with no source creates money. It will only be created by the bank."""

    def __init__(self, output: PublicKey, input: Optional[TxID], signature: Signature) -> None:
        # do not change the name of this field:
        self.output: PublicKey = output
        # do not change the name of this field:
        self.input: Optional[TxID] = input
        # do not change the name of this field:
        self.signature: Signature = signature
        self.__message: bytes = output
        # bank_transaction = True iff the transaction is a bank transaction (without input)
        if input:
            self.__message += input
            self.__bank_transaction = False
        else:
            self.__bank_transaction = True

    def get_output(self) -> PublicKey:
        return self.output

    def get_input(self) -> Optional[TxID]:
        return self.input

    def get_signature(self) -> Signature:
        return self.signature

    def get_message(self) -> bytes:
        return self.__message

    def get_txid(self) -> TxID:
        """Returns the identifier of this transaction. This is the SHA256 of the transaction contents."""
        txid = hashlib.sha256()
        header_hex = self.output + self.signature
        if type(self.input) is bytes:
            header_hex += self.input
        txid.update(header_hex)
        return TxID(txid.digest())
