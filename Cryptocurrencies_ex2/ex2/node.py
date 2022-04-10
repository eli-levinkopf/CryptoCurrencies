from re import U
from .utils import *
from .block import Block
from .transaction import Transaction
from typing import Dict, Set, Optional, List
import secrets


CONECTION_ERROR = "node can't connect to itself"
BLOCK_HASH_ERROR = "block hash does not exist in blockchain"
LATEST_HASH_ERROR = "The blockchain does not contain any blocks"


class Node:
    def __init__(self) -> None:
        """Creates a new node with an empty mempool and no connections to others.
        Blocks mined by this node will reward the miner with a single new coin,
        created out of thin air and associated with the mining reward address"""
        # {Tx: True iff node.public_key is the output of Tx}
        self.__private_key,  self.__public_key = gen_keys()
        self.__mempool: List[Transaction] = []
        self.__blockchain: List[Block] = []
        self.__utxo: List[Transaction] = []
        self.__my_utxo: Dict[Transaction, bool] = {}
        self.__connections: Set['Node'] = []
        self.__blocks_hash: List[BlockHash] = []
        self.__transactions_history: List[Transaction] = []
        self.__balance: int = 0

    def connect(self, other: 'Node') -> None:
        """connects this node to another node for block and transaction updates.
        Connections are bi-directional, so the other node is connected to this one as well.
        Raises an exception if asked to connect to itself.
        The connection itself does not trigger updates about the mempool,
        but nodes instantly notify of their latest block to each other (see notify_of_block)"""
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

    def add_transaction_to_mempool(self, transaction: Transaction) -> bool:
        """
        This function inserts the given transaction to the mempool.
        It will return False iff any of the following conditions hold:
        (i) the transaction is invalid (the signature fails)
        (ii) the source doesn't have the coin that it tries to spend
        (iii) there is contradicting tx in the mempool.

        If the transaction is added successfully, then it is also sent to neighboring nodes.
        """
        # TDDT: sender
        sender = None 
        for tx in self.__utxo:
            if tx.get_txid() == transaction.get_input():
                sender= tx
        if not sender: return False

        if not verify(transaction.get_message(), transaction.get_signature(), sender.get_output()):
            return False

        # if not transaction.get_input(): return False

        for tx in self.__mempool:
            if tx.get_input == transaction.get_input(): return False
        
        for neighbor in self.__connections:
            neighbor.add_transaction_to_mempool(transaction)
        return True
        

    def notify_of_block(self, block_hash: BlockHash, sender: 'Node') -> None:
        """This method is used by a node's connection to inform it that it has learned of a
        new block (or created a new block). If the block is unknown to the current Node, The block is requested.
        We assume the sender of the message is specified, so that the node can choose to request this block if
        it wishes to do so.
        (if it is part of a longer unknown chain, these blocks are requested as well, until reaching a known block).

        Upon receiving new blocks, they are processed and checked for validity (check all signatures, hashes,
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
        curr_block_hash = self.get_latest_hash()
        known = False
        new_blockchain = []
            
        # check if we known the given block
        while curr_block_hash != block_hash and curr_block_hash != GENESIS_BLOCK_PREV:
            curr_block_hash = self.get_block(curr_block_hash).get_prev_block_hash()

        while block_hash != GENESIS_BLOCK_PREV and not known:
            # the block is unknown to the current Node
            if not known:
                unknown_block = sender.get_block(block_hash) # The unknown block is requested
                if self.__verify_block(unknown_block, sender): # check if the block is valid
                    new_blockchain.insert(0, unknown_block) # save the new block
                curr_block_hash = self.get_latest_hash() # B 
                block_hash = unknown_block.get_prev_block_hash() # Hash of the previous block of the unknown block (new block)
                # check if we known the previous block of the new (unknown) block
                while curr_block_hash != block_hash and curr_block_hash != GENESIS_BLOCK_PREV:
                    curr_block_hash = self.get_block(curr_block_hash).get_prev_block_hash()

            if curr_block_hash != GENESIS_BLOCK_PREV:
                known = True
                known_block_idx = self.__blockchain.index(unknown_block)
        

        if not known:  # All the blocks in the blockchain of block_hash are unknown for current node
            if len(self.__blockchain) < len(new_blockchain):
                self.__blockchain = new_blockchain
                

                for block in self.__blockchain:
                    for tx in block.get_transactions():
                        self.__utxo.append(tx)
                # self.__mempool = sender.get_mempool()

                
                self.__notify_of_block_to_connections(block_hash)
                
        # There is a block that the current node knows. and the knows block is chained to a longer chain
        elif len(self.__blockchain[known_block_idx:]) < len(new_blockchain): 
            self.__blockchain += new_blockchain
            self.__notify_of_block_to_connections(block_hash)
            
    def set_utxo(self, utxo: List[Transaction]) -> None:
        self.__utxo = utxo

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
        signature=Signature(secrets.token_bytes(48))
        miner_transaction = Transaction(output=self.__public_key, tx_input=None, signature=signature)
        self.__my_utxo[miner_transaction] = True
        self.__utxo.append(miner_transaction)
        self.__balance+=1
        if (len(self.__mempool) >= BLOCK_SIZE - 1):
            transactions = self.__mempool[:BLOCK_SIZE - 1] + [miner_transaction]      
        else: 
            transactions = self.__mempool + [miner_transaction]      
        new_block = Block(prev_block_hash = GENESIS_BLOCK_PREV, transactions=transactions)
        self.__blockchain.insert(0, new_block)
        self.__transactions_history += transactions
        block_hash = new_block.get_block_hash()
        for neighbor in self.__connections:
            neighbor.notify_of_block(block_hash=block_hash, sender=self)
        return new_block.get_block_hash()


    def get_block(self, block_hash: BlockHash) -> Block:
        """
        This function returns a block object given its hash.
        If the block doesnt exist, a ValueError is raised.
        """
        for block in self.__blockchain:
            if block.get_block_hash() == block_hash:
                return block
        raise ValueError(BLOCK_HASH_ERROR)

    def get_latest_hash(self) -> BlockHash:
        """
        This function returns the last block hash known to this node (the tip of its current chain).
        """
        try:
            return self.__blockchain[-1].get_block_hash()
        except:
            return GENESIS_BLOCK_PREV

    def get_mempool(self) -> List[Transaction]:
        """
        This function returns the list of transactions that didn't enter any block yet.
        """
        # TODO:
        return list(self.__mempool)

    def get_utxo(self) -> List[Transaction]:
        """
        This function returns the list of unspent transactions.
        """
        return self.__utxo

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
        available_tx = None
        for tx in self.__my_utxo.keys():
            if self.__my_utxo[tx]:
                available_tx = tx
                self.__my_utxo[available_tx] = False
        if not available_tx: return None

        txid = available_tx.get_txid()
        signature = sign(target + txid,  self.__private_key)
        tx = Transaction(output=target, tx_input=txid, signature=signature)
        self.__mempool.append(tx)
        for neighbor in self.__connections:
            neighbor.add_transaction_to_mempool(tx)

        return tx

    def clear_mempool(self) -> None:
        """
        Clears the mempool of this node. All transactions waiting to be entered into the next block are gone.
        """

        self.__mempool = []

    def get_balance(self) -> int:
        """
        This function returns the number of coins that this node owns according to its view of the blockchain.
        Coins that the node owned and sent away will still be considered as part of the balance until the spending
        transaction is in the blockchain.
        """
        return self.__balance

    def get_address(self) -> PublicKey:
        """
        This function returns the public address of this node (its public key).
        """
        return self.__public_key

    # TODO: replace with blockchain
    def transactions_history(self) -> List[Transaction]:
        return self.__transactions_history

    def get_blockchain(self) -> List[Block]:
        return self.__blockchain

    # ------------ Privet methods: ------------------------

    def __verify_block(self, block: Block, sender: 'Node') -> bool:
        """
        Upon receiving new blocks, they are processed and checked for validity (check all signatures, hashes,
        block size , etc).
        """
        block_transactions = block.get_transactions()
        miner_award = sum([1 for tx in block_transactions if not tx.get_input()])
        if len(block_transactions) > BLOCK_SIZE or miner_award != 1:
            return False
        
        for transaction in block_transactions:
            for tx in self.transactions_history(): # check if transaction make double spend
                if tx.get_input() == transaction.get_input():
                    return False
            input_tx = None
            # for tx in sender.transactions_history(): # find the the sender of this transaction
            #     if tx.get_txid() == transaction.get_input():
            #         input_tx = tx 
            # if not input_tx and not transaction.get_input(): # minner tx case
            #     continue
            # # verify the signature
            # if not input_tx or not verify(transaction.get_message, transaction.get_signature, input_tx.get_output()):
            #     return False
        return True


    def __notify_of_block_to_connections(self, block_hash: BlockHash) -> None:
        # sent a notification of this block to the neighboring nodes of this node
        for neighbor in self.__connections: 
            neighbor.notify_of_block(block_hash)

    def __one_directional_connect(self,  other: 'Node') -> None:

        pass


"""
Importing this file should NOT execute code. It should only create definitions for the objects above.
Write any tests you have in a different file.
You may add additional methods, classes and files but be sure no to change the signatures of methods
included in this template.
"""
