import socket
from threading import Thread
import Pyro4

Pyro4.expose
class RecvBytesforDownload(object):
  def get_bytes(self, bytes):
      return bytes

class Directory_Manager():
    def __init__(self, path: str):
        self.path = path + "/Reports/files.fl"
        self.path_default = path
        self.route_path = path
        self.route_path_default = path
        self.__buffer = 1024
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.__ip = s.getsockname()[0]
        #Thread(target=self.server_download).start()
    
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
        uri = "PYRO:DirectoriesManager@"+self.__ip+":8010"
        remote = Pyro4.Proxy(uri)
        remote.create_directory(directory_name, self.path, files)
    
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
        uri = "PYRO:DirectoriesManager@"+self.__ip+":8010"
        remote = Pyro4.Proxy(uri)
        remote.delete_directory(directory_name, self.path, files)
    
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
            if len(file.split(directory_name))>1 and len(file.split(directory_name)[1].split("/"))==2 and file != directory_name:
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
                
        uri = "PYRO:FilesManager@"+self.__ip+":8011"
        remote = Pyro4.Proxy(uri)
        first = True
        while True:
            bytes_recieved = socket_client.recv(self.__buffer)
            remote.upload(file_name, read_mode, bytes_recieved, first)
            if first:
                first = False    
            if bytes_recieved == b'':
                break    
    
    def download_file(self, file_name: str, read_mode: str, socket_client: socket.socket):
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
        
        uri = "PYRO:FilesManager@"+self.__ip+":8011"
        remote = Pyro4.Proxy(uri)
        while True:
            bytes_read = remote.download(file_name, read_mode)

            if bytes_read == b'':
                break 
            socket_client.send(bytes_read)
        
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
        uri = "PYRO:FilesManager@"+self.__ip+":8011"
        remote = Pyro4.Proxy(uri)
        print(self.route_path)
        print(self.path_default)
        print(file_name)
        remote.delete(self.path_default + self.route_path + file_name)
    
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
     
    def server_download(self):
        Pyro4.Daemon.serveSimple(
    {
       RecvBytesforDownload : "RecvBytesforDownload"
    },
    host=self.__ip,
    port=8014,
    ns=False)
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
                uri = "PYRO:FilesManager@"+self.__ip+":8011"
                remote = Pyro4.Proxy(uri)
                files = files.replace(name, new_name)
                remote.rename(name, new_name, self.path, files)
            elif file_list[i] == "D~~" + name + "/" or file_list[i] == "D~~" + name:
                uri = "PYRO:DirectoriesManager@"+self.__ip+":8010"
                remote = Pyro4.Proxy(uri)
                files = files.replace(name, new_name)
                remote.change_name_directory(self.route_path_default + name, self.route_path_default + new_name, self.path, files)
       
        
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
                uri = "PYRO:FilesManager@"+self.__ip+":8011"
                remote = Pyro4.Proxy(uri)
                return remote.state(self.route_path_default + file_name)
            elif file_list[i] == "D~~" + file_name + "/" or file_list[i] == "D~~" + file_name:
                uri = "PYRO:DirectoriesManager@"+self.__ip+":8010"
                remote = Pyro4.Proxy(uri)
                return remote.state_directory(self.route_path_default + file_name)
        return None
