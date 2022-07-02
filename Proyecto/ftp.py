from random import Random
import socket
from threading import Thread
import time
import sys
from tqdm import tqdm
from directory_manager import Directory_Manager
from Accessories.return_codes import Return_Codes
from Accessories.log import Log
from Accessories.help import Help_Commands

class ServerFTP(Thread):
    def __init__(self, connection, address, ip, port, log: Log, path, directory_manager: Directory_Manager):
        Thread.__init__(self)
        self.__ip = ip
        self.__port = port
        self.__buffer = 1024
        
        self.control_connection = connection
        self.control_address = address

        self.data_address = None
        self.data_connection = None
        
        self.server_connection = None
        self.server_address = None
        
        self.pasive = False
        self.mode = 'S'
        self.type = 'A N'
        self.stru = 'F'
        self.is_anonymous = False
        self.path = path + "/root/"
        self.original_path = path + "/root/"
        
        self.__off = False
        self.__path_db = path + "/Reports/database.db"
        self.__user = None
        self.__password = None
        
        self.log = log
        self.directory_manager = directory_manager

    '''
        Publics
    '''
    def start(self):
        self.__welcome_message()
        
        while True:
            if self.__off:
                break
            
            self.log.LogMessageServer("Waiting instructions \n")
            try:
                data = self.__receive()
                data = data.decode('utf-8',errors='ignore')         
            except socket.error as err:
                if str(err) == 'timed out':
                    self.__close()
                    break

            data = str(data).replace("b'", '')
            data = data.replace("\\r\\n", '')
            data = data.replace("\r\n", '')
            
            self.log.LogMessageServer("Received instruction: {0}\n".format(data))

            data_arr = data.split(' ')

            cmd = data_arr[0]
            
            #Login
            if "USER" in cmd:
                self.user_command(data)
            elif "PASS" in cmd:
                self.pass_command(data)
            elif "CWD" in cmd:
                self.cwd_command(data)
            elif "CDUP" in cmd:
                self.cdup_command()
            
            #Logout
            elif "REIN" in cmd:
                self.rein_command()
            elif "QUIT" in cmd:
                self.quit_command()
            
            #Transfer parameters
            elif "PORT" in cmd:
                self.port_command(data)
            elif "PASV" in cmd:
                self.pasv_command()
            elif "MODE" in cmd:
                self.mode_command(data)
            elif "TYPE" in cmd:
                self.type_command(data)
            elif "STRU" in cmd:
                self.stru_command()

            #File action commands
            elif "STOR" in cmd:
                self.stor_command(data)
            elif "STOU" in cmd:
                self.stou_command(data)
            elif "RETR" in cmd:
                self.retr_command(data)
            elif "LIST" in cmd:
                self.list_command(data)
            elif "NLST" in cmd:
                self.nlst_command(data)
            elif "APPE" in cmd:
                self.appe_command(data)
            elif "RNFR" in cmd:
                self.rnfr_command(data)
            elif "RNTO" in cmd:
                self.rnto_command(data)
            elif "DELE" in cmd:
                self.dele_command(data)
            elif "RMD" in cmd:
                self.rmd_command(data)
            elif "MKD" in cmd:
                self.mkd_command(data)
            elif "PWD" in cmd:
                self.pwd_command(data)
            elif "ABOR" in cmd:
                self.abor_command()

            #Informational commands
            elif "SYST" in cmd:
                self.syst_command()
            elif "HELP" in cmd:
                self.help_command(data)

            #Miscellaneous commands
            elif "NOOP" in cmd:
                self.noop_command()
            elif len(data) != 0:
                self.command_not_found()
            else:
                self.quit_command()

    '''
        Privates
    '''
    def __send_data(self, data):
        self.data_connection.send(data)
        
    def __send_control(self, control):
        self.control_connection.send(control)
    
    def __open_data_connection(self):
        try:
            self.data_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.pasive:
                self.data_connection, self.data_address = self.server_connection.accept()
                self.log.LogWarning(f'Conexion de datos aceptada en {self.data_address}')
            else:
                self.data_connection.connect(self.data_address)
                self.log.LogWarning(f'Conectando a {self.data_address}')
        except socket.error as err:
            self.log.LogError(self.control_address[0], self.control_address[1], err)
        
    def __close_data_connection(self):
        try:
            self.data_connection.close( )
            if self.pasive:
                self.data_connection.close( )
        except socket.error as err:
            self.log.LogError(self.control_address[0], self.control_address[1],err)
    
    def __welcome_message(self):
        self.__send_control(Return_Codes.Code_220().encode())
        
    def __receive(self):
        res = self.control_connection.recv(self.__buffer)
        return res
    
    def __close(self):
        self.__off = True
        self.control_connection.close()

    def __has_access(self, file : str):
        if not self.is_anonymous and file.find("anonymous") == -1:
            return True
        if self.is_anonymous and file.find("anonymous") != -1:
            return True
        return False
            
    def __to_list_item(self,fname : str):
        st=self.directory_manager.stat(fname)
        fullmode='rwxrwxrwx'
        mode=''
        for i in range(9):
            mode+=((st.st_mode>>(8-i))&1) and fullmode[i] or '-'
        d=(self.directory_manager.is_directory(fname)) and 'd' or '-'
        ftime=time.strftime(' %b %d %H:%M ', time.gmtime(st.st_mtime))
        return d+mode+' 1 user group '+str(st.st_size)+ftime+self.directory_manager.basename(fname)+'\r\n'


    '''
        Commands
    '''
    '''
        Login
    '''
    def user_command(self, data):
        u = data.split(" ")[1]
        users = ""
        if u == "anonymous\r\n" or u == "anonymous":
            self.is_anonymous = True
            self.__user = "anonymous"
            self.path += "anonymous/"
            self.__send_control(Return_Codes.Code_230().encode())
            self.log.LogOk(self.control_address[0], self.control_address[1], "Usuario Anonymous conectado.")
        else:
            with open(self.__path_db, 'rb') as f:
                while True:
                    bytes_read = f.read()
                    if bytes_read == b'':
                        break
                    else:
                        users+=str(bytes_read)
            users = str(users).replace("b'", '')
            users = str(users).replace("'", '')
            users = users.split("\\r\\n****\\r\\n")
            
            accepted = False
            for i in range(1,len(users)-1,3):
                if str(users[i])==str(u):
                    self.__user = users[i]
                    self.__password = users[i+1]
                    accepted = True
            if accepted:
                self.__send_control(Return_Codes.Code_331(u).encode())
                self.log.LogOk(self.control_address[0], self.control_address[1], f"Usuario {u} necesita insertar contrasenna.")
            else:
                self.__send_control(Return_Codes.Code_332().encode())
                self.log.LogError(self.control_address[0], self.control_address[1], f"Usuario {u} no existe.")

    def pass_command(self, data):
        if self.__user == None:
            self.__send_control(Return_Codes.Code_530().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"Necesita utilizar el comando USER antes.")
            return
        line = data.split(" ")
        if len(line) != 2:
            self.__send_control(Return_Codes.Code_501().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"Comando incorrecto.")
            return
        p = line[1] #password 
        if p == self.__password:
            self.__password = None
            self.__send_control(Return_Codes.Code_230().encode())
            self.log.LogOk(self.control_address[0], self.control_address[1], f"Usuario {self.__user} conectado.")
        else:
            self.__send_control(Return_Codes.Code_332().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"La contrasenna del usuario {self.__user} no es correcta.")

    def cwd_command(self, data):
        if self.__user == None:
            self.__send_control(Return_Codes.Code_530().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"Necesita acceso para cambiar de directorio")
            return
        names = data.split(" ")
        pathname = ""
        for i in range(1,len(names)):
            if i == len(names) - 1:
                pathname += str(names[i])
            else:
                pathname += str(names[i]) + " "
        try:     
            if pathname.__contains__("/"):
                pathname = pathname + "/"
            else:
                pathname = self.path + pathname + "/"
            
            if not self.directory_manager.is_directory(pathname):
                self.__send_control(Return_Codes.Code_550().encode())
                self.log.LogError(self.control_address[0], self.control_address[1], f"La ruta {pathname} no existe.")
                return
            
            if not self.is_anonymous and pathname.find("root") != -1:
                self.directory_manager.change_directory(pathname)
                self.path = pathname
            elif self.is_anonymous and pathname.find("anonymous") != -1:
                self.directory_manager.change_directory(pathname)
                self.path = pathname
            else:
                self.__send_control(Return_Codes.Code_550().encode())
                self.log.LogError(self.control_address[0], self.control_address[1], f"El usuario {self.__user} no tiene acceso a la ruta {pathname}.")
                return
            
            self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario {self.__user} accedio al directorio {self.directory_manager.route_path}.") 
            self.__send_control(Return_Codes.Code_250().encode())

        # Caching the exception     
        except OSError as error: 
            self.log.LogError(self.control_address[0], self.control_address[1], f"Algo salio mal para el usuario {self.__user}. Excepcion- {error}.")
            self.__send_control(Return_Codes.Code_550().encode())

    def cdup_command(self):
        if self.__user == None:
            self.__send_control(Return_Codes.Code_530().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"Necesita acceso para cambiar de directorio.")
            return
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
            if not self.directory_manager.is_directory(pathname):
                self.__send_control(Return_Codes.Code_550().encode())
                self.log.LogError(self.control_address[0], self.control_address[1], f"La ruta {pathname} no existe.")
                return
            
            if not self.is_anonymous and pathname.find("root") != -1:
                self.directory_manager.change_directory(pathname + "/")
                self.path = pathname + "/"
            elif self.is_anonymous and pathname.find("anonymous") != -1:
                self.directory_manager.change_directory(pathname + "/")
                self.path = pathname + "/"
            else:
                self.log.LogError(self.control_address[0], self.control_address[1], f"El usuario {self.__user} no tiene acceso al directorio {pathname}.")
                self.__send_control(Return_Codes.Code_550().encode())
                return
            self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario {self.__user} entro al directorio {self.directory_manager.route_path}.")
            self.__send_control(Return_Codes.Code_200().encode() )

        # Caching the exception     
        except OSError as error:
            self.log.LogError(self.control_address[0], self.control_address[1], f"Algo salio mal para el usuario {self.__user}. Excepcion- {error}.")
            self.__send_control(Return_Codes.Code_550().encode())


    '''
        Logout
    '''
    def rein_command(self, data):
        self.data_address = None
        self.data_connection = None

        self.mode = 'S'
        self.type = 'A N'
        self.stru = 'F'
        self.is_anonymous = False
        self.path = self.original_path
        self.__fd_rename = None
        
        try:
            time_stop = int(data.split(' ')[1])
            self.__send_control(Return_Codes.Code_120(time_stop).encode())
            self.log.LogWarning(self.control_address[0], self.control_address[1], f"El servicio se reinicira en {time_stop} minutos.")
            time.sleep(time_stop * 60)
        except:
            self.__send_control(Return_Codes.Code_220().encode())
            self.log.LogOk(self.control_address[0], self.control_address[1], f"El servicio se reinicio.")
        
    def quit_command(self):
        self.__send_control(Return_Codes.Code_221().encode())
        self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha cerrado su sesion.")
        self.__close()


    '''
        Transfer parameters
    '''
    def port_command(self, data):
        if self.__user == None:
            self.__send_control(Return_Codes.Code_530().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"Necesita acceso para solicitar el puerto.")
            return
        cmd_addr = data.split(" ")
        cmd_ip_port = cmd_addr[1].split(",")

        if self.pasive:
            self.server_connection.close()
            self.pasive = False
        
        ip = ".".join(str(x) for x in cmd_ip_port[0:4])
        port = cmd_ip_port[-2:]
        port =  int(port[0])*256 + int(port[1])
        self.data_address = (ip, port)
        self.__send_control(Return_Codes.Code_200().encode())

    def pasv_command(self):
        if self.__user == None:
            self.__send_control(Return_Codes.Code_530().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"Necesita acceso para cambiar al modo pasivo.")
            return
        self.pasive = True
        self.server_connection = socket.socket()
        self.server_connection.bind((self.control_connection.getsockname()[0], 0))
        self.server_connection.listen(5)
        self.__send_control(Return_Codes.Code_227(self.control_connection.getsockname( )).encode())
        self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha activado el modo pasivo.")

    def mode_command(self, data):
        if self.__user == None:
            self.__send_control(Return_Codes.Code_530().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"Necesita acceso para cambiar de modo.")
            return
        mode = data.split(" ")[1]
        if mode != 'S' and mode != 'B' and mode != 'C':
            self.__send_control(Return_Codes.Code_501().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha insertado argumentos incorrectos para la funcion MODE.")
            return
        self.mode = mode
        self.__send_control(Return_Codes.Code_200().encode())
        self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha activado el modo {self.mode}.")

    def type_command(self,data):
        if self.__user == None:
            self.__send_control(Return_Codes.Code_530().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"Necesita acceso para cambiar de tipo.")
            return
        type_list = data.split(' ')
        
        if len(type_list) == 2:
            type = type_list[1]
        else:
            type = type_list[1] + " " + type_list[2]

        if type_list[1] != "I" and type_list[1] != "L" and type_list[1] != "A" and type_list[1] != "E":
            self.__send_control(Return_Codes.Code_501().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha insertado argumentos incorrectos para la funcion TYPE.")
            return
        elif len(type_list) == 3 and type_list[1] != "I":
            self.__send_control(Return_Codes.Code_501().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha insertado argumentos incorrectos para la funcion TYPE.")
            return
        elif len(type_list) == 4:
            #Bug con el número de bytes
            if type_list[1] == "L" and type_list[2] != 123:
                self.__send_control(Return_Codes.Code_501().encode())
                self.log.LogError(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha insertado argumentos incorrectos para la funcion TYPE.")
                return
            elif type_list[1] == "A" or type_list[1] == "E" and type_list[2] != "N" and type_list[2] != "T" and type_list[2] != "C":
                self.__send_control(Return_Codes.Code_501().encode())
                self.log.LogError(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha insertado argumentos incorrectos para la funcion TYPE.")
                return
        self.type = type
        self.__send_control(Return_Codes.Code_200().encode())
        self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha activado el tipo {self.type}.")

    def stru_command(self, data):
        if self.__user == None:
            self.__send_control(Return_Codes.Code_530().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"Necesita acceso para cambiar de estructura.")
            return
        stru = data.split(" ")[1]
        if stru != 'F' and stru != 'R' and stru != 'P':
            self.__send_control(Return_Codes.Code_501().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha insertado argumentos incorrectos para la funcion STRU.")
            return
        self.stru = stru
        self.__send_control(Return_Codes.Code_200().encode())
        self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha activado el tipo {self.type}.")


    '''
        File action commands
    '''
    def stor_command(self, data):
        if self.__user == None:
            self.__send_control(Return_Codes.Code_530().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"Necesita acceso para subir el acrhivo.")
            return
        
        names = data.split(" ")
        filename = ""
        for i in range(1,len(names)):
            if i == len(names) - 1:
                filename += str(names[i])
            else:
                filename += str(names[i]) + " "
        
        self.log.LogWarning(f"Subiendo archivo... {filename}", self.control_address[0], self.control_address[1])

        self.__send_control(Return_Codes.Code_150().encode())
        self.__open_data_connection()

        readmode = 'w+b' if  self.type == 'I' else 'w'
        try:
            self.directory_manager.upload_file(filename, readmode, self.data_connection) 
            
            self.__send_control(Return_Codes.Code_226().encode())
            self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha subido el archivo {filename}.")
        except OSError as error:
            self.log.LogError(self.control_address[0], self.control_address[1], f"Algo salio mal para el usuario {self.__user}. Excepcion- {error}.")
            self.__send_control(Return_Codes.Code_550().encode())
        self.__close_data_connection()

    def stou_command(self, data):
        if self.__user == None:
            self.__send_control(Return_Codes.Code_530().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"acceso para subir el acrhivo.")
            return
        
        names = data.split(" ")
        filename = ""
        for i in range(1,len(names)):
            if i == len(names) - 1:
                filename += str(names[i])
            else:
                filename += str(names[i]) + " "
        
        random = Random()
        filename = str(int(10000000000 * random.random())) + filename
        
        self.log.LogWarning(f"Subiendo archivo... {filename}", self.control_address[0], self.control_address[1])

        self.__send_control(Return_Codes.Code_150().encode())
        self.__open_data_connection()

        readmode = 'w+b' if  self.type == 'I' else 'w'

        try:
            self.directory_manager.upload_file(filename, readmode, self.data_connection) 
            
            self.__send_control(Return_Codes.Code_226().encode())
            self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha subido el archivo {filename}.")
        except OSError as error:
            self.log.LogError(self.control_address[0], self.control_address[1], f"Algo salio mal para el usuario {self.__user}. Excepcion- {error}.")
            self.__send_control(Return_Codes.Code_550().encode())
        self.__close_data_connection()

    def retr_command(self,data):
        if self.__user == None:
            self.__send_control(Return_Codes.Code_530().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], "Necesita acceso para descargar un archivo.")
            return
        names = data.split(" ")
        filename = ""
        for i in range(1,len(names)):
            if i == len(names) - 1:
                filename += str(names[i])
            else:
                filename += str(names[i]) + " "
        
        self.log.LogWarning(f"Descargando archivo... {filename}", self.control_address[0], self.control_address[1])

        try:
            filesize = self.directory_manager.get_file_size(filename)
        except OSError as error:
            self.log.LogError(self.control_address[0], self.control_address[1], f"Algo salio mal para el usuario {self.__user}. Excepcion- {error}.")
            self.__send_control(Return_Codes.Code_550().encode())
            return

        self.__send_control(Return_Codes.Code_150().encode())
        self.__open_data_connection()

        readmode = 'rb' if  self.type == 'I' else 'r'

        try:
            progress = tqdm(range(filesize), desc="Descargando...", unit="B", unit_scale=True, unit_divisor=self.__buffer)
            self.directory_manager.download_file(filename, readmode, self.data_connection, progress)
            
            self.__send_control(Return_Codes.Code_226().encode())
            self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha descargado el archivo {filename}.")
                
        except OSError as error:
            self.log.LogError(self.control_address[0], self.control_address[1], f"Algo salio mal para el usuario {self.__user}. Excepcion- {error}.")
            self.__send_control(Return_Codes.Code_550().encode())
        self.data_connection.close()
        
    def list_command(self, data):
        if self.__user == None:
            self.__send_control(Return_Codes.Code_530().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"Necesita acceso para listar un directorio.")
            return
        data = str(data).replace("LIST ", "")
        data = str(data).replace("LIST", "")
        if len(data) != 0:
            path = data
        else:
            path = self.path
        
        self.__send_control(Return_Codes.Code_150().encode())
        self.__open_data_connection()
        
        if not self.directory_manager.is_directory(path):
            self.__send_control(Return_Codes.Code_550().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"La ruta {path} no existe.")
            return
        l = self.directory_manager.list_directory(path)
        for t in l:
            if self.__has_access(t):
                k = self.__to_list_item(t)
                self.__send_data(k.encode())
        self.__close_data_connection()
        self.__send_control(Return_Codes.Code_226().encode())
        self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha listado el directorio {path}.")

    def nlst_command(self, data):
        data = str(data).replace("NLIST ", "")
        data = str(data).replace("NLIST", "")
        self.list_command(data)

    def appe_command(self, data):
        if self.__user == None:
            self.__send_control(Return_Codes.Code_530().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"Necesita acceso para añadir informacion a un archivo.")
            return
        
        names = data.split(" ")
        filename = ""
        for i in range(1,len(names)):
            if i == len(names) - 1:
                filename += str(names[i])
            else:
                filename += str(names[i]) + " "
        
        self.log.LogWarning(f"Modificando archivo... {filename}", self.control_address[0], self.control_address[1])

        self.__send_control(Return_Codes.Code_150().encode())
        self.__open_data_connection()

        try:
            with self.directory_manager.open_file(filename, 'a') as f:
                
                while True:
                    bytes_recieved = self.data_connection.recv(self.__buffer)
                    
                    if not bytes_recieved: break

                    f.write(bytes_recieved)
            
            self.__send_control(Return_Codes.Code_226().encode())
            self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha modificado el archivo {filename}.")
        except OSError as error:
            self.log.LogError(self.control_address[0], self.control_address[1], f"Algo salio mal para el usuario {self.__user}. Excepcion- {error}.")
            self.__send_control(Return_Codes.Code_550().encode())
        self.__close_data_connection()
        
    def rnfr_command(self, data):
        if self.__user == None:
            self.__send_control(Return_Codes.Code_530().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"Necesita acceso para solicitar cambiar el nombre a un archivo/directorio.")
            return
        
        pathname = self.path
        names = data.split(" ")
        for i in range(1,len(names)):
            if i == len(names) - 1:
                pathname += str(names[i])
            else:
                pathname += str(names[i]) + " "
        if not self.directory_manager.is_file(pathname) and not self.directory_manager.is_directory(pathname):
            self.__send_control(Return_Codes.Code_550().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"La ruta {pathname} no existe.")
            return
        self.__fd_rename = pathname
        self.__send_control(Return_Codes.Code_350().encode())

    def rnto_command(self, data):
        if self.__user == None:
            self.__send_control(Return_Codes.Code_530().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"Necesita acceso para renombrar el archivo/directorio.")
            return
        if self.__fd_rename == None:
            self.__send_control(Return_Codes.Code_553().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"No existe ruta a la que se deba cambiar el nombre.")
            return
        
        pathname = self.path
        names = data.split(" ")
        for i in range(1,len(names)):
            if i == len(names) - 1:
                pathname += str(names[i])
            else:
                pathname += str(names[i]) + " "
        try:
            if not self.directory_manager.is_file(self.__fd_rename) and not self.directory_manager.is_directory(self.__fd_rename):
                self.__send_control(Return_Codes.Code_550().encode())
                self.log.LogError(self.control_address[0], self.control_address[1], f"El archivo/directorio {self.__fd_rename} no existe.")
                return
            self.directory_manager.rename(self.__fd_rename, pathname)
            self.__send_control(Return_Codes.Code_250().encode())
            self.log.LogOk(self.control_address[0], self.control_address[1], f"El usurio {self.__user} ha renombrado satisfactoriamente el archivo {self.__fd_rename} a {pathname}.")
            self.__fd_rename = None

        # Caching the exception     
        except OSError as error: 
            self.log.LogError(self.control_address[0], self.control_address[1], f"Algo salio mal para el usuario {self.__user}. Excepcion- {error}.")
            self.__send_control(Return_Codes.Code_550().encode())

    def dele_command(self, data):
        if self.__user == None:
            self.__send_control(Return_Codes.Code_530().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"Necesita acceso para eliminar el archivo.")
            return
        pathname = self.path
        names = data.split(" ")
        for i in range(1,len(names)):
            if i == len(names) - 1:
                pathname += str(names[i])
            else:
                pathname += str(names[i]) + " "
        if not self.directory_manager.is_file(pathname):
            self.__send_control(Return_Codes.Code_550().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"El archivo {pathname} no existe.")
            return
        try: 
            self.directory_manager.delete_file(pathname)
            self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha eliminado el archivo {pathname}.")
            self.__send_control(Return_Codes.Code_250().encode())
        except OSError as error:
            self.log.LogError(self.control_address[0], self.control_address[1], f"Algo salio mal para el usuario {self.__user}. Excepcion- {error}.")
            self.__send_control(Return_Codes.Code_550().encode())

    def rmd_command(self, data):
        if self.__user == None:
            self.__send_control(Return_Codes.Code_530().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"Necesita acceso para eliminar el directorio.")
            return
        pathname = self.path
        names = data.split(" ")
        for i in range(1,len(names)):
            if i == len(names) - 1:
                pathname += str(names[i])
            else:
                pathname += str(names[i]) + " "
        
        try: 
            if not self.directory_manager.is_directory(pathname):
                self.__send_control(Return_Codes.Code_550().encode())
                self.log.LogError(self.control_address[0], self.control_address[1], f"El directorio {pathname} no existe.")
                return
            self.directory_manager.delete_directory(pathname)
            self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha eliminado el directorio {pathname}.")
            self.__send_control(Return_Codes.Code_250().encode())

        # Caching the exception     
        except OSError as error:
            self.log.LogError(self.control_address[0], self.control_address[1], f"Algo salio mal para el usuario {self.__user}. Excepcion- {error}.")
            self.__send_control(Return_Codes.Code_550().encode())

    def mkd_command(self, data):
        if self.__user == None:
            self.__send_control(Return_Codes.Code_530().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"Necesita acceso para crear el directorio/archivo.")
            return
        pathname = self.path
        names = data.split(" ")
        for i in range(1,len(names)):
            if i == len(names) - 1:
                pathname += str(names[i])
            else:
                pathname += str(names[i]) + " "

        try:
            if self.directory_manager.is_directory(pathname):
                self.__send_control(Return_Codes.Code_550().encode())
                self.log.LogError(self.control_address[0], self.control_address[1], f"Ya existe {pathname} como ruta.")
                return
            self.directory_manager.create_directory(pathname)
            self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha creado la ruta {pathname}.")
            self.__send_control(Return_Codes.Code_257(pathname).encode())

        # Caching the exception     
        except OSError as error: 
            self.log.LogError(self.control_address[0], self.control_address[1], f"Algo salio mal para el usuario {self.__user}. Excepcion- {error}.")
            self.__send_control(Return_Codes.Code_550().encode())

    def pwd_command(self, data):
        self.__send_control(Return_Codes.Code_257(self.path).encode())
        self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario {self.__user} ha mostrado el contenido del directorio {self.path}.")

    def abor_command(self):
        try:
            self.data_connection.close()
            self.__send_control(Return_Codes.Code_226(self.path).encode())
        except:
            self.__send_control(Return_Codes.Code_426(self.path).encode())
            self.__send_control(Return_Codes.Code_226(self.path).encode())
        self.log.LogWarning(self.control_address[0], self.control_address[1], f"El usuario {self.__user} cerro la conexion de datos.")


    '''
        Informational commands
    '''
    def syst_command(self):
        self.__send_control(Return_Codes.Code_215(sys.platform).encode())
        self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario {self.__user} solicito la informacion del sistema: {sys.platform}.")

    def help_command(self, data):
        data_array = str(data).split(' ')
        
        if(len(data_array) == 2):
            cmd = data_array[1]
    
            #Login
            if "USER" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.USER()).encode())
            elif "PASS" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.PASS()).encode())
            elif "CWD" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.CWD()).encode())
            elif "CDUP" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.CDUP()).encode())
            
            #Logout
            elif "REIN" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.REIN()).encode())
            elif "QUIT" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.QUIT()).encode())
            
            #Transfer parameters
            elif "PORT" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.PORT()).encode())
            elif "PASV" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.PASS()).encode())
            elif "MODE" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.MODE()).encode())
            elif "TYPE" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.TYPE()).encode())
            elif "STRU" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.STRU()).encode())

            #File action commands
            elif "STOR" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.STOR()).encode())
            elif "STOU" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.STOU()).encode())
            elif "RETR" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.RETR()).encode())
            elif "LIST" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.LIST()).encode())
            elif "NLST" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.NLST()).encode())
            elif "APPE" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.APPE()).encode())
            elif "RNFR" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.RNFR()).encode())
            elif "RNTO" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.RNTO()).encode())
            elif "DELE" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.DELE()).encode())
            elif "RMD" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.RMD()).encode())
            elif "MKD" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.MKD()).encode())
            elif "PWD" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.PWD()).encode())

            #Informational commands
            elif "SYST" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.SYST()).encode())
            elif "HELP" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.HELP()).encode())

            #Miscellaneous commands
            elif "NOOP" in cmd:
                self.__send_control(Return_Codes.Code_211(Help_Commands.NOOP()).encode())
            else:
                self.command_not_found()
            self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario ha solicitado ayuda.")
        elif(len(data_array) == 1):
            self.__send_control(Return_Codes.Code_214("El comando reconocido").encode())
            self.__send_control(Help_Commands.ALL().encode())
            self.__send_control(Return_Codes.Code_214("Help OK").encode())
            self.log.LogOk(self.control_address[0], self.control_address[1], f"El usuario ha solicitado ayuda.")
        else:
            self.__send_control(Return_Codes.Code_501().encode())
            self.log.LogError(self.control_address[0], self.control_address[1], f"El usuario ha insertado argumentos incorrectos para la funcion HELP.")

    '''
        Miscellaneous commands
    '''
    def noop_command(self):
        self.__send_control(Return_Codes.Code_200().encode())

    def command_not_found(self):
        self.__send_control(Return_Codes.Code_500().encode())
        self.log.LogError(self.control_address[0], self.control_address[1], f"El usuario ha insertado un comando no reconocido.")