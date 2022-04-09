from .utils import *
from .block import Block
from .transaction import Transaction
<<<<<<< HEAD
from typing import Dict, Set, Optional, List

CONECTION_ERROR = "node can't connect to itself"
BLOCK_HASH_ERROR = "block hash does not exist in blockchain"
LATEST_HASH_ERROR = "The blockchain does not contain any blocks"
=======
from typing import Set, Optional, List
>>>>>>> 9d7dcba9d7f7c8bf518f932470a08ea5fb0c2e99


class Node:
    def __init__(self) -> None:
        """Creates a new node with an empty mempool and no connections to others.
        Blocks mined by this node will reward the miner with a single new coin,
        created out of thin air and associated with the mining reward address"""
<<<<<<< HEAD
        # {Tx: True iff node.public_key is the output of Tx}
        self.__mempool: List[Transaction, bool] = []
        self.__blockchain: List[Block] = []
        self.__utxo: List[Transaction] = []
        self.__connections: Set['Node'] = []
        self.__private_key,  self.__public_key = gen_keys()
        self.__balance: int = 0
        self.__blocks_hash: List[BlockHash] = []
=======
        raise NotImplementedError()
>>>>>>> 9d7dcba9d7f7c8bf518f932470a08ea5fb0c2e99

    def connect(self, other: 'Node') -> None:
        """connects this node to another node for block and transaction updates.
        Connections are bi-directional, so the other node is connected to this one as well.
        Raises an exception if asked to connect to itself.
        The connection itself does not trigger updates about the mempool,
        but nodes instantly notify of their latest block to each other (see notify_of_block)"""
<<<<<<< HEAD
        if other is self:
            raise ValueError (CONECTION_ERROR)
        self.__connections.add(other)
        other.__connections.add(self)

    def disconnect_from(self, other: 'Node') -> None:
        """Disconnects this node from the other node. If the two were not connected, then nothing happens"""
        if other in self.__connections:
            del self.__connections[other]
            other.__connections.remove(self)

    def get_connections(self) -> Set['Node']:
        """Returns a set containing the connections of this node."""
        return self.__connections
=======
        raise NotImplementedError()

    def disconnect_from(self, other: 'Node') -> None:
        """Disconnects this node from the other node. If the two were not connected, then nothing happens"""
        raise NotImplementedError()

    def get_connections(self) -> Set['Node']:
        """Returns a set containing the connections of this node."""
        raise NotImplementedError()
>>>>>>> 9d7dcba9d7f7c8bf518f932470a08ea5fb0c2e99

    def add_transaction_to_mempool(self, transaction: Transaction) -> bool:
        """
        This function inserts the given transaction to the mempool.
        It will return False iff any of the following conditions hold:
        (i) the transaction is invalid (the signature fails)
        (ii) the source doesn't have the coin that it tries to spend
        (iii) there is contradicting tx in the mempool.

        If the transaction is added successfully, then it is also sent to neighboring nodes.
        """
<<<<<<< HEAD
        # TDDT: sender
        sender = None 
        if not verify(transaction.get_message(), transaction.get_signature(), sender.get_output()):
            return False

        if not transaction.get_input(): return False

        for tx in self.__mempool:
            if tx.get_input == transaction.get_input(): return False
        
        for neighbor in self.__connections:
            neighbor.add_transaction_to_mempool(transaction)
        return True
        
=======
        raise NotImplementedError()
>>>>>>> 9d7dcba9d7f7c8bf518f932470a08ea5fb0c2e99

    def notify_of_block(self, block_hash: BlockHash, sender: 'Node') -> None:
        """This method is used by a node's connection to inform it that it has learned of a
        new block (or created a new block). If the block is unknown to the current Node, The block is requested.
        We assume the sender of the message is specified, so that the node can choose to request this block if
        it wishes to do so.
        (if it is part of a longer unknown chain, these blocks are requested as well, until reaching a known block).
        Upon receiving new blocks, they are processed and and checked for validity (check all signatures, hashes,
        block size , etc).
        If the block is on the longest chain, the mempool and utxo change accordingly.
        If the block is indeed the tip of the longest chain,
        a notification of this block is sent to the neighboring nodes of this node.
        (no need to notify of previous blocks -- the nodes will fetch them if needed)

        A reorg may be triggered by this block's introduction. In this case the utxo is rolled back to the split point,
        and then rolled forward along the new branch.
        the mempool is similarly emptied of transactions that cannot be executed now.
        transactions that were rolled back and can still be executed are re-introduced into the mempool if they do
        not conflict.
        """
<<<<<<< HEAD
        if block_hash not in self.__blocks_hash:
            pass

        
=======
        raise NotImplementedError()
>>>>>>> 9d7dcba9d7f7c8bf518f932470a08ea5fb0c2e99

    def mine_block(self) -> BlockHash:
        """"
        This function allows the node to create a single block.
        The block should contain BLOCK_SIZE transactions (unless there aren't enough in the mempool). Of these,
        BLOCK_SIZE-1 transactions come from the mempool and one addtional transaction will be included that creates
        money and adds it to the address of this miner.
        Money creation transactions have None as their input, and instead of a signature, contain 48 random bytes.
        If a new block is created, all connections of this node are notified by calling their notify_of_block() method.
        The method returns the new block hash (or None if there was no block)
        """
        raise NotImplementedError()

    def get_block(self, block_hash: BlockHash) -> Block:
        """
        This function returns a block object given its hash.
        If the block doesnt exist, a ValueError is raised.
        """
<<<<<<< HEAD
        for block in self.__blockchain:
            if block.get_block_hash() == block_hash:
                return block
        raise ValueError(BLOCK_HASH_ERROR)
=======
        raise NotImplementedError()
>>>>>>> 9d7dcba9d7f7c8bf518f932470a08ea5fb0c2e99

    def get_latest_hash(self) -> BlockHash:
        """
        This function returns the last block hash known to this node (the tip of its current chain).
        """
<<<<<<< HEAD
        try:
            return self.__blockchain[-1].get_block_hash()
        except:
            raise ValueError(LATEST_HASH_ERROR)
=======
        raise NotImplementedError()
>>>>>>> 9d7dcba9d7f7c8bf518f932470a08ea5fb0c2e99

    def get_mempool(self) -> List[Transaction]:
        """
        This function returns the list of transactions that didn't enter any block yet.
        """
<<<<<<< HEAD
        return list(self.__mempool.keys())
=======
        raise NotImplementedError()
>>>>>>> 9d7dcba9d7f7c8bf518f932470a08ea5fb0c2e99

    def get_utxo(self) -> List[Transaction]:
        """
        This function returns the list of unspent transactions.
        """
<<<<<<< HEAD
        return self.__utxo
=======
        raise NotImplementedError()
>>>>>>> 9d7dcba9d7f7c8bf518f932470a08ea5fb0c2e99

    # ------------ Formerly wallet methods: -----------------------

    def create_transaction(self, target: PublicKey) -> Optional[Transaction]:
        """
        This function returns a signed transaction that moves an unspent coin to the target.
        It chooses the coin based on the unspent coins that this node has.
        If the node already tried to spend a specific coin, and such a transaction exists in its mempool,
        but it did not yet get into the blockchain then it should'nt try to spend it again (until clear_mempool() is
        called -- which will wipe the mempool and thus allow to attempt these re-spends).
        The method returns None if there are no outputs that have not been spent already.

        The transaction is added to the mempool (and as a result is also published to neighboring nodes)
        """
<<<<<<< HEAD
        available_tx = None
        for tx in self.__utxo:
            if tx not in self.__mempool:
                available_tx = tx
        if not available_tx: return None
        
        txid = available_tx.get_txid()
        signature = sign(target + txid,  self.__private_key)
        tx = Transaction(output=target, input=txid, signature=signature)
        # TODO: delete tx from self.__utxo?
        self.__mempool.append(tx)
        for neighbor in self.__connections:
            neighbor.add_transaction_to_mempool(tx)

        return tx
=======
        raise NotImplementedError()
>>>>>>> 9d7dcba9d7f7c8bf518f932470a08ea5fb0c2e99

    def clear_mempool(self) -> None:
        """
        Clears the mempool of this node. All transactions waiting to be entered into the next block are gone.
        """
<<<<<<< HEAD
        self.__mempool = []
=======
        raise NotImplementedError()
>>>>>>> 9d7dcba9d7f7c8bf518f932470a08ea5fb0c2e99

    def get_balance(self) -> int:
        """
        This function returns the number of coins that this node owns according to its view of the blockchain.
        Coins that the node owned and sent away will still be considered as part of the balance until the spending
        transaction is in the blockchain.
        """
<<<<<<< HEAD
        return self.__balance
=======
        raise NotImplementedError()
>>>>>>> 9d7dcba9d7f7c8bf518f932470a08ea5fb0c2e99

    def get_address(self) -> PublicKey:
        """
        This function returns the public address of this node (its public key).
        """
<<<<<<< HEAD
        return self.__public_key

    # ------------ Privet methods: -----------------------

    def __one_directional_connect(self,  other: 'Node') -> None:

        pass
=======
        raise NotImplementedError()
>>>>>>> 9d7dcba9d7f7c8bf518f932470a08ea5fb0c2e99


"""
Importing this file should NOT execute code. It should only create definitions for the objects above.
Write any tests you have in a different file.
You may add additional methods, classes and files but be sure no to change the signatures of methods
included in this template.
"""
