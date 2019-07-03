import ipfshttpclient as ipfs
import os, json, time, shutil

class IpfsEmr:
    def __init__(self, host, port):
        try:
            self._client = ipfs.connect(f'/ip4/{host}/tcp/{port}/http', session=True)

        except ipfs.exceptions.ConnectionError as e:
            print(f'Wollah, Not able to establish a connection given this error {e}.')
  


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



    def get_patient_folder(self, folder_hash):
        """
        Downloading the entire folder for a given ptient to add the new
        data (files) to it
        """

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

        return self.push_patient_folder(f'./{patient_name}')



    def cat_folder_content(self, folder_hash):
        """
        Prints the content of the existing files in the given folder
        """
        # first list all the files that exist in this folder
        result = self._client.ls(folder_hash)
        files_data = result['Objects'][0]['Links']

        for file_data in files_data:
            # getting the fiels hash and name for every file and just print them for now
            file_hash = file_data['Hash']
            file_name = file_data['Name']

            content = self._client.cat(file_hash).decode('utf-8')
            print(f'The {file_name} contains: \n{content}')    



    def add_medical_record(self, folder_hash, data):
        """
        Adding new medical record for a given patient taking a json file as the data
        which will contain two fileds the first one the lab results and the second will
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

        self.get_patient_folder(folder_hash)
        
        try:
            data = json.loads(data)
        except Exception as exc:
            print(f'Can not parse the file given the exception: \n {exc}')
        
        if data['mr'] is None:
            print("Null value for the medical record in the given data")
        else:
            medical_record_data = data['mr']

            fname_as_time_stam = time.strftime("%Y%m%d-%H%M%S")
            medical_record_file_path = f'{folder_hash}/medical_records/{fname_as_time_stam}'

            try:
                with open(medical_record_file_path, 'x') as mr_file:
                    mr_file.write(medical_record_data)
            except Exception as exc:
                print(f'can not create and write to the new medical record {exc}')


        # TODO writing more than one file with their extension
        if data['lr'] is None:
            print('Null value for the lr in the given data')
        else:
            lab_result = data['lr']
            print(lab_result)

        new_folder_hash = self.push_patient_folder(f'./{folder_hash}')

        # TODO removing the old folder and unpin it from ipfs
        # print('remoing the old directory')
        # shutil.rmtree(f'./{folder_hash}')


        return new_folder_hash



    def close(self):
        """
            Closing the established connection
        """
        self._client.close()




if __name__ == '__main__':
    ipfs = IpfsEmr('127.0.0.1', '5001')
    
    new_user = 'Robin'
    new_user_Hash = ipfs.create_folder_structure(new_user)

    testing_data = {
        'lr': {
            'file_ext': 'png',
            'data': '64byte formting data'
        },
        'mr': 'an encrypted content'
    }
    testing_str = json.dumps(testing_data)

    updated_hash = ipfs.add_medical_record(new_user_Hash, testing_str)
    print(updated_hash)

    ipfs.get_patient_folder(updated_hash)
