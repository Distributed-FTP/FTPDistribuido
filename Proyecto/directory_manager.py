import os

class Directory_Manager():
    def __init__(self):
        self.path = os.getcwd()
    
    #Directories
    def create_directory(self, directory_name: str):
        os.mkdir(directory_name)
    
    def delete_directory(self, directory_name: str):
        os.rmdir(directory_name)
    
    def is_directory(self, directory_name: str):
        return os.path.isdir(directory_name)
    
    def list_directory(self, directory_name: str):
        return os.listdir(directory_name)
    
    #Files
    def open_file(self, file_name: str, read_mode: str):
        return open(file_name, read_mode)
    
    def delete_file(self, file_name: str):
        os.remove(file_name)
    
    def is_file(self, file_name: str):
        return os.path.isfile(file_name)
        
    def get_file_size(self, file_name: str):
        return os.path.getsize(file_name)
        
    #All
    def rename(self, name: str, new_name: str):
        os.rename(name, new_name)