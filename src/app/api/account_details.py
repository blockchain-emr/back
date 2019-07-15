import sys, datetime
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
    user_type = current_user["acc_type"]
    print("Current user is : {}".format(address))
    balance = CareBlocks.get_balance(address)
    if balance is not None:
        return jsonify(balance=balance, current_user_address=address, status=200)
    else:
        return jsonify(msg="Invalid account address.", status=400)


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
        return jsonify(profile), 200
    else:
        return jsonify(msg="Invalid account Address", status=400)


@app.route('/account/profile', methods=['POST'])
@jwt.invalid_token_loader
@jwt_required
@swag_from('../docs/swagger/account_details/edit_profile.yml')
def edit_profile():

    if not request.is_json:
        return jsonify(msg="Unacceptable data format.", status=406)

    new_profile = request.json
    current_user = jloads(get_jwt_identity())
    address = current_user['address']

    # get patient CareBlock from chain
    careblock = CareBlocks.get_patient(address)
    print('Got their careblock boss:\n', careblock)

    # update their profile on IPFS
    new_ipfs_hash = IPFS.edit_patient_profile(careblock['ipfs_hash'], new_profile)


    # Firing notification
    notifay_msg = "Succesfully Editing Your profile data"
    time_stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    hash_after_firing = IPFS.fire_notification(new_ipfs_hash, notifay_msg, time_stamp)

    # update patient ipfs hash on chain
    update_success = CareBlocks.update_patient_ipfs(address, hash_after_firing)

    if update_success:
        return jsonify(status=201)
    else:
        return jsonify(msg="Edit failed", status=400)
