# imports
from glob import glob
import sys
sys.path.append("..")
from common.config import ETH_NODE_URI, CONTRACTS_PATH, ETH_KEYSTORE_RELATIVE_PATH

import os, json
from web3 import Web3

# Care Blocks Utility Class

class CareBlocksUtility:
    w3 = None
    isChainReady = False
    contracts = {}
    # contract used by class methods now, can be changed in the instance with a setter
    active_contract_name = 'CareBlock'

    # admin address and pass now need to be loaded as env vars
    __ETH_ADMIN_PASS = os.environ['ETH_ADMIN_PASS']
    __ETH_ADMIN_ADDRESS = os.environ['ETH_ADMIN_ADDRESS']


    # init create connection
    def __init__(self):

        try:
            node_uri = ETH_NODE_URI
            if os.path.isfile('/.dockerenv') is True:
                node_uri = "http://infra_eth_1:8545"
            
            self.w3 = Web3(Web3.HTTPProvider(
                node_uri, request_kwargs={'timeout': 30}))
            if self.is_connected():
                self.contracts = {}
                print("Connected to blockchain!")
                print("Started..")
                print("Welcome to CareBlocks :D")

            else:
                print("W3 couldn't connect to blockchain!")
        
        except Exception as e:
            print(e)
            print("Connecting to blockchain failed!")


    # check connection
    def is_connected(self):

        connected = self.w3.isConnected()
        if connected:
            print("We have a valid connection to blockchain")
        else:
            print("No connection to blockchain established")

        return connected


    # get contract path
    def get_contract_path(self, name, isCompiled=True):

        if name.lower().endswith('.sol'):
            name = name.split('.')[0]

        if isCompiled:
            return '{}{}{}.json'.format(CONTRACTS_PATH, '/build/contracts/', name)
        else:
            return '{}{}{}.sol'.format(CONTRACTS_PATH, '/contracts/', name)


    # get contract
    def get_contract_json(self, name):

        contract = self.contracts.get(name, {})

        if len(contract) > 0:
            return contract

        try:
            with open(self.get_contract_path(name)) as jcontract:
                contract = json.load(jcontract)
                self.contracts[name] = contract

        except FileNotFoundError as e:
            print(e)
            print("Please make sure you first run : 'truffle compile' ")

        return contract


    # get a list of loaded contracts
    def get_loaded_contracts(self):
        return self.contracts
    

    # deploy smart contract to chain
    def deploy_contract(self, name):
        print("Deploying started...")
        contract = self.contracts.get(name, {})
        w3 = self.w3

        # load if not loaded
        if len(contract) == 0:
            contract = self.get_contract_json(name)
            print("Extracted contract json")
            
        if contract:
            #instantiate contract
            contract_eth_instance = w3.eth.contract(
                    abi=contract['abi'],
                    bytecode=contract['bytecode'])

            # set account that will deploy the smart contract
            w3.eth.defaultAccount = self.__ETH_ADMIN_ADDRESS
            print("creating transaction")

            # deploy contract
            tx_hash = contract_eth_instance.constructor().transact()
            print("Hash: ", tx_hash)

            # get transaction receipt which has address
            print("Bout to send transaction")
            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, timeout=240)
            contract_address = tx_receipt['contractAddress']

            

            # save address in contract.json file for easier extraction later
            with open(self.get_contract_path(name), 'w') as out_file:
                contract['contractAddress'] = contract_address
                json.dump(contract, out_file)

            # add it to loaded contracts
            self.contracts[name] = contract

            print("contract address:", contract_address)
            print("Contract deployed!")


    # change active contract name
    def set_deployed_contract_name(self, name):
        self.active_contract_name = name


    # get ethereum instance of a deployed contract
    def get_contract_instance(self, name):

        contract = self.get_contract_json(name)
        
        if 'contractAddress' not in contract:
            print("Contract not deployed yet")
            print("Deploying.....")
            self.deploy_contract(name)
            contract = self.get_contract_json(name)
        
        return self.w3.eth.contract(
            contract['contractAddress'],
            abi=contract['abi']
        )


    # get data from contract
    def get_patient_count(self):
        contract_instance = self.get_contract_instance(self.active_contract_name)
        return contract_instance.call().patientCount()


    # add patient to blockchain
    def add_patient(self, patient_address, ipfs_address):

        contract_instance = self.get_contract_instance(self.active_contract_name)

        tx_hash = contract_instance.functions.addPatient(
            patient_address,
            ipfs_address
        ).transact(
            {'from': patient_address}
        )

        tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash, timeout=240)
        if tx_receipt:
            print("Successfully added Patient :)")
            self.get_patient(patient_address)
            return True
        else:
            return False
        

    # get patient CareBlock from blockchain
    def get_patient(self, patient_address):
        contract_instance = self.get_contract_instance(self.active_contract_name)

        # access patient CareBlock by his address
        patient = contract_instance.call().patients(patient_address)

        print("Here's the patient CareBlock :)")
        patient_dict = {'ipfs_hash': patient[1], 'verified': patient[2]}
        print(patient_dict)
        return patient_dict


    # update patient IPFS hash
    def update_patient_ipfs(self, patient_address, ipfs_address):
        contract_instance = self.get_contract_instance(self.active_contract_name)
        
        # create transaction
        tx_hash = contract_instance.functions.updatePatientIPFS(
            patient_address,
            ipfs_address
        ).transact(
            {'from': patient_address}
        )
        
        tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash, timeout=240)
        print("Updated patient IPFS hash")


    # update patient emr verification status
    def verify_patient_emr(self, patient_address, is_verified=True):
        contract_instance = self.get_contract_instance(
            self.active_contract_name)

        # create transaction
        tx_hash = contract_instance.functions.verifyPatient(
            patient_address,
            is_verified
        ).transact(
            {'from': patient_address}
        )

        # wait for it to be mined
        tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash, timeout=240)
        print("Updated patient verificatation status to:", is_verified)


    def create_account(self, password):
        """
            Creates an account on the chain.

            Args:
              password <str> : the password to be used to encrypt the private key.

            Retruns:
              address <str> : Hexadecimal address of the created account, None if error.
        """
        try:
            if password:
                address = self.w3.personal.newAccount(password)
                self.give_init_ether(address)
                return address

        except Exception as e:
            print("failed to create account.")
            print(e)
        return None


    def get_balance(self, acc_address):
        """
          Getting the eth balance of a given account on Blockchain.

          Args:
            acc_address <str> : the hex address of the account.

          Retruns:
            balance <int> : the eth balance of the account.
        """
        print("Getting balance...\n{}".format(self.is_connected()))
        if self.w3.isAddress(acc_address) is True:
          print("Given a valid account address.")
          return self.w3.eth.getBalance(Web3.toChecksumAddress(acc_address))
        else:
            return None

    
    # give some ether to newly created account
    def give_init_ether(self, acc_address):
        w3 = self.w3
        # required to prevent double spend problem
        # NOTE: This can be used to help with load balancing on mining chain
        nonce = w3.eth.getTransactionCount(self.__ETH_ADMIN_ADDRESS)

        # build transaction
        tx = {
            'nonce': nonce,
            'to': acc_address,
            'value': w3.toWei(10, 'ether'),
            'gas': 100000,
            'gasPrice': w3.eth.gasPrice
        }
        
        # sign it with admin private key
        pathk = self.get_keystore_file_path(self.__ETH_ADMIN_ADDRESS)
        pk = self.decrypt_private_key(
            pathk,
            self.__ETH_ADMIN_PASS
        )
        signed_tx = w3.eth.account.signTransaction(tx, pk)

        # send transaction
        try:
            print("gonna send init ether tx")
            tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
            print("waiting..")
            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            print("tranfsered init ether to : ", acc_address)
            print("Done boss ;)")

        except Exception as e:
            print(e)


    def validate_password(self, acc_address, password):
        """
            Validate password through Trying to decrypt private key of the account.

            Args:
              acc_address <str> : the hex address of the account.
              password <str> : the password to validate.

            Retruns:
              valid <dict> : {result: Ture, data: creation_date <datetime> } if valid, {result: False, data: error_msg <str>} otherwise.
        """
        state = {"result": False, "data": None}

        if self.w3.isAddress(acc_address) is True:
            acc_address = acc_address[2:].lower()
            keystore_file_path = self.get_keystore_file_path(acc_address)
            if keystore_file_path:
                if self.decrypt_private_key(keystore_file_path, password) is not None:
                    state["result"] = True
                else:
                    state["data"] = "Invalid password."
            else:
                state["data"] = "Can't locate keystore for account."
        else:
            state["data"] = "Invalid account address."

        return state


    def decrypt_private_key(self, keystore_file_path, password):
        """
            Trying to decrypt private key of account using given password.

            Args:
              keystore_file_path <str> : path to an existing account keystore.
              password <str> : the password to validate.

            Retruns:
              key <hexbytes.main.HexBytes> : HexBytes private key, or None if failed.
        """

        with open(keystore_file_path, 'r') as keystore_file:
            keystore_content = keystore_file.read()

        keystore_content = json.loads(keystore_content)
        try:
            private_key = self.w3.eth.account.decrypt(keystore_content, password)
            return private_key
        except Exception as e:
            if str(e) == "MAC mismatch":
                return None
            else:
                #TODO: handle this.
                return None

    # get path of patients keystore file
    def get_keystore_file_path(self, acc_address):
        acc_address = acc_address[2:].lower()
        fname = [f for f in os.listdir(ETH_KEYSTORE_RELATIVE_PATH) if f.find(
            acc_address[2:]) != -1][0]
        file_full_path = "{}{}".format(ETH_KEYSTORE_RELATIVE_PATH,fname) 
        # print("file address = {}, cwd = {}".format(file_full_path,os.getcwd()))
        keystore_file = glob(file_full_path)
        print("keystore file : {}".format(keystore_file))
        if keystore_file:
            keystore_file = keystore_file[0]
            return keystore_file
        else:
            return ''



###################################################################################
    # possible additions...
    # get latest block
    # get block by number

# create instance and import it when you need to interact with chain
CareBlocks = CareBlocksUtility()

###################################################################################
# if __name__ == '__main__':
    # cb = CareBlocks
    # print(cb.get_contract_json('CareBlock'))
    # cb.is_connected()
    # cb.deploy_contract('CareBlock')


