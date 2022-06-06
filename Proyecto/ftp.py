from http.client import PRECONDITION_REQUIRED
import socket
import os
import time
import sys
import tqdm

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

        self.mode = 'I'
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
        send = '220 connection started.\r\n'
        self.conn.send(send.encode())


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
        self.conn.send(('331 OK - {}.\r\n'.format(u)).encode())

    def pass_command(self, data):
        # p = data.split(" ")[1] #password 
        self.conn.send('230 OK.\r\n'.encode())

    def acct_command(self):
        self.conn.send('230 OK.\r\n'.encode())

    def cwd_command(self, data):
        list = data.split(" ")
        pathname = ""
        length = 0
        for path in list:
            if path != "CWD":
                pathname += path
                length += 1
            if len(list) > 2 and length + 1 < len(list) and length != 0:
                pathname += " "
        try:
            if pathname.__contains__("/"):
                self.path = pathname + "/"
            else:
                self.path = self.path + "/" + pathname + "/"
            os.chdir(self.path)
            
            print("The current directory is", os.getcwd()) 
            self.conn.send(('200 \"%s\" is current directory.\r\n' % os.getcwd()).encode() )

        # Caching the exception     
        except: 
            print("Something wrong with specified directory. Exception- ", sys.exc_info())
            self.conn.send(('550 \"{}\" Requested action not taken. File unavailable.\r\n'.format(os.getcwd()+"\\"+str(pathname))).encode() )

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
            self.conn.send(('200 \"%s\" is current directory.\r\n' % os.getcwd()).encode() )

        # Caching the exception     
        except: 
            print("Something wrong with specified directory. Exception- ", sys.exc_info())
            self.conn.send(('550 \"{}\" Requested action not taken. File unavailable.\r\n'.format(os.getcwd()+"/"+str(pathname))).encode() )

    def smnt_command(self):
        self.conn.send('230 OK.\r\n'.encode())


    '''
        Logout
    '''
    def rein_command(self):
        self.conn.send('230 OK.\r\n'.encode())

    def quit_command(self):
        self.conn.send('221 Goodbye.\r\n'.encode())
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
        send = '200 Port command successfull.\r\n'
        self.conn.send(send.encode())

    def pasv_command(self):     
        send = '227 passive mode activated. \r\n'
        self.conn.send(send.encode())

    def mode_command(self):
        self.conn.send('230 OK.\r\n'.encode())

    def type_command(self,data):
        self.mode = data.split(" ")
        send = '200 funcioned.\r\n'
        self.conn.send(send.encode())

    def stru_command(self):
        self.conn.send('230 OK.\r\n'.encode())


    '''
        File action commands
    '''
    def allo_command(self, data):
        self.conn.send('230 OK.\r\n'.encode())

    def rest_command(self, data):
        self.conn.send('230 OK.\r\n'.encode())

    def stor_command(self, data):
        # str_size = struct.unpack("i", self.conn.recv(4))[0]

        # filename = self.conn.recv(str_size)
        filename = data.split(" ")[1]
        
        print('Upload file... ',filename)

        self.conn.send('150 Opening data connection.\r\n'.encode())
        self.datasock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.datasock.connect(self.data_address)

        readmode = 'wb' if  self.mode == 'I' else 'w'

        try:
            with open(filename, readmode) as f:
                
                while True:
                    bytes_recieved = self.datasock.recv(self.__buffer)
                    
                    if not bytes_recieved: break

                    f.write(bytes_recieved)

            self.conn.send('226 Transfer complete.\r\n'.encode())        
        except:
            self.conn.send("550 can't access file .\r\n".encode())
        self.datasock.close()
        print('Upload Successful\n')

    def stou_command(self, data):
        self.conn.send('230 OK.\r\n'.encode())

    def retr_command(self,data):
        filename = data.split(" ")[1]
        
        print('Download file... ',filename)

        try:
            filesize = os.path.getsize(filename)
        except: 
            self.conn.send(("550 can't access file '{}'.\r\n").format(filename).encode())
            return

        progress = tqdm.tqdm(range(
            filesize), "Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)

        self.conn.send('150 Opening data connection.\r\n'.encode())
        self.socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.datasock.connect(self.data_address)
        
        print("paso")

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

                
        except:
            self.conn.send("550 can't access file: Permission denied.\r\n".encode())
        self.datasock.close()
        self.conn.send('226 Transfer complete.\r\n'.encode())

    def list_command(self):
        self.conn.send('150 Here comes the directory listing.\r\n'.encode())
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
                #self.conn.send('125 Ready open.\r\n'.encode())
                self.datasock.send(k.encode())
            
        self.datasock.close()
        self.conn.send('226 Directory send OK.\r\n'.encode())

    def nlst_command(self):
        self.conn.send('230 OK.\r\n'.encode())

    def appe_command(self, data):
        self.conn.send('230 OK.\r\n'.encode())

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
        self.__fd_rename = pathname
        self.conn.send('230 OK.\r\n'.encode())

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
        try:
            os.rename(self.__fd_rename, pathname)
            self.__fd_rename = None
            print("The current directory is", os.getcwd()) 
            self.conn.send('230 OK.\r\n'.encode())

        # Caching the exception     
        except: 
            print("Something wrong with specified directory. Exception- ", sys.exc_info())
            self.conn.send(('550 \"{}\" Requested action not taken. File unavailable.\r\n'.format(str(pathname))).encode() )
        self.conn.send('230 OK.\r\n'.encode())

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
        print(pathname)
        try: 
            os.rmdir(pathname)
            print("The current directory is", os.getcwd()) 
            self.conn.send('230 OK.\r\n'.encode())

        # Caching the exception     
        except: 
            print("Something wrong with specified directory. Exception- ", sys.exc_info())
            self.conn.send(('550 \"{}\" Requested action not taken. File unavailable.\r\n'.format(str(pathname))).encode() )

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
        
        try: 
            os.rmdir(pathname)
            print("The current directory is", os.getcwd()) 
            self.conn.send('230 OK.\r\n'.encode())

        # Caching the exception     
        except: 
            print("Something wrong with specified directory. Exception- ", sys.exc_info())
            self.conn.send(('550 \"{}\" Requested action not taken. File unavailable.\r\n'.format(str(pathname))).encode() )

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
        
        try: 
            os.mkdir(pathname)
            print("The current directory is", os.getcwd()) 
            self.conn.send('257 \"{}\" directory created.\r\n'.format(pathname).encode())

        # Caching the exception     
        except: 
            print("Something wrong with specified directory. Exception- ", sys.exc_info())
            self.conn.send(('550 \"{}\" Requested action not taken. File unavailable.\r\n'.format(str(pathname))).encode() )

    def pwd_command(self, data):
        self.conn.send(('257 \"%s\" is current directory.\r\n' % self.path).encode() )
        
        print("Successfully sent file listing \n")

    def abor_command(self, data):
        send = '225 abor command.\r\n'
        self.conn.send(send.encode())


    '''
        Informational commands
    '''
    def syst_command(self):
        self.conn.send('230 OK.\r\n'.encode())

    def stat_command(self):
        self.conn.send('230 OK.\r\n'.encode())

    def help_command(self):
        self.conn.send('230 OK.\r\n'.encode())


    '''
        Miscellaneous commands
    '''
    def site_command(self):
        self.conn.send('230 OK.\r\n'.encode())

    def noop_command(self):
        self.conn.send('230 OK.\r\n'.encode())

    def command_not_found(self):
        self.conn.send('500 Command Not Found.\r\n'.encode())


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