from flask import Flask

from p2p.node import P2PNode

from blockchain.blockchain import Blockchain

class HTTPApp:
        def __init__(self, app: Flask, node: P2PNode, chain: Blockchain) -> None:
            self.app = app
            self.node = node
            self.chain = chain
