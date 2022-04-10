import sys
from traceback import print_tb
sys.path.append('/Users/elilevinkopf/Documents/Ex22B/Cryptocurrencies/Cryptocurrencies_ex2')
from utils import *
from ex2 import *
import secrets
from unittest.mock import Mock
from typing import Callable, List
from ex2 import Node, Block, BlockHash

EvilNodeMaker = Callable[[List[Block]], Mock]
KeyFactory = Callable[[], PublicKey]

# def evil_node_maker(chain: List[Block]) -> Callable[[List[Block]], Mock]:
#     def factory(chain: List[Block]) -> Mock:
#         evil_node = Mock()
#         block_dict = {block.get_block_hash(): block for block in chain}
#         evil_node.get_latest_hash.return_value = chain[-1].get_block_hash()

#         def my_get_block(block_hash: BlockHash) -> Block:
#             if block_hash in block_dict:
#                 return block_dict[block_hash]
#             raise ValueError

#         evil_node.get_block.side_effect = my_get_block

#         return evil_node

#     return factory

def evil_node_maker(chain: List[Block]) -> Mock:
    evil_node = Mock()
    block_dict = {block.get_block_hash(): block for block in chain}
    evil_node.get_latest_hash.return_value = chain[-1].get_block_hash()

    def my_get_block(block_hash: BlockHash) -> Block:
        if block_hash in block_dict:
            return block_dict[block_hash]
        raise ValueError

    evil_node.get_block.side_effect = my_get_block

    return evil_node

if __name__ == '__main__':
    block = Block()
    alice = Node()
    bob = Node()
    
    tx1 = Transaction(gen_keys()[1], None, Signature(secrets.token_bytes(64)))
    block1 = Block(GENESIS_BLOCK_PREV, [tx1])
    tx2 = Transaction(gen_keys()[1], None, Signature(secrets.token_bytes(64)))
    block2 = Block(block1.get_block_hash(), [tx2])

    block_chain = [block1, block2]
    eve = evil_node_maker(block_chain)
    alice.notify_of_block(eve.get_latest_hash(), eve)
    assert alice.get_latest_hash() == block2.get_block_hash()
    alice.set_utxo([tx1])
    assert tx1 in alice.get_utxo()
