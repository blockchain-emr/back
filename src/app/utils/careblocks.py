# imports
import sys
sys.path.append("..")
from common.config import ETH_NODE_URI, CONTRACTS_PATH

import os
import json
from web3 import Web3
from solc import compile_source


# class
class CareBlocks:

    w3 = None
    contracts = {}

    # init create connection
    def __init__(self):

        try:
            self.w3 = Web3(Web3.HTTPProvider(
                ETH_NODE_URI, request_kwargs={'timeout': 30}))
            if self.isConnected():
                print("Connected to blockchain")
            else:
                print("W3 couldn't connect to blockchain!")
        
        except Exception as e:
            print("Connecting to blockchain failed!")

    # check connection
    def isConnected(self):
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
    

    # deploy contract
    def deploy_contract(self, name):
        contract = contracts.get(name, {})

        if len(contract) == 0:
            contract = self.get_contract_json(name)
        

        
    
    # get data from contract#
    # set data on contract

# if __name__ == '__main__':
    # cb = CareBlocks()