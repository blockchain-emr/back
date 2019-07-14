import sys, json, time
sys.path.append("..")
from utils.careblocks import CareBlocks
from utils.ipfs import IPFS
from common.config import *



# adding appointment
@app.route('/add/appointment', methods=['POST'])
@jwt.invalid_token_loader
@jwt_required
@swag_from('../docs/swagger/appointment/add_appointment.yml')
def add_appointment():
    if not request.is_json:
        return jsonify(msg="Unacceptable data format.", status=406)

    new_appointment = request.json

    current_user = json.loads(get_jwt_identity())
    address = current_user['address']
    print(f"Current user is : {address}")

    care_blk = CareBlocks.get_patient(address)

    # adding the appointment to IPFS
    new_ipfs_hash = IPFS.add_appointement(care_blk['ipfs_hash'], new_appointment)

    # update patient ipfs hash on chain
    update_success = CareBlocks.update_patient_ipfs(address, new_ipfs_hash)

    if update_success:
        return jsonify(status=201)
    else:
        return jsonify(msg="Can't add the appointment failed", status=400)



# retrieving all appointments
@app.route('/get/appointments', methods=['GET'])
@jwt.invalid_token_loader
@jwt_required
@swag_from('../docs/swagger/appointment/get_all_appointments.yml')
def get_all_appointments():
    current_user = json.loads(get_jwt_identity())
    address = current_user['address']

    care_blk = CareBlocks.get_patient(address)
    
    all_appointments = IPFS.retrieve_all_appointements(care_blk['ipfs_hash'])

    if all_appointments:
        return jsonify(all_appointments, status=200)
    else:
        return jsonify(msg="Can't retrieve them", status=400)



# retrieve all apointments after a given time stamp
@app.route('/get/appointments/ts', methods=['POST'])
@jwt.invalid_token_loader
@jwt_required
@swag_from('../docs/swagger/appointment/get_appointment_ts.yml')
def get_appointment_ts():
    if not request.is_json:
        return jsonify(msg="Unacceptable data format.", status=406)
    time_stamp = request.json

    current_user = json.loads(get_jwt_identity())
    address = current_user['address']

    care_blk = CareBlocks.get_patient(address)

    appointments_after_ts = IPFS.retrieve_appointement_ts(care_blk['ipfs_hash'], time_stamp)

     if appointments_after_ts:
        return jsonify(appointments_after_ts, status=200)
    else:
        return jsonify(msg="Can't retrieve them", status=400)

