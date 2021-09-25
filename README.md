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
  npm install
```
```bash
  npm run build
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

This command runs the blockchain node on PORT = 4000 as default, so ensure your PORT 4000 to be free
```bash
  python3 main.py
```

To create a new node in the blockchain
```bash
  python3 main.py --port=PORT
```
PORT = New port address for the node to instanstiate

### Functionality
After running the main.py

Launch http://localhost:4000/ in your browser to see the Web App running

There are five options on the Web App at first glance.
1. Chain: List of Blocks with their properties are listed here
2. Verified Transactions: List of all verified transactions are listed here
3. Unverified Transactions: Transactions that are not verified are listed here
4. Linked Nodes: All the registered nodes of the blockchain, which can be registered from the registered node block on the website, are listed here
5. Resolve Conflicts: Resolve Conflicts by clicking here

There is a place for Add a new transaction, where you have to add the Sender, Recipient, and Amount of the transaction, and this transaction goes into the Unverified Transactions list. You can mine on the Unverified Transactions page to view the transactions on the Verified Transactions Page

### Team Details
###### Group Number : G56
1. [Battula Venkata Sai Ankit](https://github.com/saiankit) - 2019AAPS0331H
2. [Sreekar Venkata Nutulapati](https://github.com/sreekarnv) - 2019AAPS1217H
3. [Sidharth Anand](https://github.com/sidharth-anand/) - 2019A7PS1203H