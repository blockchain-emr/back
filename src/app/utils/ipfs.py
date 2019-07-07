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


    # README -> DEPRECATION FROM HERE TILL THE END
    def ls_folder_content(self, folder_hash):
        folder_data = self._client.ls(folder_hash)
        folder_content = folder_data['Objects'][0]['Links']
        return folder_content



    def push_patient_folder(self, folder_path):
        """
        Pushing an entire folder to ipfs and returning the hash of the
        parent folder to be stored in the blockchain
        """

        if os.path.isdir(folder_path):
            res = self._client.add(folder_path, recursive=True)
            folder_hash = res[-1]['Hash']
            print(f'folder has been added with an address {folder_hash}')
            return folder_hash

        else:
            print('The given path is not valid')
            exit(1)



    def pull_patient_folder(self, folder_hash):
        self._client.get(folder_hash)



    def create_folder_structure(self, patient_name):
        """
        Creating the folder structure for every NEW_ADDED patient
        to the blockchain, and creates initial two folders
        (lab_results, medical_records)
        """

        lab_results = f'./{patient_name}/lab_results'
        medical_records = f'./{patient_name}/medical_records'

        os.makedirs(lab_results, exist_ok=True)
        os.makedirs(medical_records, exist_ok=True)

        folder_hash = self.push_patient_folder(f'./{patient_name}')

        # removing folder after pushing it
        print('removing the old directory')
        shutil.rmtree(f'./{patient_name}')

        return folder_hash



    def add_medical_record(self, folder_hash, data):
        """
        Adding new medical record for a given patient taking a json file as the data
        which will contain two fields the first one the lab results and the second will
        be the medical record
        json_file{
            'lr': {
                'file_ext_1': 'ext',
                'encrypted_data_1': 'data',
                'file_ext_2': 'ext',
                'data': 'encrypted_data'
            },
            'mr': 'encrypted_json_file'
        }
        """

        self.pull_patient_folder(folder_hash)
        
        try:
            data = json.loads(data)
        except Exception as exc:
            print(f'Can not parse the file given the exception: \n {exc}')
        
        if data['mr'] is None:
            print("Null value for the medical record in the given data")
        else:
            medical_record_data = data['mr']

            fname_as_time_stam = time.strftime("%Y%m%d%H%M%S")
            medical_record_file_path = f'{folder_hash}/medical_records/{fname_as_time_stam}'

            try:
                with open(medical_record_file_path, 'x') as mr_file:
                    print('writing to the local file')
                    mr_file.write(medical_record_data)
            except Exception as exc:
                print(f'Can not create and write to the new medical record {exc}')


        # TODO writing more than one file with their extension
        if data['lr'] is None:
            print('Null value for the lr in the given data')
        else:
            lab_result = data['lr']
            print(lab_result)

        new_folder_hash = self.push_patient_folder(f'./{folder_hash}')

        # removing folders after adding it
        print(f'removing the old directory{folder_hash}')
        shutil.rmtree(f'./{folder_hash}')

        return new_folder_hash



    def get_patient_mrs(self, folder_hash):
        """
        Getting the content of the MRs for a given patient from ipfs then
        concatinate all those MR for returning it to the user as one json file
        """
        # Getting the MR folder hash
        nested_folders_data = self.ls_folder_content(folder_hash)

        mr_folder_hash = ''
        for folder in nested_folders_data:
            if folder['Name'] == 'medical_records':
                mr_folder_hash = folder['Hash']
                print(f'Getting medical record folder Hash:{mr_folder_hash}')
                break
        
        #Getting all the medical record given the mr_folder_hash
        if mr_folder_hash:
            files_data = self.ls_folder_content(mr_folder_hash)
        else:
            print('Can not get the medical record folder hash')
            exit(1)

        # getting the files content and compine them together
        all_mr_data = []
        if files_data:
            for file_info in files_data:
                file_content = self.get_file_content(file_info['Hash'])
                data = {'Name': file_info['Name'], 'Content': file_content}
                all_mr_data.append(data)
        else:
            print('Can not get the medical record files data')
            exit(1)
        
        # ordering the list
        all_mr_data_sorted = sorted(all_mr_data, key=lambda k: k['Name'])
        
        return json.dumps(all_mr_data_sorted)



    def get_patient_data(self, folder_hash):
        """
        Getting all the data for a given patient These data 
        Includes all his medical records and all his lab results
        """
       
        pass



    def get_patient_lr(self, folder_hash):
        #TODO looping over all the lr files and compine them into one file
        pass



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

    ipfsemr.close()

