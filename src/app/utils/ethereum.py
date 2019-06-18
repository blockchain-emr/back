import web3, os,sys
from web3 import Web3

sys.path.append("..")
from common.config import ETH_NODE_URI
node_uri = ETH_NODE_URI
if os.path.isfile('/.dockerenv') is True:
    node_uri = "http://infra_eth_1:8545"

w3 = Web3(Web3.HTTPProvider(node_uri, request_kwargs={'timeout': 60}))



def get_balance(acc_id):
  """
    Getting the eth balance of a given account on Blockchain.

    Args:
      acc_id <str> : the hex address of the account.

    Retruns:
      balance <int> : the eth balance of the account.
  """
  print("Getting balance, Connected : {} .".format(w3.isConnected()))
  if w3.isAddress(acc_id) is True:
    print("Given a valid account address.")
    return w3.eth.getBalance(Web3.toChecksumAddress(acc_id))
  else:
      return None



def create_account():
    pass
