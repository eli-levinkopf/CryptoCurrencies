from ex1 import *


def test_block(bank: Bank, alice_coin: Transaction) -> None:
    hash1 = bank.get_latest_hash()
    block = bank.get_block(hash1)
    assert len(block.get_transactions()) == 1
    assert block.get_prev_block_hash() == GENESIS_BLOCK_PREV

    bank.end_day()

    hash2 = bank.get_latest_hash()
    block2 = bank.get_block(hash2)
    assert len(block2.get_transactions()) == 0
    assert block2.get_prev_block_hash() == hash1


def test_create_money_happy_flow(bank: Bank, alice: Wallet, bob: Wallet,
                                 alice_coin: Transaction) -> None:
    alice.update(bank)
    bob.update(bank)
    assert alice.get_balance() == 1
    assert bob.get_balance() == 0
    utxo = bank.get_utxo()
    assert len(utxo) == 1
    assert utxo[0].output == alice.get_address()


def test_transaction_happy_flow(bank: Bank, alice: Wallet, bob: Wallet,
                                alice_coin: Transaction) -> None:
    tx = alice.create_transaction(bob.get_address())
    assert tx is not None
    assert bank.add_transaction_to_mempool(tx)
    assert bank.get_mempool() == [tx]
    bank.end_day(limit=1)
    alice.update(bank)
    bob.update(bank)
    assert alice.get_balance() == 0
    assert bob.get_balance() == 1
    assert not bank.get_mempool()
    assert bank.get_utxo()[0].output == bob.get_address()
    assert tx == bank.get_block(bank.get_latest_hash()).get_transactions()[0]


def test_re_transmit_the_same_transaction(bank: Bank, alice: Wallet,
                                          bob: Wallet,
                                          alice_coin: Transaction) -> None:
    tx = alice.create_transaction(bob.get_address())
    assert tx is not None
    assert bank.add_transaction_to_mempool(tx)
    assert not bank.add_transaction_to_mempool(tx)
    assert bank.get_mempool() == [tx]


def test_spend_coin_not_mine(bank2: Bank, alice: Wallet, bob: Wallet,
                             alice_coin: Transaction) -> None:
    tx = alice.create_transaction(bob.get_address())
    assert tx is not None
    assert not bank2.add_transaction_to_mempool(tx)
    assert not bank2.get_mempool()


def test_change_output_of_signed_transaction(bank: Bank, alice: Wallet,
                                             bob: Wallet, charlie: Wallet,
                                             alice_coin: Transaction) -> None:
    tx = alice.create_transaction(bob.get_address())
    assert tx is not None
    tx = Transaction(output=charlie.get_address(),
                     input=tx.input, signature=tx.signature)
    assert not bank.add_transaction_to_mempool(tx)
    assert not bank.get_mempool()
    bank.end_day()
    alice.update(bank)
    bob.update(bank)
    assert alice.get_balance() == 1
    assert bob.get_balance() == 0
    assert charlie.get_balance() == 0


def test_change_coin_of_signed_transaction(bank: Bank, alice: Wallet,
                                           bob: Wallet, charlie: Wallet,
                                           alice_coin: Transaction) -> None:
    # Give Bob two coins
    tx = alice.create_transaction(bob.get_address())
    assert tx is not None
    bank.add_transaction_to_mempool(tx)
    bank.create_money(bob.get_address())
    bank.end_day()
    alice.update(bank)
    bob.update(bank)
    charlie.update(bank)
    bob_coin1, bob_coin2 = bank.get_utxo()
    # Bob gives a coin to Charlie, and Charlie wants to steal the second one
    tx = bob.create_transaction(charlie.get_address())
    assert tx is not None
    tx2 = Transaction(output=tx.output,
                      input=bob_coin2.get_txid() if tx.input == bob_coin1.get_txid()
                      else bob_coin1.get_txid(), signature=tx.signature)
    assert not bank.add_transaction_to_mempool(tx2)
    assert not bank.get_mempool()
    assert bank.add_transaction_to_mempool(tx)
    assert bank.get_mempool()
    bank.end_day()
    alice.update(bank)
    bob.update(bank)
    charlie.update(bank)
    assert alice.get_balance() == 0
    assert bob.get_balance() == 1
    assert charlie.get_balance() == 1


def test_double_spend_fail(bank: Bank, alice: Wallet, bob: Wallet,
                           charlie: Wallet, alice_coin: Transaction) -> None:
    tx1 = alice.create_transaction(bob.get_address())
    assert tx1 is not None
    # make alice spend the same coin
    alice.update(bank)
    alice.unfreeze_all()
    tx2 = alice.create_transaction(charlie.get_address())
    assert tx2 is not None  # Alice will try to double spend

    assert bank.add_transaction_to_mempool(tx1)
    assert not bank.add_transaction_to_mempool(tx2)
    bank.end_day(limit=2)
    alice.update(bank)
    bob.update(bank)
    charlie.update(bank)
    assert alice.get_balance() == 0
    assert bob.get_balance() == 1
    assert charlie.get_balance() == 0


def test_unfreeze_all(bank: Bank, alice: Wallet, bob: Wallet, charlie: Wallet,
                      alice_coin: Transaction) -> None:
    assert alice.create_transaction(charlie.get_address())
    assert not alice.create_transaction(bob.get_address())
    alice.unfreeze_all()
    assert alice.create_transaction(bob.get_address())


def test_no_money(bank: Bank, alice: Wallet, bob: Wallet, charlie: Wallet,
                  alice_coin: Transaction) -> None:
    tx = Transaction(charlie.get_address(), alice_coin.get_txid(),
                     alice_coin.signature)
    assert not bank.add_transaction_to_mempool(tx)


def test_over_limit(bank: Bank, alice: Wallet, bob: Wallet, charlie: Wallet,
                    alice_coin: Transaction, alice_coin2: Transaction) -> None:
    tx_1 = alice.create_transaction(bob.get_address())
    tx_2 = alice.create_transaction(charlie.get_address())
    assert bank.add_transaction_to_mempool(tx_1)
    assert bank.add_transaction_to_mempool(tx_2)
    bank.end_day(limit=1)
    alice.update(bank)
    bob.update(bank)
    charlie.update(bank)
    assert alice.get_balance() == 1
    assert bob.get_balance() == 1
    assert charlie.get_balance() == 0

def test_empty_block(bank: Bank) -> None:
    assert len(bank.get_utxo()) == 0
    assert len(bank.get_mempool()) == 0
    bank.end_day()
    assert len(bank.get_utxo()) == 0
    assert len(bank.get_mempool()) == 0
    b: Block = bank.get_block(bank.get_latest_hash())
    assert len(b.get_transactions()) == 0


def test_update_utxo(bank: Bank, alice: Wallet) -> None:
    assert len(bank.get_utxo()) == 0
    assert len(bank.get_mempool()) == 0
    bank.create_money(alice.get_address())
    assert len(bank.get_utxo()) == 0
    assert len(bank.get_mempool()) == 1
    bank.end_day()
    assert len(bank.get_utxo()) == 1
    assert len(bank.get_mempool()) == 0


def test_block_size(bank: Bank, alice: Wallet, bob: Wallet, charlie: Wallet, alice_coin: Transaction) -> None:
    bank.create_money(alice.get_address())
    bank.end_day()

    alice.update(bank)
    bob.update(bank)
    charlie.update(bank)
    assert alice.get_balance() == 2
    assert bob.get_balance() == 0
    assert charlie.get_balance() == 0

    tx1: Transaction = alice.create_transaction(bob.get_address())
    tx2: Transaction = alice.create_transaction(charlie.get_address())

    assert tx1 is not None
    assert tx2 is not None

    assert len(bank.get_mempool()) == 0
    assert len(bank.get_utxo()) == 2

    bank.add_transaction_to_mempool(tx1)
    bank.add_transaction_to_mempool(tx2)

    assert len(bank.get_mempool()) == 2
    assert len(bank.get_utxo()) == 2

    bank.end_day(limit=1)

    assert len(bank.get_mempool()) == 1
    assert len(bank.get_utxo()) == 2
    b: Block = bank.get_block(bank.get_latest_hash())
    assert len(b.get_transactions()) == 1

    alice.update(bank)
    bob.update(bank)
    charlie.update(bank)
    assert alice.get_balance() == 1
    assert bob.get_balance() + charlie.get_balance() == 1
    assert max(bob.get_balance(), charlie.get_balance()) == 1
    assert min(bob.get_balance(), charlie.get_balance()) == 0

    bank.end_day(limit=1)

    assert len(bank.get_mempool()) == 0
    assert len(bank.get_utxo()) == 2
    b: Block = bank.get_block(bank.get_latest_hash())
    assert len(b.get_transactions()) == 1

    alice.update(bank)
    bob.update(bank)
    charlie.update(bank)
    assert alice.get_balance() == 0
    assert bob.get_balance() == 1
    assert charlie.get_balance() == 1


def test_unfreeze_transactions_and_balance(bank: Bank, alice: Wallet, bob: Wallet, charlie: Wallet, alice_coin: Transaction) -> None:
    alice.update(bank)
    bob.update(bank)
    charlie.update(bank)
    assert alice.get_balance() == 1
    assert bob.get_balance() == 0
    assert charlie.get_balance() == 0

    tx1: Transaction = alice.create_transaction(bob.get_address())
    assert tx1 is not None
    assert alice.get_balance() == 1

    tx2: Transaction = alice.create_transaction(charlie.get_address())
    assert tx2 is None
    assert alice.get_balance() == 1

    alice.unfreeze_all()
    tx3: Transaction = alice.create_transaction(charlie.get_address())
    assert tx3 is not None
    assert alice.get_balance() == 1
