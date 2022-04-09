import sys
sys.path.append('/Users/elilevinkopf/Documents/Ex22B/Cryptocurrencies/Cryptocurrencies_ex1')
from utils import *
from ex1 import Transaction, Wallet, Bank, Block

if __name__ == '__main__':
    block = Block()
    print(block.get_prev_block_hash())