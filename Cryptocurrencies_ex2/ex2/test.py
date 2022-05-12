import sys
from traceback import print_tb
sys.path.append('/Users/elilevinkopf/Documents/Ex22B/Cryptocurrencies/Cryptocurrencies_ex2')
from utils import *
from ex2 import *
import secrets
from unittest.mock import Mock
from typing import Callable, List
from ex2 import Node, Block, BlockHash
import hashlib


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

def f2(l:List[int]):
    l.append(len(l)+1)
    l.remove(4)
    return l

def f1():
    l = [1, 2, 3, 4, 5]
    f2(l)
    print(l)


if __name__ == '__main__':
    # block = Block()
    alice = Node()
    bob = Node()
    charlie = Node()
    

    # block1 = Block(BlockHash(hashlib.sha256(b"Not Genesis").digest()),
    #                [Transaction(gen_keys()[1], None, Signature(secrets.token_bytes(64)))])
    # block2 = Block(block1.get_block_hash(), [Transaction(
    #     gen_keys()[1], None, Signature(secrets.token_bytes(64)))])
    # block3 = Block(block2.get_block_hash(), [Transaction(
    #     gen_keys()[1], None, Signature(secrets.token_bytes(64)))])

    # evil_node = evil_node_maker([block1, block2, block3])

    # alice.notify_of_block(block3.get_block_hash(), evil_node)
