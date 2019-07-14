import ipfshttpclient as ipfs
import os, json, datetime, shutil


class IpfsEmr:
    def __init__(self, host, port):
        try:
            self._client = ipfs.connect(f'/ip4/{host}/tcp/{port}/http', session=True)
            print(f'\n...... Connection Established with ipfs host: {host}, and port: {port} ......\n')

        except Exception as e:
            print(f'...... Wollah, Not able to establish a connection given the below ERROR: ......\n\n{e}.\n')
            exit(1)



    def get_json_file(self, file_hash):
        data = self._client.get_json(file_hash)

        # make sure the comming data in dict format
        if not isinstance(data, dict):
            data = json.loads(data)
            return data
        else:
            return data
        


    def push_json_file(self, json_file):
        file_hash = self._client.add_json(json_file)

        if file_hash:
            return file_hash

        else:
            print(f'Can not push the json file')
            exit(1)



    def get_file_content(self, file_hash):
        """
        Getting the content for a given file hash as a string
        """
        data = self._client.cat(file_hash).decode('utf-8')
        return data


    
    def add_new_patient(self, patient_profile_data):
        """ creating the json file for a new added patient returning the file hash """

        if not isinstance(patient_profile_data, dict):
            print(f'Converting the patient_pro_data into json object')
            patient_profile_data = json.loads(patient_profile_data)
        
        patient_data = {
            'profile_data': patient_profile_data,
            'appointments': {},
            'chronic': '',
            'lab_results': ''
        }

        patient_hash = self.push_json_file(patient_data)
        print(f'Successfully added a new patient with file hash: {patient_hash}')

        return patient_hash



    def get_patient_profile(self, patient_hash):
        """ retreiving the main patient json file and gets the profile data from it"""
        patient_data = self.get_json_file(patient_hash)
        profile = patient_data['profile_data']

        return profile
        


    def edit_patient_profile(self, patient_hash, new_profile):
        patient_data = self.get_json_file(patient_hash)
        patient_data['profile_data'] = new_profile

        print(f'The new edited patient data is {patient_data["profile_data"]}')

        new_patient_hash = self.push_json_file(patient_data)
        print(f'Successfully edited the patient profile')

        return new_patient_hash



    def add_chronics(self, patient_hash, chronic_data):
        # add json file then update the field in the patient_data file
        chronic_hash = self.push_json_file(chronic_data)
        patient_data = self.get_json_file(patient_hash)

        # adding the chronic file hash into the patient data file
        patient_data['chronic'] = chronic_hash
        print(patient_data)
        new_patient_hash = self.push_json_file(patient_data)

        return new_patient_hash
    


    def retreive_chronics(self, patient_hash):
        patient_data = self.get_json_file(patient_hash)
        chronics_hash = patient_data['chronic']

        if chronics_hash:
            chronics_data = self.get_json_file(chronics_hash)

            if chronics_data:
                return chronics_data
                
        else:
            return 'This patient does not have any chronics'

    

    def add_appointement(self, patient_hash, appointment_data):
        # 1 pushing the data as a file to ipfs {timestamp: appointment_file_hash}
        appointement_hash = self.push_json_file(appointment_data)
        appointement_ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        # time.sleep(2)
        patient_data = self.get_json_file(patient_hash)
        appointments = patient_data['appointments']

        # adding the new key value pair to the dictionary of appointments
        appointments[appointement_ts] = appointement_hash
        
        patient_data['appointments'] = appointments
        print(f'patient data after adding appointments {patient_data}')

        new_patient_hash = self.push_json_file(patient_data)

        return new_patient_hash



    def retrieve_appointement_ts(self, patient_hash, last_time_stamp):
        """all_appointmentsall_appointments
        Taking a timestamp and retrieve all the appointments that happened 
        after this timestamp
        """
        last_time_stamp = int(last_time_stamp)
        # getting all the time stamps from the appointments dictionary
        patient_data = self.get_json_file(patient_hash)
        appointments_data = patient_data['appointments']

        all_appointments = {}
        if appointments_data:
            for ts, file_hash in appointments_data.items():
                if last_time_stamp < int(ts):
                    print(f'{last_time_stamp} is smaller than {int(ts)}')
                    data = self.get_json_file(file_hash)
                    all_appointments[ts] = data
                
            print(all_appointments)
            return all_appointments

        else:
            print('The given patient doesn\'t have any previous appointments')
        
        
        
    def retrieve_all_appointements(self, patient_hash):
        patient_data = self.get_json_file(patient_hash)
        appointements_data = patient_data['appointments'] # dict {'tiemstamp': 'file_hash'}

        all_appointments = {}
        if appointements_data:
            for ts, file_hash in appointements_data.items():
                data = self.get_json_file(file_hash)
                print(f'Time Stamp: {ts}, has data {data}')
                all_appointments[ts] = data
                
            print(all_appointments)
            return all_appointments

        else:
            print('The given patient doesn\'t have any previous appointments')
        


    def add_lab_result(self, patient_hash, attachments_hashs, meta_data, appointment_ts):
        """ 
        lab result json file it's a meta data about every lab result in which it contains
        data about the lab, attachments, and the appointment time_stamp in which this lab
        result happened in 
        """
        patient_data = self.get_json_file(patient_hash)
        lab_result_hash = patient_data['lab_results']

        lab_result_ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        lab_result_json_file = ''
        if lab_result_hash:
            # If there is a lab_result hash get it and append to it
            lab_result_json_file = self.get_json_file(lab_result_hash)

            lab_result_json_file[lab_result_ts] = {
                'meta_data': meta_data,
                'attachments': attachments_hashs,
                'appointments_ts': appointment_ts
            }

        else:
            # If it doesn't exist I will push it directly
            
            lab_result_json_file[lab_result_ts] = {
                'meta_data': meta_data,
                'attachments': attachments_hashs,
                'appointments_ts': appointment_ts
            }
        
        # PUSHING lab_result_json_file to ipfs
        new_lab_result_hash = self.push_json_file(lab_result_json_file)

        #PUSHING new_lab_result_hash to patient json file
        patient_data['lab_results'] = new_lab_result_hash

        new_patient_hash = self.push_json_file(patient_data)

        return new_patient_hash
    


    def retrieve_lab_results_for_appointment(self, patient_hash, appointment_ts):
        patient_data = self.get_json_file(patient_hash)
        lab_result_hash = patient_data['lab_results']

        if lab_result_hash:
            # lab results json file
            lab_results = self.get_json_file(lab_result_hash)

            lab_result_data = {}
            for _, data in lab_results.items():
                if data['appointments_ts'] == appointment_ts:
                    lab_result_data = data
            if lab_result_data:
                # getting attachments
                attachments_hashs = lab_result_data['attachments']

                self.retreive_attachments(attachments_hashs)
        else:
            print('There is not any lab_results data')



    def add_attachments(self, img_data):
        # TODO returning a list of files hashes that added to ipfs
        pass



    def retreive_attachments(self, attachments_hashs):
        # TODO getting all the attachments given the hashes
        pass



    def close(self):
        print('\n...... Closing Connection :) ......\n')
        self._client.close()


###################################################################################
###################################################################################
# create instance and import it whenever you need it
IPFS = IpfsEmr('127.0.0.1', '5001')


###################################################################################
###################################################################################
if __name__ == '__main__':

    ipfsemr = IpfsEmr('127.0.0.1', '5001')

    # dummy data comming with add_patient request
    patient_prof = {
        'name': 'Nico Robin',
        'mail': 'Robin@mail.com',
        'phone': '0102222255',
        'address': '0xsdfsf4sdf54454',
    }

    # adding the patient
    robin_hash = ipfsemr.add_new_patient(patient_prof)
    ipfsemr.retrieve_all_appointements(robin_hash)
    print(f'The new added patient: {ipfsemr.get_patient_profile(robin_hash)}')

    # editing the profile info
    patient_prof_edit = {
        'name': 'Robin',
        'mail': 'awesomerobin@mail.com',
        'phone': '0102222255',
        'address': '0xsdfsf4sdf54454',
    }

    new_robin_hash = ipfsemr.edit_patient_profile(robin_hash, patient_prof_edit)
    print(f'Get the new patient profile: {ipfsemr.get_patient_profile(new_robin_hash)}')


    # adding chronics to an existing patient
    # as chronics gonna be a single file so the doctor should every time in editing add
    # the new edits then send the whole file
    chronics_data = {
        'issues': ['diabetes type 1', 'High blood pressure'],
        'allergies': {
            'food allergies': ['milk', 'egg', 'Peanuts'],
            'others': ['Asthma']
        }
    }

    # adding new chronic file
    new_robin_hash_2 = ipfsemr.add_chronics(new_robin_hash, chronics_data)

    # retrive chronics
    chronics_data_ipfs = ipfsemr.retreive_chronics(new_robin_hash_2)
    print(f'Getting those chronics data from ipfs{chronics_data}')


    # adding appointement data
    app_1_data = {
        'diagnoses': 'flue',
        'diet': 'do not eat anything just FAST',
        'medications': ['asprine', 'rifo', 'panadol'],
        'other patient data': 'empty'
    }

    app_2_data = {
        'diagnoses': 'anything',
        'diet': 'do not eat anything just FAST',
        'medications': ['panadol'],
        'other patient data': 'just empty'
    }

    app_3_data = {
        'diagnoses': 'some random disease',
        'diet': 'Eat whatever you want do not listen to the doctor',
        'medications': ['asprine'],
        'other patient data': 'any other patient data that any doctor can write'
    }

    robin_hash_1 = ipfsemr.add_appointement(new_robin_hash_2, app_1_data)
    robin_data_after_first_app = ipfsemr.retrieve_all_appointements(robin_hash_1)

    print(robin_data_after_first_app)

    # pushing the second and third data 
    robin_hash_2 = ipfsemr.add_appointement(robin_hash_1, app_2_data)
    robin_hash_3 = ipfsemr.add_appointement(robin_hash_2, app_3_data)

    # retrieving after everything
    robin_final_data = ipfsemr.retrieve_all_appointements(robin_hash_3)

    # getting a timeStamp from our data to retrieve all the records after it
    time_st = ''
    for ts, data in robin_final_data.items():
        if data['diagnoses'] == 'anything':            
            time_st = ts
            print(time_st)

    # print(f'HEY YOU I NEED TO SLEEP AND THIS IS THE DATA AFTER ALL THIS AMAZING TIME WE HAD:\n\n {robin_final_data}\n')
    
    robin_data_ts = ipfsemr.retrieve_appointement_ts(robin_hash_3, time_st)
    print(f'HEY YOU I NEED TO SLEEP AND THIS IS THE DATA AFTER ALL THIS AMAZING TIME WE HAD:\n\n {robin_data_ts}\n')
    

    ipfsemr.close()

