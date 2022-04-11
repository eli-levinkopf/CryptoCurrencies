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
        self.__tmp_utxo: List[Transaction] = []
        self.__my_utxo: Dict[TxID, bool] = {}
        self.__connections: Set['Node'] = set()
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
        other.notify_of_block(self.get_latest_hash(), self)
        other.__connections.add(self)
        self.notify_of_block(other.get_latest_hash(), other)


    def disconnect_from(self, other: 'Node') -> None:
        """Disconnects this node from the other node. If the two were not connected, then nothing happens"""
        if other in self.__connections:
            self.__connections.remove(other)
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

        for tx in self.__mempool:
            if tx.get_input() == transaction.get_input(): return False

        if transaction in self.__mempool: return False

        for tx in self.__mempool:
            if tx.get_input == transaction.get_input(): return False
        
        self.__mempool.append(transaction)
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
        new_blockchain: List[Block]= []
        new_hashes: List[BlockHash]= []
            
        # check if we known the given block
        while curr_block_hash != block_hash and curr_block_hash != GENESIS_BLOCK_PREV:
            curr_block_hash = self.get_block(curr_block_hash).get_prev_block_hash()

        while block_hash != GENESIS_BLOCK_PREV and not known:
            # the block is unknown to the current Node
            if not known: 
                try:
                    unknown_block = sender.get_block(block_hash) # The unknown block is requested
                except: return
                new_blockchain.insert(0, unknown_block) # save the new block
                new_hashes.insert(0, block_hash) # save the new block hash
                curr_block_hash = self.get_latest_hash()
                block_hash = unknown_block.get_prev_block_hash() # Hash of the previous block of the unknown block (new block)
                # check if we known the previous block of the new (unknown) block
                while curr_block_hash != block_hash and curr_block_hash != GENESIS_BLOCK_PREV:
                    curr_block_hash = self.get_block(curr_block_hash).get_prev_block_hash()

            if curr_block_hash != GENESIS_BLOCK_PREV: # get to a known block (known for current node)
                known = True
                known_block_idx = self.__blockchain.index(self.get_block(curr_block_hash))
        
        if not known:  # All the blocks in the blockchain of block_hash are unknown for current node
            if len(self.__blockchain) < len(new_blockchain):
                if self.__verify_blockchain_and_update_utxo(new_blockchain, new_hashes): # verify and update utxo
                    self.__blockchain = list(reversed(new_blockchain)) # replace blockchain
                    self.__notify_of_block_to_connections(block_hash, sender) # updae all connections
                
        # There is a block that the current node knows, and the knows block is chained to a longer chain
        elif len(self.__blockchain[known_block_idx + 1:]) < len(new_blockchain):
            # verify blocks
            if self.__verify_blockchain_for_split(new_blockchain, new_hashes, known_block_idx):
                self.__update_utxo(new_blockchain, known_block_idx) # update utxo
                self.__update_mempool(new_blockchain) # update mempool
                self.__blockchain += new_blockchain # update blockchain
                self.__blockchain = list(reversed(self.__blockchain))
                self.__notify_of_block_to_connections(block_hash, sender) # updae all connections


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
        self.__my_utxo[miner_transaction.get_txid()] = True
        self.__utxo.append(miner_transaction)
        self.__balance+=1
        if len(self.__mempool) >= BLOCK_SIZE - 1:
            transactions = self.__mempool[:BLOCK_SIZE - 1] + [miner_transaction]      
        else: 
            transactions = self.__mempool + [miner_transaction]  
        hash_block = self.get_latest_hash()    
        new_block = Block(prev_block_hash = hash_block, transactions=transactions)
        self.__blockchain.insert(0, new_block)
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
            return self.__blockchain[0].get_block_hash()
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
        available_txid = None
        for txid in self.__my_utxo.keys():
            if self.__my_utxo[txid]:
                available_txid = txid
                self.__my_utxo[available_txid] = False
        if not available_txid: return None

        # txid = available_txid.get_txid()
        signature = sign(target + available_txid,  self.__private_key)
        tx = Transaction(output=target, tx_input=txid, signature=signature)
        self.__mempool.append(tx)
        self.__utxo.append(tx)
        for neighbor in self.__connections:
            neighbor.add_transaction_to_mempool(tx)

        return tx

    def clear_mempool(self) -> None:
        """
        Clears the mempool of this node. All transactions waiting to be entered into the next block are gone.
        """
        for tx in self.__mempool:
            txid = tx.get_input()
            if txid in self.__my_utxo.keys():
                self.__my_utxo[txid] = True
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


    def get_blockchain(self) -> List[Block]:
        return self.__blockchain

    # ------------ Privet methods: ------------------------

    def __verify_blockchain_and_update_utxo(self, new_blockchain: List[Block], new_hashes: List[BlockHash]) -> bool:
        tmp_utxo: List[Transaction] = self.__initialize_tmp_utxo(new_blockchain)
        inx = len(new_blockchain)
        for block in new_blockchain:
            if not self.__verify_block(block, new_hashes[new_blockchain.index(block)]):
                inx = new_blockchain.index(block) # index of the first invalid block
                break
            # check validity of tx
            for tx in block.get_transactions(): 
                if not tx.get_input(): continue # minner transaction case
                tx_sender = self.__get_tx_sender(tx, tmp_utxo) # get the sender of this transaction
                if not tx_sender or not verify(tx.get_message(), tx.get_signature(), tx_sender.get_output()): # verify the signature
                    inx = new_blockchain.index(block) # index of the first invalid block
                    break

        if len(self.__blockchain) >= len(new_blockchain[:inx]): return False
        for block in new_blockchain[inx:]:
            new_blockchain.remove(block) # remove invalid blocks
        # TODO: 
        self.__utxo = tmp_utxo
        return True

    
    def __verify_blockchain_for_split(self, new_blockchain: List[Block], new_hashes: List[BlockHash], known_block_idx: int) -> bool:
        tmp_utxo: List[Transaction] = self.__initialize_tmp_utxo(new_blockchain)
        inx = len(new_blockchain)
        for block in new_blockchain:
            if not self.__verify_block(block, new_hashes[new_blockchain.index(block)]):
                inx = len(new_blockchain)
                break

            for tx in block.get_transactions():
                if not tx.get_input(): continue
                tx_sender = self.__get_tx_sender(tx, tmp_utxo)
                if not tx_sender or not verify(tx.get_message(), tx.get_signature(), tx.get_output()):
                    inx = len(new_blockchain)
                    break
                    
        if len(self.__blockchain[known_block_idx + 1:]) >= len(new_blockchain): return False
        for block in new_blockchain[inx:]:
            new_blockchain.remove(block)
        # self.__tmp_utxo = tmp_utxo
        return True


    def __verify_block(self, block: Block, hash :BlockHash) -> bool:
        block_transactions = block.get_transactions()
        miner_award = sum(1 for tx in block_transactions if not tx.get_input()) # miner_award per block most to be 1
        if block.get_block_hash() != hash or len(block_transactions) > BLOCK_SIZE or miner_award != 1:
             return False
        return True


    def __get_tx_sender(self, transaction: Transaction, utxo: List[Transaction]) -> Optional[Transaction]: 
        for tx in utxo:
            if transaction.get_input() == tx.get_txid():
                utxo.remove(tx)
                return tx
        return False

    def __initialize_tmp_utxo(self, new_blockchain: List[Block]) -> List[Transaction]:
        return [tx for block in new_blockchain for tx in block.get_transactions()]

    def __update_utxo(self, new_blockchain: List[Block], known_block_idx: int) -> None:
        tmp_utxo: List[Transaction] = self.__initialize_tmp_utxo(new_blockchain)
        # remove from utxo all transactions that are in the shortest subchain (blockchain[known_block_idx + 1:]) ?
        for block in self.__blockchain[known_block_idx + 1:]:
            for tx in block.get_transactions():
                if tx.get_input() in self.__my_utxo: # current block is the input of tx
                    self.__my_utxo[tx.get_input()] = True
                    # TODO: balance++
                elif tx in self.__utxo:
                    self.__utxo.remove(tx)
                    
        self.__utxo += tmp_utxo

    def __update_mempool(self, new_blockchain: List[Block]) -> None:
        for block in new_blockchain:
            for tx in block.get_transactions():
                if tx in self.__mempool:
                    self.__mempool.remove(tx)

 

    def __notify_of_block_to_connections(self, block_hash: BlockHash, sender: 'Node') -> None:
        # sent a notification of this block to the neighboring nodes of this node
        for neighbor in self.__connections: 
            neighbor.notify_of_block(block_hash, self)



"""
Importing this file should NOT execute code. It should only create definitions for the objects above.
Write any tests you have in a different file.
You may add additional methods, classes and files but be sure no to change the signatures of methods
included in this template.
"""
