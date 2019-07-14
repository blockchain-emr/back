import sys, json,threading, time
sys.path.append("..")
from common.config import *
from utils import general as gutils
from utils.careblocks import CareBlocks



@app.route('/auth',methods=['POST'])
@swag_from('../docs/swagger/accounts_management/auth.yml')
def auth():
    if not request.is_json:
        return jsonify(msg="Unacceptable data format.", status=406)

    eth_address = request.json.get('address', None)
    password = request.json.get('password', None)
    if not eth_address:
        return jsonify(msg="Missing address parameter.", status=400)
    if not password:
        return jsonify(msg="Missing password parameter.", status=400)

    password_validation = CareBlocks.validate_password(eth_address, password)
    if password_validation['result'] is False:
        return jsonify(msg=password_validation["data"], status=401)

    user_identity = {
        "address" : eth_address,
        "acc_type" : "patient"
    }
    user_identity = json.dumps(user_identity)
    print(user_identity)

    access_token  = create_access_token(identity=user_identity, expires_delta = token_expire)
    refresh_token = create_refresh_token(identity=user_identity, expires_delta = refresh_expire)

    # Unlock account for 2 hours, so the patient can interact with blockchain within that window
    # After this window, the access token will expire and the client needs to point them to relogin
    CareBlocks.w3.personal.unlockAccount(eth_address, password, 7200)

    return jsonify(access_token=access_token, refresh_token=refresh_token, status=200)


@app.route('/register',methods=['POST'])
@swag_from('../docs/swagger/accounts_management/register.yml')
def register():
    if not request.is_json:
        return jsonify(msg="Unacceptable data format.", status=406)

    patient_json = request.json

    password = patient_json.get("password",None)

    # create account for patient on ethereum & give them some ether
    eth_address = CareBlocks.create_account(password)
    print(type(eth_address))
    if not eth_address:
        return jsonify(msg="Error happened, not created.", status=500)
    else:
        # We don't need the password anymore
        del patient_json['password']
        thread = threading.Thread(target=gutils.store_user_data, args=(patient_json,eth_address,password))
        thread.daemon = True
        thread.start()
        print("Replying to client now ...")

    return jsonify(address=eth_address, status=201)
