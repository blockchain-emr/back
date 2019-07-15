import sys, json, time, datetime
sys.path.append("..")
from utils.careblocks import CareBlocks
from utils.ipfs import IPFS
from common.config import *


@app.route('/get/chronics', methods=['GET'])
@jwt.invalid_token_loader
@jwt_required
@swag_from('../docs/swagger/chronics/get_chronics.yml')
def get_chronics():
    current_user = json.loads(get_jwt_identity())
    address = current_user['address']

    care_blk = CareBlocks.get_patient(address)

    all_chronics = IPFS.retreive_chronics(care_blk['ipfs_hash'])

    if all_chronics:
        return jsonify(all_chronics), 200
    else:
        return jsonify(msg="Can't retrieve them", status=400)



@app.route('/add/chronics', methods=['POST'])
@jwt.invalid_token_loader
@jwt_required
@swag_from('../docs/swagger/chronics/add_chronics.yml')
def add_chronic():
    if not request.is_json:
        return jsonify(msg="Unacceptable data format.", status=406)

    new_chronic = request.json

    current_user = json.loads(get_jwt_identity())
    address = current_user['address']
    print(f"Current user is : {address}")

    care_blk = CareBlocks.get_patient(address)

    # adding the appointment to IPFS
    new_ipfs_hash = IPFS.add_chronics(care_blk['ipfs_hash'], new_chronic)


    #Firing notification
    notifay_msg = "Succesfully added a new Chronics data"
    time_stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    hash_after_firing = IPFS.fire_notification(new_ipfs_hash, notifay_msg, time_stamp)

    # update patient ipfs hash on chain
    update_success = CareBlocks.update_patient_ipfs(address, hash_after_firing)

    if update_success:
        return jsonify(msg='Updated successfully', status=201)
    else:
        return jsonify(msg="Can't add the appointment failed", status=400)
