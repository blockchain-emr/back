import ipfshttpclient as ipfs
import os, json, time, shutil


class IpfsEmr:
    def __init__(self, host, port):
        try:
            self._client = ipfs.connect(f'/ip4/{host}/tcp/{port}/http', session=True)
            print(f'\n...... Connection Established with ipfs host: {host}, and port: {port} ......\n')

        except ipfs.exceptions.ConnectionError as e:
            print(f'Wollah, Not able to establish a connection given the below ERROR \n{e}.')
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
        chronics_data = patient_data['chronic']

        if chronics_data:
            return chronics_data
        else:
            return 'This patient does not have any chronics'

    

    # README -> DEPRECATION FROM HERE TILL THE END
    def ls_folder_content(self, folder_hash):
        folder_data = self._client.ls(folder_hash)
        folder_content = folder_data['Objects'][0]['Links']
        return folder_content



    def close(self):
        print('\n...... Closing Connection :) ......\n')
        self._client.close()




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



    ipfsemr.close()

