import sys, json,threading, time
sys.path.append("..")
from common.config import *
from utils import general as gutils
from utils.careblocks import CareBlocks


@app.route('/auth',methods=['POST'])
@swag_from('../docs/swagger/accounts_management/auth.yml')
def auth():
    if not request.is_json:
        return jsonify(msg="Unacceptable data format."), 406

    eth_address = request.json.get('address', None)
    password = request.json.get('password', None)
    if not eth_address:
        return jsonify(msg="Missing address parameter."), 400
    if not password:
        return jsonify(msg="Missing password parameter."), 400

    password_validation = CareBlocks.validate_password(eth_address, password)
    if password_validation['result'] is False:
        return jsonify(msg=password_validation["data"]), 401

    user_identity = {
        "address" : eth_address
    }
    user_identity = json.dumps(user_identity)
    print(user_identity)

    access_token  = create_access_token(identity=user_identity, expires_delta = token_expire)
    refresh_token = create_refresh_token(identity=user_identity,expires_delta = refresh_expire)

    return jsonify(access_token=access_token,refresh_token=refresh_token), 200


@app.route('/register',methods=['POST'])
@swag_from('../docs/swagger/accounts_management/register.yml')
def register():
    if not request.is_json:
        return jsonify(msg="Unacceptable data format."), 406

    first_name = request.json.get("first_name",None)
    last_name = request.json.get("last_name",None)
    email = request.json.get("email",None)
    age = request.json.get("age",None)
    national_id = request.json.get("national_id",None)
    phone_number = request.json.get("phone_number",None)
    password = request.json.get("password",None)

    eth_address = CareBlocks.create_account(password)
    if not eth_address:
        return jsonify(msg="Error happened, not created."), 500
    else:
        # Unlock patient account in order to register him to the chain
        CareBlocks.w3.personal.unlockAccount(eth_address, password, 240)

        # Add patient to block chain throught the CareBlock smart contract
        CareBlocks.add_patient(
            eth_address,
            '{} {}'.format(first_name, last_name),
            'QxIPFS' # TODO handle IPFS
        )

    return jsonify({
                    'address': eth_address,
                    'status_code': 201
                    })
