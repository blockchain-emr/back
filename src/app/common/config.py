#constants
from flask import Flask, jsonify, abort, request
import logging
from flasgger import Swagger,swag_from
ETH_NODE_URI = "http://localhost:8545"

global app, log
app = Flask(__name__)
swagger = Swagger(app)

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
