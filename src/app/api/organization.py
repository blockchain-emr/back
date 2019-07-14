import sys, json
sys.path.append("..")
from common.config import *
from common.models import *
from utils import general as gutils


@app.route('/doctor/register',methods=['POST'])
@jwt_required
@swag_from('../docs/swagger/doctor/register.yml')
def doctor_registeration():
	if not request.is_json:
		return jsonify(msg="Not Acceptable data format."), 406
	current_user = json.loads(get_jwt_identity())
	acc_type = current_user["acc_type"]
	if acc_type == "organization":
		organization = Organization.objects.get(id=current_user["id"])
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
		doctor.phone_number = request.json.get("phone_number")
		doctor.organization = organization
		doctor.save()

		log.info("Registeration Successed - Doctor : " + mail)
		return jsonify(msg="Registered!"), 201
	else:
		return jsonify(msg="Only an organization can register a doctor."), 401



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
			entity = {}
			e = json.loads(e[0].to_json())
			entity["id"] = e["_id"]["$oid"]
			entity["acc_type"] = auth_type
			entity = json.dumps(entity)
			print(entity)
			access_token = create_access_token(identity=entity, expires_delta = token_expire)
			refresh_token = create_refresh_token(identity=entity, expires_delta = refresh_expire)
			if auth_type == "doctor":
				return jsonify(access_token=access_token,refresh_token=refresh_token, status=200)
			else:
				return jsonify(token=access_token,refresh_token=refresh_token, status=200)



@app.route('/doctor',methods=['GET'])
@jwt_required
@swag_from('../docs/swagger/doctor/list.yml')
def list_doctors():
	current_user = json.loads(get_jwt_identity())
	if current_user["acc_type"] == "organization":
		doctors = gutils.get_doctors_list(current_user["id"])
	elif current_user["acc_type"] == "patient":
		doctors = gutils.get_doctors_list()
	else:
		return jsonify(msg="Unknown requester entity."),401
	return jsonify(doctors),200


@app.route('/doctor/profile',methods=['GET'])
@jwt_required
@swag_from('../docs/swagger/doctor/profile.yml')
def get_doctor_profile():
	current_user = json.loads(get_jwt_identity())
	if current_user["acc_type"] == "doctor":
		doc = Doctor.objects.only("first_name","last_name","email","organization","phone_number").get(id=current_user["id"])
		print("doc phone = " + doc.phone_number)
		doctor_obj = {
		"full_name" : doc.first_name + " " + doc.last_name,
		"email" : doc.email,
		"organization": doc.organization.full_name,
		"phone_number": doc.phone_number
		}

	else:
		return jsonify(msg="Unauthorized."),401
	return jsonify(doctor_obj),200


@app.route('/organization/profile',methods=['GET'])
@jwt_required
@swag_from('../docs/swagger/organization/profile.yml')
def get_org_profile():
	current_user = json.loads(get_jwt_identity())
	if current_user["acc_type"] == "organization":
		org = Organization.objects.only("full_name","email","username","phone_number").get(id=current_user["id"])
		org = json.loads(org.to_json())
		org.pop("_id")

	else:
		return jsonify(msg="Unauthorized."),401
	return jsonify(org),200


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


@app.route('/organization/profile',methods=['POST'])
@jwt_required
@swag_from('../docs/swagger/organization/edit_profile.yml')
def edit_org_profile():
	if not request.is_json:
		return jsonify(msg="Not Acceptable data format."), 406
	print("requst json {} ".format(request.json))
	current_user = json.loads(get_jwt_identity())
	acc_type = current_user["acc_type"]
	if acc_type == "organization":
		org = Organization.objects.get(id = current_user["id"])
		org.full_name = request.json.get("full_name",None)
		org.email = request.json.get("email",None)
		org.phone_number = request.json.get("phone_number",None)
		org.username = request.json.get("username",None)
		org.save()
		return jsonify(msg="Edited!",status=201)
	else:
		return jsonify(msg="Only an organization is allowed to call this endpoint."), 401
