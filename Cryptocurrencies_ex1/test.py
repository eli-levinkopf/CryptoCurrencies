import hashlib
from traceback import print_tb
from ex1.utils import *

from ex1 import *
import secrets
def create_transaction() -> Transaction:
    input, output = gen_keys()
    # message: bytes = secrets.token_bytes(64)
    message = output + input
    signature: Signature = sign(message, input)
    Tx = Transaction(output, input, signature)
    return Tx

# Tx = create_transaction()
# print(Tx.get_txid())



# transactions = [create_transaction() for i in range(3)]
# first_block = Block(transactions)
# print(first_block.get_transactions())
# print(f'first_block: {first_block.get_block_hash()}')
# prev_block_hash = 'b7d2ffa9cb0a6192dc154e33cc1d07cf01ee03cbc9494f1449b54e208fe16490'
# some_block = Block(transactions, prev_block_hash)
# print(f'some_block: {some_block.get_block_hash()}')

# bank = Bank()

# PrivateKey1, PublicKey1 = gen_keys()
# PrivateKey2, PublicKey2 = gen_keys()
# message1 = PublicKey2
# signature1: Signature = sign(message1, PrivateKey1)

# bank.create_money(PublicKey1)
# bank.create_money(PublicKey1)
# Tx1 = Transaction(output=PublicKey2, input=None, signature=signature1)
# print(bank.add_transaction_to_mempool(Tx1))

# (bank.end_day())
# print(bank.get_mempool())
# print(bank.get_utxo())

# target = gen_keys()[1]
# bank.create_money(target)
# (bank.add_transaction_to_mempool(Tx))
# (bank.add_transaction_to_mempool(Tx1))
# (bank.end_day())
# print(bank.get_blockchain())
# print(bank.get_latest_hash())
# print(bank.get_mempool())
# print(bank.get_utxo())
# print(bank.get_inputs())
# print(bank.get_block(bank.get_blockchain()[0].get_block_hash()))
# print(bank.get_block(bank.get_blockchain()[0].get_block_hash() + 'f'))


bank = Bank()
alice = Wallet()
bob = Wallet()
charlie = Wallet()


# alice_coin
# bank.create_money(alice.get_address())
# bank.end_day()
# alice.update(bank)



# print(bank.get_mempool())
# print(alice.get_balance())
# print(alice.get_txid())


bank.create_money(alice.get_address())
bank.create_money(alice.get_address())
bank.end_day()
alice.update(bank)
assert alice.get_balance() == 2

tx1 = alice.create_transaction(bob.get_address())
bank.add_transaction_to_mempool(tx1)
bank.end_day()
alice.unfreeze_all()
assert alice.get_balance() == 2

tx2 = alice.create_transaction(bob.get_address())
assert tx2 is not None
tx3 = alice.create_transaction(bob.get_address())
assert tx3 is not None
assert bank.add_transaction_to_mempool(tx2)
assert not bank.add_transaction_to_mempool(tx3)

bank.end_day()
# print(bank.get_blockchain()[0].get_prev_block_hash())
alice.update(bank)
# print(bank.get_blockchain()[0].get_transactions())
assert not alice.get_balance()