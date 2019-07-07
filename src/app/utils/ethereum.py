import web3, os,sys, json
#from datetime import datetime as dt
from glob import glob
from web3 import Web3

sys.path.append("..")
from common.config import ETH_NODE_URI, ETH_KEYSTORE_RELATIVE_PATH
node_uri = ETH_NODE_URI
if os.path.isfile('/.dockerenv') is True:
    node_uri = "http://infra_eth_1:8545"

w3 = Web3(Web3.HTTPProvider(node_uri, request_kwargs={'timeout': 60}))



def get_balance(acc_address):
  """
    Getting the eth balance of a given account on Blockchain.

    Args:
      acc_address <str> : the hex address of the account.

    Retruns:
      balance <int> : the eth balance of the account.
  """
  print("Getting balance, Connected : {} .".format(w3.isConnected()))
  if w3.isAddress(acc_address) is True:
    print("Given a valid account address.")
    return w3.eth.getBalance(Web3.toChecksumAddress(acc_address))
  else:
      return None



def validate_password(acc_address, password):
    """
        Validate password through Trying to decrypt private key of the account.

        Args:
          acc_address <str> : the hex address of the account.
          password <str> : the password to validate.

        Retruns:
          valid <dict> : {result: Ture, data: creation_date <datetime> } if valid, {result: False, data: error_msg <str>} otherwise.
    """
    state = {"result":False,"data":None}

    if w3.isAddress(acc_address) is True:
        acc_address = acc_address[2:].lower()

        file_full_path = "{}*--{}".format(ETH_KEYSTORE_RELATIVE_PATH,acc_address)
        print("file address = {}, cwd = {}".format(file_full_path,os.getcwd()))
        keystore_file = glob(file_full_path)
        print("keystore file : '{}'".format(keystore_file))
        if keystore_file:
            keystore_file = keystore_file[0]
            if decrypt_private_key(keystore_file, password) is not None:
                state["result"] = True
            else:
                state["data"] = "Invalid password."
        else:
            state["data"] = "Can't locate keystore for account."
    else:
        state["data"] = "Invalid account address."

    return state



def decrypt_private_key(keystore_file_path, password):
    """
        Trying to decrypt private key of account using given password.

        Args:
          keystore_file_path <str> : path to an existing account keystore.
          password <str> : the password to validate.

        Retruns:
          key <hexbytes.main.HexBytes> : HexBytes private key, or None if failed.
    """

    with open(keystore_file_path,'r') as keystore_file:
        keystore_content = keystore_file.read()

    keystore_content = json.loads(keystore_content)
    try:
        private_key = w3.eth.account.decrypt(keystore_content,password)
        return private_key
    except Exception as e:
        if str(e) == "MAC mismatch":
            return None
        else:
            #TODO: handle this.
            return None



def create_account(password):
    """
        Creates an account on the chain.

        Args:
          password <str> : the password to be used to encrypt the private key.

        Retruns:
          address <str> : Hexadecimal address of the created account, None if error.
    """
    try:
        if password:
            return w3.personal.newAccount(password)
    except Exception as e:
        print("failed to create account.")
    return None
