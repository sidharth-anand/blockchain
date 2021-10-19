import hashlib
import json
import typing

from time import time

from blockchain.transaction import Transaction

class Block(dict):
    def __init__(self, index: int, proof_of_work: int, previous_hash: str, transactions: typing.List[Transaction] = []) -> None:
        self.index = index
        self.timestamp = time()
        self.proof_of_work = proof_of_work
        self.previous_hash = previous_hash
        self.transactions = transactions

        dict.__init__(self, index=self.index, timestamp=self.timestamp, proof_of_work=self.proof_of_work, previous_hash=self.previous_hash, transactions=self.transactions)

    def hash(self):
        return hashlib.sha256(json.dumps(self, sort_keys=True).encode()).hexdigest()

    @staticmethod
    def genesis():
        return Block(1, 0, '0')
