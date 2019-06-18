import sys
sys.path.append("..")
from utils import ethereum as eth
from common.config import *

@swag_from('../docs/swagger/account_details/get_balance.yml')
@app.route('/account/balance/<string:acc_id>', methods=['GET'])
def get_balance(acc_id):
    balance = eth.get_balance(acc_id)
    if balance is not None:
      print(type(balance))
      return jsonify({'balance': balance}),200
    else:
      return jsonify({'result': "Invalid account address."}),400
