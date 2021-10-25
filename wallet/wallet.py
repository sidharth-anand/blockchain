import typing
from functools import reduce

from ellipticcurve.ecdsa import Ecdsa
from ellipticcurve.privateKey import PrivateKey
from ellipticcurve.signature import Signature

from blockchain.transaction import Transaction, TransactionIn, TransactionOut, TransactionTypes, UnspentTransactionOut
from blockchain.constants import CHAIN_ADDRESS

class Wallet():
    def __init__(self) -> None:
        # Create Private Keys and Public Key from Private key
        self.private_key = PrivateKey()
        self.public_key = self.private_key.publicKey()

    def load_keys_from_file(self, filename: str) -> None:
        # If the node is owner, private key is loaded from wallet.key file
        # Public Key is created from private key loaded from wallet.key file
        self.private_key = PrivateKey.fromString(open(filename).readlines()[0])
        self.public_key = self.private_key.publicKey()

    def set_private_key(self, private_key: str) -> None:
        self.private_key = PrivateKey.fromString(private_key)
        self.public_key - self.private_key.publicKey()

    def create_transaction(self, recipient_address: str, amount: float, unspent_transaction_outs: typing.List[UnspentTransactionOut], transaction_pool: typing.List[Transaction], type: TransactionTypes = TransactionTypes.TRANSFER) -> typing.Union[Transaction, None]:
        my_address = self.public_key.toString()
        my_unspent_transactions = self.filter_transaction_pool([u for u in unspent_transaction_outs if u.address == my_address], transaction_pool)

        ret = self.transaction_outs_for_amount(my_unspent_transactions, amount)
        if ret is not None:
            (included_unspent_transaction_outs, left_over_amount) = ret
        else:
            return None

        unsigned_transaction_ins = [TransactionIn(unspent_transaction_out.transaction_out_id, unspent_transaction_out.transaction_out_index, '') for unspent_transaction_out in included_unspent_transaction_outs]
        transaction_outs = self.create_transaction_outs(recipient_address, amount, left_over_amount)

        transaction = Transaction(unsigned_transaction_ins, transaction_outs, type)

        transaction_signatures = self.get_transaction_signatures(transaction, unspent_transaction_outs)

        if transaction_signatures is None:
            return None

        for i, transaction_in in enumerate(transaction.transaction_ins):
            transaction.transaction_ins[i] = TransactionIn(transaction_in.transaction_out_id, transaction_in.transaction_out_index, transaction_signatures[i])

        return transaction

    def filter_transaction_pool(self, unspent_transasction_outs: typing.List[UnspentTransactionOut], transaction_pool: typing.List[Transaction]) -> typing.List[UnspentTransactionOut]:
        transaction_ins = [transaction_in for transaction in transaction_pool for transaction_in in transaction.transaction_ins]
        removable: typing.List[UnspentTransactionOut] = []

        for unspent_transaction_out in unspent_transasction_outs:
            current_ins = [transaction_in for transaction_in in transaction_ins if transaction_in.transaction_out_index == unspent_transaction_out.transaction_out_index and transaction_in.transaction_out_id == unspent_transaction_out.transaction_out_id]
            if len(current_ins) != 0:
                removable.append(unspent_transaction_out)

        return [unspent_transaction_out for unspent_transaction_out in unspent_transasction_outs if unspent_transaction_out not in removable]


    def transaction_outs_for_amount(self, unspent_transaction_outs: typing.List[UnspentTransactionOut], amount: float) -> typing.Union[typing.Tuple[typing.List[UnspentTransactionOut], float], None]:
        current_amount = 0
        included_unspent_transaction_outs: typing.List[UnspentTransactionOut] = []

        for unspent_transaction_out in unspent_transaction_outs:
            included_unspent_transaction_outs.append(unspent_transaction_out)
            current_amount += unspent_transaction_out.amount

            if current_amount >= amount:
                return (included_unspent_transaction_outs, current_amount - amount)
        return None


    def create_transaction_outs(self, recipient_address: str, amount: float, left_over_amount: float) -> typing.List[TransactionOut]:
        transaction_out = TransactionOut(recipient_address, amount)

        if left_over_amount == 0:
            return [transaction_out]
        else:
            left_over_transaction = TransactionOut(self.public_key.toString(), left_over_amount)
            return [transaction_out, left_over_transaction]


    def get_transaction_signatures(self, transaction: Transaction, unspent_transaction_outs: typing.List[UnspentTransactionOut]) -> typing.Union[typing.List[str], None]:
        signatures: typing.List[str] = []

        for i in range(len(transaction.transaction_ins)):
            transaction_in = transaction.transaction_ins[i]

            referenced_unspent_transaction_out = UnspentTransactionOut.find_unspent_transaction_out(transaction_in.transaction_out_id, transaction_in.transaction_out_index, unspent_transaction_outs)

            if referenced_unspent_transaction_out is None:
                return None

            if self.private_key.publicKey().toString() != referenced_unspent_transaction_out.address:
                return None

            signatures.append(Ecdsa.sign(transaction.id, self.private_key)._toString())

        return signatures


    """
        Can account Validate
        - If there is a transaction which has the type 'VALIDATOR', that shows that
          the node has undergone a transaction for it to become a validator
        - Hence, we are checking for a VALIDATOR TransactionType and returning True if it is existing
    """
    def can_account_validate(self, transactions: typing.List[Transaction]) -> bool:
        for transaction in transactions:
            if transaction.type == TransactionTypes.VALIDATOR and Ecdsa.verify(transaction.id, Signature._fromString(transaction.transaction_ins[0].signature), self.public_key):
                return True

        return False


    """
        Get Account Balance
        - User’s balance is calculated by scanning the blockchain and aggregating all UTXO belonging to that user/node.
    """
    def get_account_balance(self, unspent_transaction_outs: typing.List[UnspentTransactionOut]) -> float:
        return reduce(
          lambda a,b: a + b.amount,
          [unspent_transaction_out
          for unspent_transaction_out in unspent_transaction_outs
            if unspent_transaction_out.address == self.public_key.toString()
          ], 0)

    """
        Get Account Stake Balance
        - Amount of coins staked are calculated
    """
    def get_account_stake(self, transactions: typing.List[Transaction]) -> float:
        stake_amount = 0

        # If transaction type is STAKE, it is considered as a STAKE transaction
        # We calculate the transaction_outs and if the transaction_out.address == CHAIN_ADDRESS, the transaction_out.amount is added to stake_amount
        for transaction in transactions:
            if transaction.type == TransactionTypes.STAKE and Ecdsa.verify(transaction.id, Signature._fromString(transaction.transaction_ins[0].signature), self.public_key):
                for transaction_out in transaction.transaction_outs:
                    if transaction_out.address == CHAIN_ADDRESS:
                        stake_amount += transaction_out.amount

        return stake_amount