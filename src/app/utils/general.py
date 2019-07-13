from time import sleep as tsleep
from utils.ipfs import IPFS
from utils.careblocks import CareBlocks

def store_user_data(patient_json, eth_address, password):
    print("Thread started ...")
    CareBlocks.give_init_ether(address)
    user_full_name = "{} {}".format(patient_json["first_name"],patient_json["last_name"])
    print("Creating ipfs and chain entries for user {} ..".format(user_full_name))
    # Create Patient.json for patient on IPFS & get hash
    ipfs_patient_hash = IPFS.add_new_patient(patient_json)
    print("User {}'s profile created on IPFS with hash {}".format(user_full_name,ipfs_patient_hash))
    # Add patient to block chain throught the CareBlock smart contract
    # Unlock patient account in order to register him to the chain
    CareBlocks.w3.personal.unlockAccount(eth_address, password, 240)
    CareBlocks.add_patient(
        eth_address,
        ipfs_patient_hash
    )
    print("User {} was added to the chain.".format(user_full_name))
