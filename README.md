# Blockchain Programming Assignment

## Run Locally

Step #1: Build the Web UI
Ensure that you have [Node.js](https://nodejs.org) installed on your machine

```bash
  cd blockchain
```
```bash
  cd web
```
```bash
  yarn install
```
```bash
  yarn build
```

Ensure that you have [python3](python.org/downloads/) installed on your machine

Download all the required dependencies for Python

```bash
  cd blockchain
```

```bash
  pip3 install -r requirements.txt
```

After successfully installing the dependencies, run the main.py file for launching the web app

This command runs the blockchain node both on ports 4000 and 4001 as default, so ensure both of these ports are free
```
  python3 main.py
```

In addition to using a port to serve the UI over HTTP, the application also uses a SOCKET_PORT to communicate with other nodes

To create a new node in the blockchain
```bash
  python3 main.py --port=PORT --socket=SOCKET_PORT
```
PORT = New port address for the node to instanstiate
SOCKET_PORT = Socket port address for the node

Since, in POS, you need to stake some coins to be able to mint blocks, a static owner wallet has already been setup in the Genesis Block. This wallet is configured to be a validator with 50 coins as account balance, and an additional 10 coin stake. To use this account, run
```
python3 main.py --owner
```

### Functionality
After running the main.py

Launch http://localhost:4000/ in your browser to see the Web App running

When you launch any additional nodes, use the register node form and enter `http://localhost:4000` (or the url of the first node you launched) and click on register. This will setup up peer-to-peer communications with all existing nodes. You should now be able to view the full list of nodes in the linked nodes section

There is a Wallet Button in the Navbar, which shows coins that you have in your wallet. It also shows your wallet address and whether you are a validator.

The Stake Coins Button allows you to stake some coins on the chain if you are a validator, allowing you to mint blocks.

There exist these options on the Web App at first glance.
1. Chain: List of Blocks with their properties are listed here
2. Verified Transactions: List of all verified transactions are listed here
3. Unverified Transactions: Transactions that are not verified are listed here
4. Linked Nodes: All the registered nodes of the blockchain, which can be registered from the registered node block on the website, are listed here
6. Wallet: Shows coins that you have in your wallet account. This also shows your wallet address. When people want to transfer coins you will be needing to provide the address present in your wallet. Also indicates whether or not you are a validator
7. Add a new transaction: The Recipient's wallet address, and Amount of the transaction has to be mentioned, and this transaction goes into the Unverified Transactions list.
8. Mine: You can mine on the Unverified Transactions page to view the transactions on the Verified Transactions Page
9. Stake Coins: stake some coins on the chain if you are a vlaidator, allowing you to mint blocks.

#### Transactions
The following transaction types are present in the app
1. Transfer - Indicates a transfer from one wallet to the next
2. Validator - Burns 10 coins from a wallet to the chain, and allows the wallet to become a validator
3. Stake - Transfers coins from a wallet to the chain as stake
4. Coinbase - Used to setup the ICO for the owner wallet and provide rewards for minting

All of the above transactions are linked to a wallet using Bitcoin's method of UnspentTransactionOuts.

#### POS
The app uses Ethereum's POS algorithm:
```
SHA256(prevhash + address + timestamp) <= 2^256 * stake / diff
```

You can find this implementation in the `validate_stake` method in `blockchain/blockchain.py`

#### P2P and Consensus

All changes to the chain - adding a transaction, registering a node, minting a new block - are propogated throughout the network of nodes using P2P connections. 

Consensus is achieved among the nodes on which chain to adopt by calculating the Accumulated Difficulty on a chain and not the chain length.
(Find the implementation in `get_accumulated_difficulty` in `blockchain/blockchain.py`)

Difficulty is increased or decreased based on the constants `BLOCK_GENERATION_INTERVAL` and `DIFFICULTY_ADJUSTMENT_ITNERVAL` in `blockchain/constants.py`
(See how these constants are used in `get_adjusted_difficulty` in `blockchain/blockchain.py`)

### API Documentation
#### Wallet
##### [GET] Wallet
```
Shows all the content of a wallet
  - Wallet Address
  - Account Balance
  - Is validator
  - Staked coins
```

```curl
http://localhost:4000/wallet
```
Sample response
```json
{
    "address": [
        "db8439eb600af85672a9c2f5d7370fe2798c19ef8fba22ea3ed02567b99cb2d2e708bcc258e7ea7741b44430a7199a8cb9474444be6b458b3bafbb3baa3e31f5",
        200
    ],
    "balance": 0,
    "is_validator": false,
    "stake": 0
}
```

##### [GET] Wallet Address
```
This endpoint returns the public key of the node's wallet
```
```curl
http://localhost:4000/wallet/address
```
Sample response
```curl
db8439eb600af85672a9c2f5d7370fe2798c19ef8fba22ea3ed02567b99cb2d2e708bcc258e7ea7741b44430a7199a8cb9474444be6b458b3bafbb3baa3e31f5
```

##### [GET] Wallet Balance
```
This endpoint returns the balance amount of coins present in the wallet
```
```curl
http://localhost:4000/wallet/balance
```
Sample response
```curl
25.0
```

##### [GET] Wallet Stake
```
This endpoint returns the amount of coins that are put on stake by the node
```
```curl
http://localhost:4000/wallet/stake
```
Sample response
```curl
5
```

##### [GET] Wallet Check if Validator
```
This endpoint returns true if the given node is a validator
```
```curls
http://localhost:4000/wallet/validator
```
Sample response
```curl
true
```

#### Transactions
##### [POST] Become a Validator - Transaction
```
    Create a new validator transaction
    - This transaction makes the user a Validator
    - VALIDATOR_AMOUNT is burnt
        - VALIDATOR_AMOUNT burnt is non-refundable
        - The amount is transferred to CHAIN_ADDRESS (128 bits of '0')
```
```
This endpoint returns the amount of coins that are put on stake by the node
```
```curl
http://localhost:4000/transactions/validator
```
Sample response
```json
you are already a validator
```

##### [POST] Create a new transaction
```
    Create a new transaction
    - This is a POST Endpoint to create a new transaction between a sender and recipient
    - The request body contains two paramenters
        - Recipient - address of the wallet of recipient
        - Amount - number of coins that are need to be transferred
```
```curl
http://localhost:4000/transactions/new
```
Sample Body
```json
{
    "recipient": "d9eb850f0bf8294113e9d121239be418934611c3ff36aac4d1ed3055af46993b34040c002101f8c552b91d2ea91e60a8187f82ec012c640e2d01c3eec1d5e489",
    "amount":"20"
}
```
Sample response
```json
{
    "message": "Added your transaction to pool"
}
```

##### [POST] Stake Coins
```
    Create a new stake transaction
    - This is a POST Endpoint to create a new transaction to stake coins enabling the user to mint blocks
    - The request body contains two paramenters
        - Amount - number of coins that are need to be staked
```
```curl
http://localhost:4000/transactions/stake
```
Sample Body
```json
{
    "amount":"2"
}
```
Sample response
```curl
'Added your transaction to pool'
```

##### [GET] Transaction Pool
```
    Get Transactions Pool
    - This endpoint returns all the transactions currently in the pool
    - Once the block is minted, the transaction pool is emptied and this endpoint then returns an empty array
```
```curl
http://localhost:4000/transactions/pool
```
Sample Response
```json
[
    {
        "id": "21626cfbeb1a4d8eabfbfd4f4bac585c7a555e92baceb862d2bcd16d55b7142c",
        "transaction_ins": [
            {
                "signature": "30440220499e695ae36d906c36f4265ccdb8af34bb34e8b5b096e5a1dc256d718a9a43d402200cdb98b77ffd6ee8ff060fe9caedcfda0e3f679d84ab1f45a195d65ac381858b",
                "transaction_out_id": "a85c5e0f292e499ca416c562cf749162df9c99aa5471adba39057f2b8911add2",
                "transaction_out_index": 0
            },
            {
                "signature": "304402203ad42f3b468180e34eca19acb857358d6a5ad5e3c4b466e52085d735784db64302207cef90e943cec5de4354c64fb93f2c4a1b88ea21c6fd4d6bbcd34893a3d9c550",
                "transaction_out_id": "9ccf4ed8bc7a8a5a35698f809af11693c139b908b65d6325e9e15733f9b2b592",
                "transaction_out_index": 1
            }
        ],
        "transaction_outs": [
            {
                "address": "d9eb850f0bf8294113e9d121239be418934611c3ff36aac4d1ed3055af46993b34040c002101f8c552b91d2ea91e60a8187f82ec012c640e2d01c3eec1d5e489",
                "amount": 20.0
            },
            {
                "address": "fc15e6f072f6421cdb903da96936c2b0528f752bceb3a7f8b74260149a1b293d647e48c37925f69b0105d28a82e00f3af2bd3e7c5974a43db39887287a585eca",
                "amount": 5.0
            }
        ],
        "type": "transfer"
    }
]
```

##### [GET] Mint Blocks
```
- The requirements a node has to fulfil to mint nodes is:
        - It must be a validator
        - It must stake some coints before minting
    - If any of the requirements fail to occur, the minting process is not taken forward
    - Once the requirements are fulfiled, consensus algorithms is run, block is created and appended to the chain
```
```curl
http://localhost:4000/mint
```
Sample response
```curl
'Minting Completed!'
```

##### [GET] Print the chain
```
    Chain
    - This endpoint returns the whole full blockchain
    - All the blocks with transactions and the length of blockchain is returned as json
```
```curl
http://localhost:4000/chain
```
Sample response
```json
{
    "chain": [
        {
            "difficulty": 0,
            "index": 1,
            "minter_address": "fc15e6f072f6421cdb903da96936c2b0528f752bceb3a7f8b74260149a1b293d647e48c37925f69b0105d28a82e00f3af2bd3e7c5974a43db39887287a585eca",
            "minter_balance": 0,
            "previous_hash": "",
            "timestamp": 1635166871.445565,
            "transactions": [
                {
                    "id": "08efdf57fa672ca56a4bbf6607681d2a27019d8741e4673adf4dd55ecc354d4d",
                    "transaction_ins": [
                        {
                            "signature": "3045022100f192164efcdead014d87c2c15bf67ec55d33a52ca886006dcbe5f245319a32ca02202bc929e13dee95fdefa530cf1cc56483ba0566d43ac1327a5469bc48af01e838",
                            "transaction_out_id": "",
                            "transaction_out_index": 1
                        }
                    ],
                    "transaction_outs": [
                        {
                            "address": "fc15e6f072f6421cdb903da96936c2b0528f752bceb3a7f8b74260149a1b293d647e48c37925f69b0105d28a82e00f3af2bd3e7c5974a43db39887287a585eca",
                            "amount": 50
                        }
                    ],
                    "type": "coinbase"
                },
                {
                    "id": "41fd558a5d670419438600968a7f1480236ae4800d784f17d62e27a37abc78a6",
                    "transaction_ins": [
                        {
                            "signature": "3045022073c3937557b0015aeebe9cc154b2d2f8c8dc39d5fb33a0f8b7ad3f883c98fb5a022100aa683337150e5711a02f3fd665dfeec50181f74e931831415bcfd338d677c33c",
                            "transaction_out_id": "",
                            "transaction_out_index": 1
                        }
                    ],
                    "transaction_outs": [
                        {
                            "address": "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                            "amount": 10
                        }
                    ],
                    "type": "validator"
                },
                {
                    "id": "3f999f91b84369fee4c4270da85cad47c51bc06fe2ed60e594f83b0fc68c56ed",
                    "transaction_ins": [
                        {
                            "signature": "3045022100aaa707597e2c9fd5818586fc2b47bd8e330326c61fdfe7a243c3f033bb64814c022037e36d6335a71e8469b3892dd6fc0e8688eb266d779d6749dfb7aa9203b121b2",
                            "transaction_out_id": "",
                            "transaction_out_index": 1
                        }
                    ],
                    "transaction_outs": [
                        {
                            "address": "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                            "amount": 5
                        }
                    ],
                    "type": "stake"
                }
            ]
        },
        {
            "difficulty": 0,
            "index": 2,
            "minter_address": "fc15e6f072f6421cdb903da96936c2b0528f752bceb3a7f8b74260149a1b293d647e48c37925f69b0105d28a82e00f3af2bd3e7c5974a43db39887287a585eca",
            "minter_balance": 50,
            "previous_hash": "1b521fb7a5c3d86a589caa59a93b46db9ade906ac9ea71efbe93dbd8e07c4fbd",
            "timestamp": 1635167117.656538,
            "transactions": [
                {
                    "id": "a85c5e0f292e499ca416c562cf749162df9c99aa5471adba39057f2b8911add2",
                    "transaction_ins": [
                        {
                            "signature": "",
                            "transaction_out_id": "",
                            "transaction_out_index": 2
                        }
                    ],
                    "transaction_outs": [
                        {
                            "address": "fc15e6f072f6421cdb903da96936c2b0528f752bceb3a7f8b74260149a1b293d647e48c37925f69b0105d28a82e00f3af2bd3e7c5974a43db39887287a585eca",
                            "amount": 5
                        }
                    ],
                    "type": "coinbase"
                },
                {
                    "id": "9ccf4ed8bc7a8a5a35698f809af11693c139b908b65d6325e9e15733f9b2b592",
                    "transaction_ins": [
                        {
                            "signature": "3044022046c45c73e87daa4837e06f7d61827a6213742ed24aa10b4faaefa26329d96611022071353ae28aabf45dccb08ec014e9172241c0ff53f1abf4748b1894d9ec742050",
                            "transaction_out_id": "08efdf57fa672ca56a4bbf6607681d2a27019d8741e4673adf4dd55ecc354d4d",
                            "transaction_out_index": 0
                        }
                    ],
                    "transaction_outs": [
                        {
                            "address": "db8439eb600af85672a9c2f5d7370fe2798c19ef8fba22ea3ed02567b99cb2d2e708bcc258e7ea7741b44430a7199a8cb9474444be6b458b3bafbb3baa3e31f5",
                            "amount": 30.0
                        },
                        {
                            "address": "fc15e6f072f6421cdb903da96936c2b0528f752bceb3a7f8b74260149a1b293d647e48c37925f69b0105d28a82e00f3af2bd3e7c5974a43db39887287a585eca",
                            "amount": 20.0
                        }
                    ],
                    "type": "transfer"
                }
            ]
        }
    ],
    "length": 2
}
```

### Team Details
###### Group Number : G56
1. [Battula Venkata Sai Ankit](https://github.com/saiankit) - 2019AAPS0331H
2. [Sreekar Venkata Nutulapati](https://github.com/sreekarnv) - 2019AAPS1217H
3. [Sidharth Anand](https://github.com/sidharth-anand/) - 2019A7PS1203H