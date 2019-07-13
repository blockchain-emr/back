import sys
from json import loads as jloads
sys.path.append("..")
from utils.careblocks import CareBlocks
from utils.ipfs import IPFS
from common.config import *

@app.route('/account/balance', methods=['GET'])
@jwt.invalid_token_loader
@jwt_required
@swag_from('../docs/swagger/account_details/get_balance.yml')
def get_balance():
    current_user = jloads(get_jwt_identity())
    address = current_user["address"]
    print("Current user is : {}".format(address))
    balance = CareBlocks.get_balance(address)
    if balance is not None:
        print(type(balance))
        return jsonify({'balance': balance, "current_user_adress" : address}),200
    else:
        return jsonify({'result': "Invalid account address."}),400


@app.route('/account/profile', methods=['GET'])
@jwt.invalid_token_loader
@jwt_required
@swag_from('../docs/swagger/account_details/get_profile.yml')
def get_profile():
    current_user = jloads(get_jwt_identity())
    address = current_user['address']
    
    # get patient CareBlock from chain
    careblock = CareBlocks.get_patient(address)
    print('Got their careblock boss:\n', careblock)

    # get their profile from IPFS
    profile = IPFS.get_patient_profile(careblock['ipfs_hash'])

    if profile:
        return jsonify({'profile': profile}),200
    else:
        return jsonify({'result': "Invalid account Address"}), 400
    
