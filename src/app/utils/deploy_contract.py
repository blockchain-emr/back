import sys, os, json
from web3 import Web3

sys.path.append("..")
from common.config import ETH_NODE_URI

node_uri = ETH_NODE_URI
if os.path.isfile('/.dockerenv') is True:
    node_uri = "http://infra_eth_1:8545"

w3 = Web3(Web3.HTTPProvider(node_uri, request_kwargs={'timeout': 60}))

def deploy_contract():
  """
    Deploy Smart Contract on the Blockchain.

    Args:

    Retruns:
  """
  w3.personal.unlockAccount(w3.personal.listAccounts[9],"hossam", 1000)
  w3.eth.defaultAccount = w3.eth.accounts[9]
  
  # compile contract with truffle compile first
  # load compiled contract file
  file_dir = os.path.dirname(os.path.realpath('__file__'))
  contract_path = os.path.join(file_dir, '../truffle/build/contracts/CareBlock.json')
  ContractFile = json.load(open(contract_path))
  abi = ContractFile['abi']
  bytecode = ContractFile['bytecode']

  # instantiate contract
  contract = w3.eth.contract(abi=abi, bytecode=bytecode)

  # deploy contract
  tx_hash = contract.constructor().transact()
  
  # get transaction receipt which has address

  tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
  contract_address = tx_receipt['contractAddress']
  print("contract address:", contract_address)
  print("Contract deployed!")

  # get contract instance

if __name__ == '__main__':
    deploy_contract()