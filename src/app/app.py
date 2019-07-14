#!flask/bin/python
import argparse
from common.config import *
from api.account_details import *
from api.authentication import *
from api.organization import *



if __name__ == '__main__':
    log.info("Application launched")
    parser = argparse.ArgumentParser(prog='app.py')
    parser.add_argument("--debug",action="store_true", help="Enables debug mode.")
    args    = parser.parse_args()
    if args.debug:
        app.run(host="0.0.0.0",port=5000,threaded=True,debug=True)
    else:
        app.run(host="0.0.0.0",port=5000,threaded=True)
