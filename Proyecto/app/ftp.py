from http.client import PRECONDITION_REQUIRED
from nturl2path import pathname2url
import socket
import os
import time
import sys
import tqdm
from return_codes import Return_Codes

class ServerFTP():
    def __init__(self, ip, port, buffer=1024):

        self.__ip = ip
        self.__port = port
        self.__buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn = None
        self.addr = None

        self.data_address = None
        self.datasock = None

        self.mode = 'S'
        self.type = 'A N'
        self.stru = 'F'
        self.is_anonymous = False
        self.path = os.getcwd() + "/root/"
        self.__fd_rename = None
    

    '''
        Connections
    '''
    def bind(self):
        self.socket.bind((self.__ip, self.__port))
        self.socket.listen(1)

    def accept(self):
        self.conn, self.addr = self.socket.accept()
        print('Connection accepted on {}'.format(self.addr).encode())

    def receive(self):
        res = self.conn.recv(self.__buffer)
        return res

    def welcome_message(self):
        self.conn.send(Return_Codes.Code_220().encode())


    '''
        Commands
    '''
    '''
        Login
    '''
    def user_command(self, data):
        u = data.split(" ")[1]
        if u == "anonymous\r\n" or u == "anonymous":
            self.is_anonymous = True
        self.conn.send(Return_Codes.Code_331(u).encode())

    def pass_command(self, data):
        # p = data.split(" ")[1] #password 
        #self.conn.send(Return_Codes.Code_332().encode())
        #self.conn.send(Return_Codes.Code_500().encode())
        self.conn.send(Return_Codes.Code_230().encode())

    def acct_command(self, data):
        None

    def cwd_command(self, data):
        list = data.split(" ")
        pathname = ""
        length = 0
        for path in list:
            if path != "CWD":
                pathname += path
            if len(list) > 2 and length + 1 < len(list) and length != 0:
                pathname += " "
            length+=1
        try:
            if pathname.__contains__("/"):
                self.path = pathname + "/"
            else:
                self.path = self.path + pathname + "/"
            os.chdir(self.path)
            
            print("The current directory is", os.getcwd()) 
            self.conn.send(Return_Codes.Code_200().encode())

        # Caching the exception     
        except: 
            print("Something wrong with specified directory. Exception- ", sys.exc_info())
            self.conn.send(Return_Codes.Code_550().encode())

    def cdup_command(self, data):
        paths = self.path.split('/')
        i = len(paths) - 1
        continue_delete = True
        while continue_delete:
            if paths[i] == '':
                paths.pop(i)
                i -= 1
            elif paths[i] != '':
                paths.pop(i)
                continue_delete = False
        pathname = "/"
        for p in paths:
            if p != '':
                pathname = pathname + p + "/"
        try: 
            self.path = pathname + "/"
            os.chdir(pathname + "/")
            print("The current directory is", os.getcwd()) 
            self.conn.send(Return_Codes.Code_200().encode() )

        # Caching the exception     
        except: 
            print("Something wrong with specified directory. Exception- ", sys.exc_info())
            self.conn.send(Return_Codes.Code_550().encode())

    def smnt_command(self):
        None


    '''
        Logout
    '''
    def rein_command(self, data):
        self.data_address = None
        self.datasock = None

        self.mode = 'S'
        self.type = 'A N'
        self.stru = 'F'
        self.is_anonymous = False
        self.path = os.getcwd() + "/root/"
        self.__fd_rename = None
        
        try:
            time_stop = int(data.split(' ')[1])
            self.conn.send(Return_Codes.Code_120().encode() )
            time.sleep(time_stop * 60)
        except:
            self.conn.send(Return_Codes.Code_220().encode() )
        
    def quit_command(self):
        self.conn.send(Return_Codes.Code_221().encode())
        self.__close()


    '''
        Transfer parameters
    '''
    def port_command(self, data):
        cmd_addr = data.split(" ")
        cmd_ip_port = cmd_addr[1].split(",")

        ip = ".".join(str(x) for x in cmd_ip_port[0:4])
        port = cmd_ip_port[-2:]
        port =  int(port[0])*256 + int(port[1])
        self.data_address = (ip, port)
        self.conn.send(Return_Codes.Code_200().encode())

    def pasv_command(self):     
        self.conn.send(Return_Codes.Code_227().encode())

    def mode_command(self, data):
        mode = data.split(" ")[1]
        if mode != 'S' and mode != 'B' and mode != 'C':
            self.conn.send(Return_Codes.Code_501().encode())
            return
        self.mode = mode
        self.conn.send(Return_Codes.Code_200().encode())

    def type_command(self,data):
        type_list = data.split(' ')
        
        if len(type_list) == 2:
            type = type_list[1]
        else:
            type = type_list[1] + " " + type_list[2]

        if type_list[1] != "I" and type_list[1] != "L" and type_list[1] != "A" and type_list[1] != "E":
            self.conn.send(Return_Codes.Code_501().encode())
            return
        elif len(type_list) == 2 and type_list[1] != "I":
            self.conn.send(Return_Codes.Code_501().encode())
            return
        elif len(type_list) == 3:
            if type_list[1] == "L" and type_list[2] != 123:
                self.conn.send(Return_Codes.Code_501().encode())
                return
            elif type_list[1] == "A" or type_list[1] == "E" and type_list[2] != "N" and type_list[2] != "T" and type_list[2] != "C":
                self.conn.send(Return_Codes.Code_501().encode())
                return
        self.type = type
        self.conn.send(Return_Codes.Code_200().encode())

    def stru_command(self, data):
        stru = data.split(" ")[1]
        if stru != 'F' and stru != 'R' and stru != 'P':
            self.conn.send(Return_Codes.Code_501().encode())
            return
        self.stru = stru
        self.conn.send(Return_Codes.Code_200().encode())


    '''
        File action commands
    '''
    def allo_command(self, data):
        self.conn.send(Return_Codes.Code_200().encode())

    def rest_command(self, data):
        None

    def stor_command(self, data):
        # str_size = struct.unpack("i", self.conn.recv(4))[0]

        # filename = self.conn.recv(str_size)
        filename = data.split(" ")[1]
        
        print('Upload file... ',filename)

        self.conn.send(Return_Codes.Code_150().encode())
        self.datasock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.datasock.connect(self.data_address)

        readmode = 'wb' if  self.mode == 'I' else 'w'

        try:
            with open(filename, readmode) as f:
                
                while True:
                    bytes_recieved = self.datasock.recv(self.__buffer)
                    
                    if not bytes_recieved: break

                    f.write(bytes_recieved)
            
            self.conn.send(Return_Codes.Code_226().encode())
        except:
            self.conn.send(Return_Codes.Code_550().encode())
        self.datasock.close()
        print('Upload Successful\n')

    def stou_command(self, data):
        None

    def retr_command(self,data):
        filename = data.split(" ")[1]
        
        print('Download file... ',filename)

        try:
            filesize = os.path.getsize(filename)
        except: 
            self.conn.send(Return_Codes.Code_550().encode())
            return

        progress = tqdm.tqdm(range(
            filesize), "Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)

        self.conn.send(Return_Codes.Code_150().encode())
        self.socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.datasock.connect(self.data_address)

        readmode = 'rb' if  self.mode == 'I' else 'r'

        try: 
            with open(filename, readmode) as f:

                for _ in progress:

                    bytes_read = f.read(self.__buffer)

                    if not bytes_read:
                        break
                    # self.conn.send('125 Ready data connection.\r\n'.encode())
                    # self.conn.sendall(bytes_read)
                    self.datasock.send(bytes_read)
                    progress.update(len(bytes_read))
            self.conn.send(Return_Codes.Code_226().encode())
                
        except:
            self.conn.send(Return_Codes.Code_550().encode())
        self.datasock.close()
        
    def list_command(self):
        self.conn.send(Return_Codes.Code_150().encode())
        self.datasock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.datasock.connect(self.data_address)

        if self.is_anonymous and self.path.find("anonymous/") == -1:
            self.path = self.path + "anonymous/"
            l = os.listdir(self.path)
        else:
            l = os.listdir(self.path)

        for t in l:
            if self.__has_access(t):
                k = self.__to_list_item(t, self.path)
                self.datasock.send(k.encode())
            
        self.datasock.close()
        self.conn.send(Return_Codes.Code_226().encode())

    def nlst_command(self):
        None

    def appe_command(self, data):
        None

    def rnfr_command(self, data):
        path_name = str(data).split(" ")
        path_name.remove("RNFR")
        
        pathname = self.path
        i = 0
        for path in path_name:
            if i <= len(path_name)-2:
                pathname = pathname + path + " "
            else:
                pathname = pathname + path
            i+=1
        self.__fd_rename = pathname
        self.conn.send(Return_Codes.Code_350().encode())

    def rnto_command(self, data):
        path_name = str(data).split(" ")
        path_name.remove("RNTO")
        
        pathname = self.path
        i = 0
        for path in path_name:
            if i <= len(path_name)-2:
                pathname = pathname + path + " "
            else:
                pathname = pathname + path
            i+=1
        try:
            os.rename(self.__fd_rename, pathname)
            self.__fd_rename = None
            print("The current directory is", os.getcwd()) 
            self.conn.send(Return_Codes.Code_250().encode())

        # Caching the exception     
        except: 
            print("Something wrong with specified directory. Exception- ", sys.exc_info())
            self.conn.send(Return_Codes.Code_550().encode())

    def dele_command(self, data):
        path_name = str(data).split(" ")
        path_name.remove("DELE")
        
        pathname = self.path
        i = 0
        for path in path_name:
            if i <= len(path_name)-2:
                pathname = pathname + path + " "
            else:
                pathname = pathname + path
            i+=1
        try: 
            os.rmdir(pathname)
            print("The current directory is", os.getcwd()) 
            self.conn.send(Return_Codes.Code_250().encode())

        # Caching the exception     
        except: 
            try: 
                os.remove(pathname)
                print("The current directory is", os.getcwd()) 
                self.conn.send(Return_Codes.Code_250().encode())
            except:
                print("Something wrong with specified directory. Exception- ", sys.exc_info())
                self.conn.send(Return_Codes.Code_550().encode())

    def rmd_command(self, data):
        path_name = str(data).split(" ")
        path_name.remove("RMD")
        
        pathname = self.path
        i = 0
        for path in path_name:
            if i <= len(path_name)-2:
                pathname = pathname + path + " "
            else:
                pathname = pathname + path
            i+=1
        
        try: 
            os.rmdir(pathname)
            print("The current directory is", os.getcwd()) 
            self.conn.send(Return_Codes.Code_250().encode())

        # Caching the exception     
        except: 
            print("Something wrong with specified directory. Exception- ", sys.exc_info())
            self.conn.send(Return_Codes.Code_550().encode())

    def mkd_command(self, data):
        path_name = str(data).split(" ")
        path_name.remove("MKD")
        
        pathname = self.path
        i = 0
        for path in path_name:
            if i <= len(path_name)-2:
                pathname = pathname + path + " "
            else:
                pathname = pathname + path
            i+=1

        try:
            os.mkdir(pathname)
            print("The current directory is", os.getcwd()) 
            self.conn.send(Return_Codes.Code_257(pathname).encode())

        # Caching the exception     
        except: 
            print("Something wrong with specified directory. Exception- ", sys.exc_info())
            self.conn.send(Return_Codes.Code_550().encode())

    def pwd_command(self, data):
        self.conn.send(Return_Codes.Code_257(self.path).encode())

    def abor_command(self):
        try:
            self.datasock.close()
            self.conn.send(Return_Codes.Code_226(self.path).encode())
        except:
            self.conn.send(Return_Codes.Code_426(self.path).encode())
            self.conn.send(Return_Codes.Code_226(self.path).encode())


    '''
        Informational commands
    '''
    def syst_command(self):
        self.conn.send(Return_Codes.Code_215("ST").encode())

    def stat_command(self):
        None

    def help_command(self):
        None


    '''
        Miscellaneous commands
    '''
    def site_command(self):
        None

    def noop_command(self):
        self.conn.send(Return_Codes.Code_200().encode())

    def command_not_found(self):
        self.conn.send(Return_Codes.Code_500().encode())


    '''
        Privates
    '''
    def __close(self):
        self.conn.close()
        self.socket.close()

    def __has_access(self, file : str):
        if not self.is_anonymous and file.find("anonymous") != -1:
            return False
        return True
            
    def __to_list_item(self,fn, path = "./root"):
        st=os.stat(path + fn)
        fullmode='rwxrwxrwx'
        mode=''
        for i in range(9):
            mode+=((st.st_mode>>(8-i))&1) and fullmode[i] or '-'
        d=(os.path.isdir(path + fn)) and 'd' or '-'
        ftime=time.strftime(' %b %d %H:%M ', time.gmtime(st.st_mtime))
        return d+mode+' 1 user group '+str(st.st_size)+ftime+os.path.basename(path + fn)+'\r\n'