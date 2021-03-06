import os
import socket
import tqdm
from chord import Node

class Directory_Manager():
    def __init__(self, path: str, node_chord: Node):
        self.path = path + "/Reports/files.fl"
        self.path_default = path
        self.route_path = path
        self.route_path_default = path
        self.__buffer = 1024
        self.__node = node_chord
    
    
    #Directories
    def create_directory(self, directory_name: str):
        directory_name = directory_name.replace("//", "/")
        files = ""
        with open(self.path, 'rb') as f:
            while True:
                bytes_read = f.read()
                if bytes_read == b'':
                    break
                else:
                    files += str(bytes_read)
        file_list = files.split("\\n")
        for i in range(len(file_list)):
            file = str(file_list[i]).replace("b'", '')
            file_list[i] = str(file).replace("'", '')
        path = directory_name.split(self.route_path_default)
        file_list.append("D~~" + path[len(path)-1] + "/")   
        files = ""
        for i in range(len(file_list)):
            if file_list[i] != "":
                files += file_list[i] + "\n"
        files.replace("//", "/")
        self.__node.create_directory(directory_name)
        with open(self.path, 'w') as f:
            f.write(files)
    
    def delete_directory(self, directory_name: str):
        directory_name = directory_name.replace("//", "/")
        files = ""
        with open(self.path, 'rb') as f:
            while True:
                bytes_read = f.read()
                if bytes_read == b'':
                    break
                else:
                    files += str(bytes_read)
        
        file_list = files.split("\\n")
        for i in range(len(file_list)):
            file = str(file_list[i]).replace("b'", '')
            file_list[i] = str(file).replace("'", '')
        path = directory_name.split(self.route_path_default)
        if path[len(path)-1] == "/root/" or path[len(path)-1] == "/root/anonymous/":
            return EOFError
        file_list.remove("D~~" + path[len(path)-1] + "/")   
        files = ""
        for i in range(len(file_list)):
            if file_list[i] != "":
                files += file_list[i] + "\n" 
        files.replace("//", "/")
        self.__node.delete_directory(directory_name)
        with open(self.path, 'w') as f:
            f.write(files)
    
    def is_directory(self, directory_name: str):
        directory_name = directory_name.replace("//", "/")
        files = ""
        with open(self.path, 'rb') as f:
            while True:
                bytes_read = f.read()
                if bytes_read == b'':
                    break
                else:
                    files += str(bytes_read)
        
        file_list = files.split("\\n")
        for i in range(len(file_list)):
            file = str(file_list[i]).replace("b'", '')
            file_list[i] = str(file).replace("'", '')
        
        directory_name = directory_name.split(self.route_path_default)
        path = directory_name[len(directory_name)-1]
        path = "D~~" + path
        if path[len(path)-1] != "/":
            path += "/"
        if file_list.__contains__(path):
            return True
        return False
    
    def list_directory(self, directory_name: str):
        directory_name = directory_name.replace("//", "/")
        directory_selection = directory_name.split("/root/")
        directory_name = "/root/" + directory_selection[1]
        self.route_path = directory_name
        files = ""
        with open(self.path, 'rb') as f:
            while True:
                bytes_read = f.read()
                if bytes_read == b'':
                    break
                else:
                    files += str(bytes_read)
        file_list = files.split("\\n")
        list_result = []
        for i in range(len(file_list)):
            file = str(file_list[i]).replace("b'", '')
            file = str(file).replace("D~~", '')
            file = str(file).replace("F~~", '')
            file = str(file).replace("'", '')
            if file.__contains__(directory_name) and file != directory_name:
                list_result.append(self.route_path_default + file)
        return list_result
    
    def change_directory(self, directory_name: str):
        directory_name = directory_name.replace("//", "/")
        self.route_path = directory_name.split(self.route_path_default)[1]
    
    
    #Files   
    def upload_file(self, file_name: str, read_mode: str, socket_client: socket.socket):
        file_name = file_name.replace("//", "/")
        file_name = self.route_path + file_name
        files = ""
        with open(self.path, 'rb') as f:
            while True:
                bytes_read = f.read()
                if bytes_read == b'':
                    break
                else:
                    files += str(bytes_read)
        file_list = files.split("\\n")
        for i in range(len(file_list)):
            file = str(file_list[i]).replace("b'", '')
            file_list[i] = str(file).replace("'", '')
        if not file_list.__contains__("F~~" + file_name):
            file_list.append("F~~" + file_name)
        files = ""
        for i in range(len(file_list)):
            if file_list[i] != "":
                files += file_list[i] + "\n"
        files.replace("//", "/")
        with open(self.path_default + file_name, read_mode) as f:
            while True:
                bytes_recieved = socket_client.recv(self.__buffer)
                f.write(bytes_recieved)
                  
                if bytes_recieved == b'':
                    break 
        
        self.__node.upload_file(self.path_default + file_name)
        
        with open(self.path, 'w') as f:
            f.write(files)
    
    def download_file(self, file_name: str, read_mode: str, socket_client: socket.socket, progress: tqdm):
        file_name = file_name.replace("//", "/")
        file_name = self.route_path + file_name
        files = ""
        with open(self.path, 'rb') as f:
            while True:
                bytes_read = f.read()
                if bytes_read == b'':
                    break
                else:
                    files += str(bytes_read)
        file_list = files.split("\\n")
        for i in range(len(file_list)):
            file = str(file_list[i]).replace("b'", '')
            file = str(file).replace("D~~", '')
            file = str(file).replace("F~~", '')
            file_list[i] = str(file).replace("'", '')   
        
        self.__node.download_file(self.path_default + file_name)
        
        with open(self.path_default + file_name, read_mode) as f:
            for _ in progress:
                progress.update(len(bytes_read)) 
                bytes_read = f.read(self.__buffer)

                if bytes_read == b'':
                    break 
                socket_client.send(bytes_read)
            progress.close()
        
        self.__node.update_nodes()
        
    def delete_file(self, file_name: str):
        file_name = file_name.replace("//", "/")
        files = ""
        with open(self.path, 'rb') as f:
            while True:
                bytes_read = f.read()
                if bytes_read == b'':
                    break
                else:
                    files += str(bytes_read)
        
        file_list = files.split("\\n")
        for i in range(len(file_list)):
            file = str(file_list[i]).replace("b'", '')
            file_list[i] = str(file).replace("'", '')
        path = file_name.split(self.route_path_default)
        file_list.remove("F~~" + path[len(path)-1])   
        files = ""
        for i in range(len(file_list)):
            if file_list[i] != "":
                files += file_list[i] + "\n"
        self.__node.delete_file(file_name)
        with open(self.path, 'w') as f:
            f.write(files)
    
    def is_file(self, file_name: str):
        file_name = file_name.replace("//", "/")
        files = ""
        with open(self.path, 'rb') as f:
            while True:
                bytes_read = f.read()
                if bytes_read == b'':
                    break
                else:
                    files += str(bytes_read)
        
        file_list = files.split("\\n")
        for i in range(len(file_list)):
            file = str(file_list[i]).replace("b'", '')
            file_list[i] = str(file).replace("'", '')
        
        file_name = file_name.split(self.route_path_default)
        path = file_name[len(file_name)-1]
        path = "F~~" + path
        if file_list.__contains__(path):
            return True
        return False
        
    def get_file_size(self, file_name: str):
        return self.__node.get_size_file(self.path_default + self.route_path + file_name)
     
   
    #All
    def rename(self, name: str, new_name: str):
        name = name.replace(self.route_path_default, "")
        new_name = new_name.replace(self.route_path_default, "")
        name = name.replace("//", "/")
        new_name = new_name.replace("//", "/")
        files = ""
        with open(self.path, 'rb') as f:
            while True:
                bytes_read = f.read()
                if bytes_read == b'':
                    break
                else:
                    files += str(bytes_read)
                    
        file_list = files.split("\\n") 
        files = ""
        for i in range(len(file_list)):
            file = str(file_list[i]).replace("b'", '')
            file_list[i] = str(file).replace("'", '')
            if file_list[i] != "":
                files += file_list[i] + "\n"
        for i in range(len(file_list)):
            if file_list[i] == "F~~" + name:
                self.__node.change_name_file(self.route_path_default + name, self.route_path_default + new_name)
            elif file_list[i] == "D~~" + name + "/" or file_list[i] == "D~~" + name:
                self.__node.changeName_directory(self.route_path_default + name, self.route_path_default + new_name)
        files = files.replace(name, new_name)
        with open(self.path, 'w') as f:
            f.write(files)
       
        
    #Extra
    def basename(self, file_name: str):
        file_name = file_name.replace(self.route_path_default, "")
        file_name = file_name.replace("//", "/")
        names = file_name.split("/")
        names.remove("")
        if names[len(names)-1] != "":
            return names[len(names)-1]
        else:
            return names[len(names)-2]
    
    def stat(self, file_name: str):
        file_name = file_name.replace("//", "/")
        file_name = file_name.replace(self.route_path_default, "")
        files = ""
        with open(self.path, 'rb') as f:
            while True:
                bytes_read = f.read()
                if bytes_read == b'':
                    break
                else:
                    files += str(bytes_read)
        file_list = files.split("\\n")
        for i in range(len(file_list)):
            file = str(file_list[i]).replace("b'", '')
            file_list[i] = str(file).replace("'", '')
        for i in range(len(file_list)):
            if file_list[i] == "F~~" + file_name:
                return self.__node.state_file(self.route_path_default + file_name)
            elif file_list[i] == "D~~" + file_name + "/" or file_list[i] == "D~~" + file_name:
                return self.__node.state_directory(self.route_path_default + file_name)
        return None
