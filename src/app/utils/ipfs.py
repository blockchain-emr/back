import ipfshttpclient as ipfs
import os, json

class IpfsEmr:
    def __init__(self, host, port):
        try:
            self._client = ipfs.connect(f'/ip4/{host}/tcp/{port}/http', session=True)

        except ipfs.exceptions.ConnectionError as e:
            print(f'Wollah, Not able to establish a connection given this error {e}.')
        

    def add_file(self, file_path):
        if os.path.isfile(file_path):
            res = self._client.add(file_path)
            file_hash = res['Hash']
            print(f'File has been added with an address {file_hash}')
            return file_hash

        else:
            print('The given path is not valid')
            exit(1)


    def get_file(self, file_hash):
        """
            taking the file hash and retrive the file from ipfs
            return the content of the given file as a string
        """
        content = self._client.cat(file_hash)
        content_str = content.decode("utf-8")

        return content_str

        
    def add_folder(self, folder_path):
        if os.path.isdir(folder_path):
            res = self._client.add(folder_path, recursive=True)
            folder_hash = res[-1]['Hash']
            print(f'folder has been added with an address {folder_hash}')
            return folder_hash

        else:
            print('The given path is not valid')
            exit(1)


    def get_folder(self, folder_hash):
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
    


    def create_folder_structure(self, patient_name):
        """
        Creating the folder structure for every NEW_ADDED patient
        to the blockchain, and creates initial files with them to 
        store meta data about our two folders (lab_results, medical_records)
        """

        lab_results = f'./{patient_name}/lab_results'
        medical_records = f'./{patient_name}/medical_records'

        meta_data_lr = f'./{patient_name}/lab_results/meta_data_lr.json'
        meta_data_mr = f'./{patient_name}/medical_records/meta_data_mr.json'


        os.makedirs(lab_results, exist_ok=True)
        os.makedirs(medical_records, exist_ok=True)

        # creating initial files as meta data for every folder to keep track of the folders
        data = {'current_num': 0}

        create_meta_data_files(path=meta_data_lr, data=data)
        create_meta_data_files(path=meta_data_mr, data=data)

        # Pushing the folder to the blockchain

        return self.add_folder(f'./{patient_name}')



    def close(self):
        """
            Closing the established connection
        """
        self._client.close()




def create_meta_data_files(path, data):
    with open(path, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=2)



if __name__ == '__main__':
    ipfs = IpfsEmr('127.0.0.1', '5001')
    
    new_user = 'Ahmed'
    new_user_Hash = ipfs.create_folder_structure(new_user)

    