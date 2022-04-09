import sys
sys.path.append('/Users/elilevinkopf/Documents/Ex22B/Cryptocurrencies/Cryptocurrencies_ex2')
from utils import *
from ex2 import Transaction, Block

if __name__ == '__main__':
    block = Block()
    print(block.get_prev_block_hash())