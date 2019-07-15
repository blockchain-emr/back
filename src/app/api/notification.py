import sys, json, time
sys.path.append("..")
from utils.careblocks import CareBlocks
from utils.ipfs import IPFS
from common.config import *


@app.route('/get/notifications', methods=['GET'])
@jwt.invalid_token_loader
@jwt_required
@swag_from('../docs/swagger/notifications/get_notifications.yml')
def get_notifications():
    current_user = json.loads(get_jwt_identity())
    address = current_user['address']

    care_blk = CareBlocks.get_patient(address)

    all_notifications = IPFS.get_notifications(care_blk['ipfs_hash'])

    if all_notifications:
        return jsonify(all_notifications), 200
        
    else:
        return jsonify("Can't retrieve notifications"), 400