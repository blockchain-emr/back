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

    # init create connection
    def __init__(self):

        try:
            self.w3 = Web3(Web3.HTTPProvider(
                ETH_NODE_URI, request_kwargs={'timeout': 30}))
            if self.isConnected():
                print("Connected to blockchain!")
                print("Started..")
                print("Welcome to CareBlocks :D")

            else:
                print("W3 couldn't connect to blockchain!")
        
        except Exception as e:
            print("Connecting to blockchain failed!")

    # check connection
    def isConnected(self):
        print("We have a valid connection to blockchain")
        return self.w3.isConnected()

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
        contract = self.contracts.get(name, {})
        w3 = self.w3

        if len(contract) == 0:
            contract = self.get_contract_json(name)
            if contract:
                self.contracts[name] = contract

                #instantiate contract
                contract_eth_instance = w3.eth.contract(
                    abi=contract['abi'],
                    bytecode=contract['bytecode'])

                # set account that will deploy the smart contract
                w3.eth.defaultAccount = w3.eth.accounts[0]

                # deploy contract
                tx_hash = contract_eth_instance.constructor().transact()
                print("Hash: ", tx_hash)
                # get transaction receipt which has address
                print("Bout to send transaction")
                tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, timeout=120)
                contract_address = tx_receipt['contractAddress']
                print("contract address:", contract_address)
                print("Contract deployed!")
            else:
                print("Failed to delpy contract.\nMake sure contract is compiled with truffle!")

        
    
    # get data from contract
    # set data on contract

# if __name__ == '__main__':
    # cb = CareBlocks()
    # print(cb.get_contract_json('CareBlock'))
    # cb.isConnected()
    # cb.deploy_contract('CareBlock')

# TODO add full comments