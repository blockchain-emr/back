# imports
import sys
sys.path.append("..")
from common.config import ETH_NODE_URI, CONTRACTS_PATH

import os
import json
from web3 import Web3


# Care Block Utility Class

class CareBlocks:

    w3 = None
    contracts = {}
    # contract used by class methods now, can be changed in the instance with a setter
    active_contract_name = 'CareBlock'   

    # init create connection
    def __init__(self):

        try:
            self.w3 = Web3(Web3.HTTPProvider(
                ETH_NODE_URI, request_kwargs={'timeout': 30}))
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
            w3.eth.defaultAccount = w3.eth.accounts[0]
            print("creating transaction")

            # deploy contract
            tx_hash = contract_eth_instance.constructor().transact()
            print("Hash: ", tx_hash)

            # get transaction receipt which has address
            print("Bout to send transaction")
            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, timeout=120)
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
        return self.w3.eth.contract(
            contract['contractAddress'],
            abi=contract['abi']
        )


    # get data from contract
    def get_patient_count(self):
        contract_instance = self.get_contract_instance(self.active_contract_name)
        return contract_instance.call().patientCount()


    # add patient to blockchain
    def add_patient(self, patient_address, patient_name, ipfs_address):

        contract_instance = self.get_contract_instance(self.active_contract_name)

        tx_hash = contract_instance.functions.addPatient(
            patient_address,
            patient_name,
            ipfs_address
        ).transact(
            {'from': self.w3.eth.accounts[0]}
        )

        tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash, timeout=120)
        print("Successfully added Patient :)")


    # get patient CareBlock from blockchain
    def get_patient(self, address):
        contract_instance = self.get_contract_instance(self.active_contract_name)

        # access patient CareBlock by his address
        patient = contract_instance.call().patients(address)

        print("Here the patient CareBlock :)")
        print(patient)
        return patient

    # possible additions...
    # get accounts
    # get account_balance
    # get latest block
    # get block by number


# if __name__ == '__main__':
    # cb = CareBlocks()
    # print(cb.get_contract_json('CareBlock'))
    # cb.is_connected()
    # cb.deploy_contract('CareBlock')

# TODO add full comments
