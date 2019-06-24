import sys
sys.path.append("..")
from common.config import *
from utils import ethereum as eth


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

    password_validation = eth.validate_password(eth_address,password)
    if password_validation['result'] is False:
        return jsonify(msg=password_validation["data"]), 401

    user_identity = {
        "address" : eth_address,
        "creation_date" : password_validation["data"],
        "password": password #TODO: kill myself for this
     }

    access_token  = create_access_token(identity=user_identity, expires_delta = token_expire)
    refresh_token = create_refresh_token(identity=user_identity,expires_delta = refresh_expire)

    return jsonify(access_token=access_token,refresh_token=refresh_token), 200
