import sys, json
sys.path.append("..")
from common.config import *
from common.models import *
from utils import general as gutils


@app.route('/doctor/register',methods=['POST'])
@swag_from('../docs/swagger/doctor/register.yml')
def doctor_registeration():
	if not request.is_json:
		return jsonify(msg="Not Acceptable data format."), 406
	mail = request.json.get("email",None)
	pwd = request.json.get("password",None)
	if not mail or not pwd:
		log.error("Registeration - Missing user and password inputs")
		return jsonify(msg="Invaild credentials!"),400

	if len(Doctor.objects.filter(email=mail.lower()) )!=0:
		log.error("Registeration - already used email - "+mail)
		return jsonify(msg="This mail can't be used!") ,400
	doctor = Doctor(email=mail)
	doctor.password = gutils.hash_SHA512(pwd)
	doctor.first_name = request.json.get("first_name",None)
	doctor.last_name = request.json.get("last_name",None)
	doctor.save()

	log.info("Registeration Successed - Doctor : " + mail)
	return jsonify(msg="Registered!"), 201



@app.route('/orgauth',methods=['POST'])
@swag_from('../docs/swagger/organization/auth.yml')
def orgauth():
	if not request.is_json:
		return jsonify(msg="Not Acceptable data format."), 406
	auth_type = request.json.get('auth_type',None)
	if not auth_type:
		return jsonify(msg="Missing auth_type parameter"), 400
	else:
		if auth_type == "doctor":
			mail = request.json.get('auth_identifier', None)
			if not mail:
				return jsonify(msg="Missing email parameter"), 400

			e = Doctor.objects.filter(email=mail.lower())

		elif auth_type == "organization":
			username = request.json.get('auth_identifier', None)
			if not username:
				return jsonify(msg="Missing username parameter"), 400
			e = Organization.objects.filter(username=username.lower())

		else:
			return jsonify(msg="Value Error: can't recognize valid auth_type value."), 400

		password = request.json.get('password', None)
		if not e or len(e)==0 or not gutils.verify_hash(password,e[0].password):
			return jsonify(msg="Invaild credentials"), 401
		else:
			access_token = create_access_token(identity=json.loads(e.to_json()), expires_delta = token_expire)
			refresh_token = create_refresh_token(identity=json.loads(e.to_json()), expires_delta = refresh_expire)
			return jsonify(access_token=access_token,refresh_token=refresh_token, status=200)



@app.route('/doctor',methods=['GET'])
@jwt_required
@swag_from('../docs/swagger/doctor/list.yml')
def list_doctors():
	doctors = json.loads(Doctor.objects.only("first_name","last_name","id").to_json())
	print(doctors)
	for doc in doctors:
		print(doc)
		doc['id'] = doc['_id']['$oid']
		doc.pop("_id")
	return jsonify(doctors),200



@app.route('/organization/register',methods=['POST'])
@swag_from('../docs/swagger/organization/register.yml')
def org_registeration():
	if not request.is_json:
		return jsonify(msg="Not Acceptable data format."), 406
	username = request.json.get("username",None)
	pwd = request.json.get("password",None)
	if not username or not pwd:
		log.error("Registeration - Missing user and password inputs")
		return jsonify(msg="Invaild credentials!"),400

	if len(Organization.objects.filter(username=username.lower()) )!=0:
		log.error("Registeration - already used username - "+username)
		return jsonify(msg="This username can't be used!") ,400
	org = Organization(username=username)
	org.password = gutils.hash_SHA512(pwd)
	org.full_name = request.json.get("full_name",None)
	org.email = request.json.get("email",None)
	org.save()


	log.info("Registeration Successed - Organization : " + str(org))
	return jsonify(msg="Registered!"), 201
