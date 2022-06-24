import os

class Directory_Manager():
    def __init__(self):
        self.path = os.getcwd()
    
    def create_directory(self, directory_name: str):
        os.mkdir(directory_name)
    
    def delete_directory(self, directory_name: str):
        os.rmdir(directory_name)
    
    def rename_directory(self, directory_name: str, new_directory_name: str):
        os.rename(directory_name, new_directory_name)
    
    def list_directory(self, directory_name: str):
        os.listdir(directory_name)
    
    def create_file(self, file_name: str):
        os.mknod(file_name)
    
    def delete_file(self, file_name: str):
        os.remove(file_name)
    
    def download_file(self, file_name: str):
        os.system(f'wget {file_name}')
    
    def upload_file(self, file_name: str):
        os.system(f'wget {file_name}')