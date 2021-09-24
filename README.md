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

Launch http://localhost:4000/ in your browser to see the Web App running

To create a new node in the blockchain
```bash
  python3 main.py --port=PORT
```
PORT = New port address for the node to instanstiate

### Team Details
###### Group Number : G56
1. [Battula Venkata Sai Ankit](https://github.com/saiankit) - 2019AAPS0331H
2. [Sreekar Venkata Nutulapati](https://github.com/sreekarnv) - 2019AAPS1217H
3. [Sidharth Anand](https://github.com/sidharth-anand/) - 2019A7PS1203H