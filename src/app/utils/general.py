from time import sleep as tsleep
import sys, json
from utils.ipfs import IPFS
from utils.careblocks import CareBlocks
from passlib.hash import pbkdf2_sha512
sys.path.append("..")
from common.config import *
from common.models import *


def store_user_data(patient_json, eth_address, password):
    print("Thread started ...")
    print("{}, {}, {}".format(patient_json, eth_address,password))

    CareBlocks.give_init_ether(eth_address)
    user_full_name = "{} {}".format(patient_json["first_name"],patient_json["last_name"])
    print("Creating ipfs and chain entries for user {} ..".format(user_full_name))
    # Create Patient.json for patient on IPFS & get hash
    ipfs_patient_hash = IPFS.add_new_patient(patient_json)
    print("User {}'s profile created on IPFS with hash {}".format(user_full_name,ipfs_patient_hash))
    # Add patient to block chain throught the CareBlock smart contract
    # Unlock patient  in order to register him to the chain
    CareBlocks.w3.personal.unlockAccount(eth_address, password, 240)
    CareBlocks.add_patient(
        eth_address,
        ipfs_patient_hash
    )
    print("User {} was added to the chain.".format(user_full_name))


def hash_SHA512(password):
    return pbkdf2_sha512.hash(password)

def verify_hash(password,user_hash):
    return pbkdf2_sha512.verify(password,user_hash)


def get_doctors_list(organization = None):
    doctors = []
    if organization is not None:
        org_obj = Organization.objects.get(id=organization)
        doctors = json.loads(Doctor.objects.only("first_name","last_name","id").filter(organization=organization).to_json())
        for doc in doctors:
            print(doc)
            doc['id'] = doc['_id']['$oid']
            doc.pop("_id")
    else:
        doctors = json.loads(Doctor.objects.only("first_name","last_name","id").to_json())
        for doc in doctors:
            print(doc)
            doc['id'] = doc['_id']['$oid']
            doc.pop("_id")
    return doctors
