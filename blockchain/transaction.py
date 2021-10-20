class Transaction(dict):
    def __init__(self, sender: str, recipient: str, amount: float) -> None:
            self.sender = sender
            self.recipient = recipient
            self.amount = amount

            dict.__init__(self, sender=self.sender, recipient=self.recipient, amount=self.amount)

    @staticmethod
    def from_dict(transaction_data: dict):
        return Transaction(transaction_data['sender'], transaction_data['recipient'], transaction_data['amount'])