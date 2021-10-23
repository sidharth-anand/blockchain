import hashlib
import json
import typing

from time import time

from blockchain.constants import GENESIS_BLOCK_INDEX, OWNER_ADDRESS, OWNER_INIT_AMOUNT
from blockchain.transaction import Transaction, TransactionIn, TransactionOut, TransactionTypes

class Block(dict):
    def __init__(self, index: int, previous_hash: str, difficulty: int, minter_balance: float, minter_address: str, transactions: typing.List[Transaction] = []) -> None:
        self.index = index

        self.timestamp = time()
        self.previous_hash = previous_hash

        self.difficulty = difficulty

        self.minter_balance = minter_balance
        self.minter_address = minter_address

        self.transactions = transactions

        dict.__init__(self, index=self.index, timestamp=self.timestamp, previous_hash=self.previous_hash, difficulty=self.difficulty, transactions=self.transactions)

    def hash(self):
        return hashlib.sha256(json.dumps(self, sort_keys=True).encode()).hexdigest()

    @staticmethod
    def genesis():
        transaction_in = TransactionIn('', GENESIS_BLOCK_INDEX, '')
        transaction_out = TransactionOut(OWNER_ADDRESS, OWNER_INIT_AMOUNT)
        transaction = Transaction([transaction_in], [transaction_out], TransactionTypes.COINBASE)

        return Block(GENESIS_BLOCK_INDEX, '', 0, 0, OWNER_ADDRESS, [transaction])

    @staticmethod
    def from_dict(block_data: dict):
        block = Block(block_data['index'], block_data['previous_hash'], block_data['difficulty'], block_data['minter_balance'], block_data['minter_address'])
        block.timestamp = block_data['timestamp']

        for transaction in block_data['transactions']:
            block.transactions.append(Transaction.from_dict(transaction))
        
        return block