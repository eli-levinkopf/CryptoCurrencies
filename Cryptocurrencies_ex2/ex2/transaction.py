from .utils import PublicKey, Signature, TxID
from typing import Optional
<<<<<<< HEAD
import hashlib
=======
>>>>>>> 9d7dcba9d7f7c8bf518f932470a08ea5fb0c2e99


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
<<<<<<< HEAD
        # self._message = output
        self._message = self.output + self.input if self.input else self.output

    def get_output(self) -> PublicKey:
        return self.output

    def get_input(self) -> Optional[TxID]:
        return self.input

    def get_signature(self) -> Signature:
        return self.signature

    def get_message(self) -> bytes:
        return self._message
=======
>>>>>>> 9d7dcba9d7f7c8bf518f932470a08ea5fb0c2e99

    def get_txid(self) -> TxID:
        """
        Returns the identifier of this transaction. This is the sha256 of the transaction contents.
        This function is used by the tests to compute the tx hash. Make sure to compute this every time 
        directly from the data in the transaction object, and not cache the result
        """
<<<<<<< HEAD
        txid = hashlib.sha256()
        txid.update(self._message + self.signature)
        return TxID(txid.digest())
        
=======
        raise NotImplementedError()
>>>>>>> 9d7dcba9d7f7c8bf518f932470a08ea5fb0c2e99


"""
Importing this file should NOT execute code. It should only create definitions for the objects above.
Write any tests you have in a different file.
You may add additional methods, classes and files but be sure no to change the signatures of methods
included in this template.
"""
