import hashlib
import json
import typing

from time import time

from blockchain.constants import GENESIS_BLOCK_INDEX, OWNER_ADDRESS, OWNER_INIT_AMOUNT, CHAIN_ADDRESS, OWNER_INIT_STAKE, VALIDATOR_AMOUNT
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

        dict.__init__(self, index=self.index, timestamp=self.timestamp, previous_hash=self.previous_hash, difficulty=self.difficulty, minter_balance=self.minter_balance, minter_address=self.minter_address, transactions=self.transactions)

    def hash(self):
        return hashlib.sha256(json.dumps(self, sort_keys=True).encode()).hexdigest()

    @staticmethod
    def genesis():
        owner_amount_signature = '3045022100f192164efcdead014d87c2c15bf67ec55d33a52ca886006dcbe5f245319a32ca02202bc929e13dee95fdefa530cf1cc56483ba0566d43ac1327a5469bc48af01e838'
        owner_validator_signature = '3045022073c3937557b0015aeebe9cc154b2d2f8c8dc39d5fb33a0f8b7ad3f883c98fb5a022100aa683337150e5711a02f3fd665dfeec50181f74e931831415bcfd338d677c33c'
        owner_stake_signature = '3045022100aaa707597e2c9fd5818586fc2b47bd8e330326c61fdfe7a243c3f033bb64814c022037e36d6335a71e8469b3892dd6fc0e8688eb266d779d6749dfb7aa9203b121b2'

        owner_amount_transaction = Transaction([TransactionIn('', GENESIS_BLOCK_INDEX, owner_amount_signature)], [TransactionOut(OWNER_ADDRESS, OWNER_INIT_AMOUNT)], TransactionTypes.COINBASE)
        owner_validator_transaction = Transaction([TransactionIn('', GENESIS_BLOCK_INDEX, owner_validator_signature)], [TransactionOut(CHAIN_ADDRESS, VALIDATOR_AMOUNT)], TransactionTypes.VALIDATOR)
        owner_stake_transaction = Transaction([TransactionIn('', GENESIS_BLOCK_INDEX, owner_stake_signature)], [TransactionOut(CHAIN_ADDRESS, OWNER_INIT_STAKE)], TransactionTypes.STAKE)

        return Block(GENESIS_BLOCK_INDEX, '', 0, 0, OWNER_ADDRESS, [owner_amount_transaction, owner_validator_transaction, owner_stake_transaction])

    @staticmethod
    def from_dict(block_data: dict):
        block = Block(block_data['index'], block_data['previous_hash'], block_data['difficulty'], block_data['minter_balance'], block_data['minter_address'])
        block.timestamp = block_data['timestamp']
        block.transactions = []

        for transaction_data in block_data['transactions']:
            block.transactions = block.transactions + [Transaction.from_dict(transaction_data)]
            block['transactions'] = block.transactions
        
        return block