#constants
from flask import Flask, jsonify, abort, request
import logging
import datetime as dt
from flasgger import Swagger,swag_from
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity, jwt_refresh_token_required, create_refresh_token
)


ETH_NODE_URI = "http://localhost:8545"
ETH_KEYSTORE_RELATIVE_PATH = "../../Infra/files/keystore/"

global app, log,jwt, token_expire,refresh_expire,reset_expire
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = b'\x1bY!*?\xbb9\xb4\x98\xb0\xd6\r\xe7\x089\xdd\xc55\x80w\xd4\xc3\xce\xecM.\xc7\xd1(i' #os.urandom(50)
swagger = Swagger(app)
jwt = JWTManager(app)

token_expire   = dt.timedelta(seconds=14400)# 4 hours #days=2)
refresh_expire = dt.timedelta(days=0.5)
reset_expire   = dt.timedelta(seconds=10800)# 3 hours


formater = logging.Formatter("%(asctime)s In %(filename)s : %(message)s")
formater.datefmt = "%Y/%m/%d %H:%M:%S"
log = logging.getLogger('mylogger')
handler1 = logging.FileHandler('info.log')
handler1.setLevel(logging.INFO)
handler1.setFormatter(formater)
log.addHandler(handler1)

handler2 = logging.FileHandler('error.log')
handler2.setLevel(logging.ERROR)
handler2.setFormatter(formater)
log.addHandler(handler2)
log.setLevel(logging.INFO)
