import typing
import hashlib

from enum import Enum
from functools import reduce

from ellipticcurve.ecdsa import Ecdsa
from ellipticcurve.signature import Signature
from ellipticcurve.publicKey import PublicKey

from blockchain.constants import COINBASE_AMOUNT, OWNER_INIT_AMOUNT

class TransactionTypes(Enum):
    COINBASE = 'coinbase'
    STAKE = 'stake'
    VALIDATOR = 'validator'
    TRANSFER = 'transfers'

class UnspentTransactionOut(dict):
    def __init__(self, transaction_out_id: str, transaction_out_index: int, address: str, amount: float) -> None:
        self.transaction_out_id = transaction_out_id
        self.transaction_out_index = transaction_out_index
        self.address = address
        self.amount = amount

        dict.__init__(self, transaction_out_id=self.transaction_out_id, transaction_out_index=self.transaction_out_index, address=self.address, amount=self.amount)

    @staticmethod
    def find_unspent_transaction_out(transaction_id: str, index: int, unspent_transaction_outs):
        return [u for u in unspent_transaction_outs if u.transaction_out_id == transaction_id and u.transaction_out_index == index][0]

class TransactionIn(dict):
    def __init__(self, transaction_out_id: str, transaction_out_index: int, signature: str) -> None:
        self.transaction_out_id = transaction_out_id
        self.transaction_out_index = transaction_out_index
        self.signature = signature

        dict.__init__(self, transaction_out_id=self.transaction_out_id, transaction_out_index=self.transaction_out_index, signature=self.signature)

    def get_amount(self, unspent_transaction_outs: typing.List[UnspentTransactionOut]) -> float:
        return UnspentTransactionOut.find_unspent_transaction_out(self.transaction_out_id, self.transaction_out_index, unspent_transaction_outs).amount

    def __eq__(self, other):
        return self.transaction_out_id + str(self.transaction_out_index) == other.transaction_out_id + str(other.transaction_out_index)

    def __hash__(self):
        return hash(self.transaction_out_id + str(self.transaction_out_index) + self.signature)

class TransactionOut(dict):
    def __init__(self, address: str, amount: float) -> None:
        self.address = address
        self.amount = amount

        dict.__init__(self, address=self.address, amount=self.amount)

class Transaction(dict):
    def __init__(self, transaction_ins: typing.List[TransactionIn], transaction_outs: typing.List[TransactionOut], transaction_type: TransactionTypes = TransactionTypes.TRANSFER) -> None:
            self.transaction_ins = transaction_ins
            self.transaction_outs = transaction_outs
            self.type = transaction_type

            dict.__init__(self, id=self.id, transaction_ins=self.transaction_ins, transaction_outs=self.transaction_outs)

    @property
    def id(self):
        ins = ''.join(list(map(lambda i: i.transaction_out_id + str(i.transaction_out_index), self.transaction_ins)))
        outs = ''.join(list(map(lambda o: o.address + str(o.amount), self.transaction_outs)))

        return hashlib.sha256((ins + outs + str(self.type)).encode()).hexdigest()

    def validate(self, unspent_transaction_outs: typing.List[UnspentTransactionOut]) -> bool:
        valid_ins = reduce(lambda a, b: a and b, map(lambda i: self.validate_transaction_in(i, unspent_transaction_outs), self.transaction_ins), True)
        if not valid_ins:
            return False

        total_in_value = reduce(lambda a,b: a + b, map(lambda i: i.get_amount(unspent_transaction_outs), self.transaction_ins), 0)
        total_out_value = reduce(lambda a,b: a + b, map(lambda o: o.amount, self.transaction_outs), 0)

        if not total_out_value == total_in_value:
            return False

        return True

    @staticmethod
    def validate_transactions_in_block(transactions, unspent_transaction_outs: typing.List[UnspentTransactionOut], block_index: int) -> bool:
        coinbase_transactions = [t for t in transactions if t.type == TransactionTypes.COINBASE]
        if not len(coinbase_transactions) == 1:
            return False
        if not Transaction.validate_coinbase_transaction(coinbase_transactions[0], block_index):
            return False

        transaction_ins = [i for t in transactions for i in t.transaction_ins]
        if not len(set(transaction_ins)) == len(transaction_ins):
            return False

        return reduce(lambda a,b : a and b, map(lambda t: t.validate(unspent_transaction_outs), [t for t in transactions if t.type != TransactionTypes.COINBASE]),True)

    def validate_transaction_in(self, transaction_in: TransactionIn, unspent_transaction_outs: typing.List[UnspentTransactionOut]) -> bool:
        referenced_unspent = [u for u in unspent_transaction_outs if u.transaction_out_id == transaction_in.transaction_out_id and u.transaction_out_index == transaction_in.transaction_out_index][0]
        
        key = PublicKey.fromString(referenced_unspent.address)
        signature = Signature._fromString(transaction_in.signature)

        return Ecdsa.verify(self.id, signature, key)

    @staticmethod
    def generation_coinbase_transaction(address: str, block_index: int):
        transaction_in = TransactionIn('', block_index, '')
        transaction_out = TransactionOut(address, COINBASE_AMOUNT) 

        return Transaction([transaction_in], [transaction_out], TransactionTypes.COINBASE)

    @staticmethod
    def process_transactions(transactions, unspent_transaction_outs: typing.List[UnspentTransactionOut], block_index: int) -> typing.Union[typing.List[UnspentTransactionOut], None]:
        if not Transaction.validate_transactions_in_block(transactions, unspent_transaction_outs, block_index):
            return None

        return Transaction.update_unspent_transaction_outs(transactions, unspent_transaction_outs)

    @staticmethod
    def update_unspent_transaction_outs(transactions, unspent_transaction_outs: typing.List[UnspentTransactionOut]) -> typing.List[UnspentTransactionOut]:
        new_unspent_transaction_outs = reduce(lambda a,b: a + b, map(lambda t: [UnspentTransactionOut(t.id, i, o.address, o.amount) for i, o in enumerate(t.transaction_outs)], transactions), [])
        consumed_transaction_outs = map(lambda i: UnspentTransactionOut(i.transaction_out_id, i.transaction_out_index, '', 0), reduce(lambda a,b: a + b, [t.transaction_ins for t in transactions], []))

        return [u for u in unspent_transaction_outs if not UnspentTransactionOut.find_unspent_transaction_out(u.transaction_out_id, u.transaction_out_index, consumed_transaction_outs)] + new_unspent_transaction_outs

    @staticmethod
    def validate_coinbase_transaction(transaction, block_index: int) -> bool:
        return transaction.type == TransactionTypes.COINBASE and len(transaction.transaction_ins) == 1 and len(transaction.transaction_outs) == 1 and transaction.transaction_ins[0].transaction_out_index == block_index and (transaction.transaction_outs[0].amount == COINBASE_AMOUNT or transaction.transaction_outs[0].amount == OWNER_INIT_AMOUNT)

    #TODO: Update this shit
    @staticmethod
    def from_dict(transaction_data: dict):
        return Transaction(transaction_data['recipient'], transaction_data['amount'])