from pickle import TRUE
import socket
import os
import threading
import Pyro4
import time

from utils import get_proxy

@Pyro4.expose
class Listen(object):
    def update_predecesor(predecesor):
        node.predecessor=predecesor

    def update_sucesor(sucesor):
        node.successor=sucesor

    def update_fingetables():
        for i in range(0,8):
            id=pow(2,i)+node.id
            node.finger_table[id]=node.give_me_sucesor(id)

    def leave_message(id):
       node.node_control[id]=False

    def join_to_system(node_control_boss,node_list_boss):
        node.node_control=node_control_boss
        node.node_list=node_list_boss
    
    def assign_boss(ip_boss):
        node.ip_boss=ip_boss

    def assign_id():
      node.id=node.node_list.index(node.ip)

    def ping():
        return

    #def update_file_hash(keys,values):### Para Cargar archivos
         #for key in 


@Pyro4.expose
class ResultConnection(object):
    def give_me_nodos_encontrados(self):
        return node.NodosEncontrados

    def give_me_ip_boss(self):
        return node.ip

    def return_orden(self,message,ip_cliente,NodosEncontradosPorEl):
        if message=="Code #399#":
            if node.ip==node.ip_boss:
                node.NodosEncontrados.append(ip_cliente)
                node.NodosEncontrados.extend(NodosEncontradosPorEl)
                return 'Code #400#'
            elif node.ip_boss==None:
                node.NodosEncontrados.append(node.ip)
                node.NoSereLider=True
                return "Nodo aislado"
            else:
                return "Code #398#" 



@Pyro4.expose
class Node:
    def __init__(self, ip, path):
        self.id=None
        self.ip=ip
        self.files=list()  #se guardaran los archivos que esten almacenados en este nodo , mas alla que sea una replica . 
        self.files_system=dict()  #Aqui se guardara el hash del archivo y en que otros nodos esta
        self.predecessor=None
        self.successor=None
        self.finger_table=dict()
        self.ip_boss=None
        self.there_boss=False
        self.node_list=[]
        self.requests=[]  # aqui se guardan las requests de los clientes
        self.leader_calls=False
        self.stabilized_system=False
        self.finish_countdown=False
        self.NodosEncontrados=[]
        self.NoSereLider=False
        self.files_hash=dict()
        self.path=path
        self.node_control=[]

    '''
        Properties
    '''
    @property
    def create_directory_property(self, name:str):
        os.mkdir(name)
    
    @property
    def delete_directory_property(self, name:str):
        os.rmdir(name)
        
    @property
    def rename_directory_property(self, name:str, new_name:str):
        os.rename(name, new_name)
    
    @property
    def state_directory_property(self, name:str):
        return os.stat(name)
    
    @property
    def delete_file_property(self, name:str):
        os.remove(name)
        
    @property
    def get_size_file_property(self,root):
        return self.get_size_file(root)
    
    @property
    def rename_file_property(self, name:str, new_name:str):
        os.rename(name, new_name)
    
    @property
    def state_file_property(self, name:str):
        return os.stat(name)
    
    #@property
    #def id(self):
    #    return self.__id
    
    #@property
    #def successor(self):
    #    return self.__successor
    
    #@property
    #def predecessor(self):
    #    return self.__predecessor
    
    '''
        Actions
    '''
    def create_directory(self,name:str):
        self.create_directory_property(name)
        for nodo in self.node_list:
            if nodo!=self.__ip:
                if self.node_control[self.node_list.index(nodo)]==True:
                    node = get_proxy(nodo)
                    try:
                          node.create_directory_property(name)
                    except:
                        stabilized_system=False

    def changeName_directory(self,name,new_name):
        self.rename_directory_property(name)
        for nodo in self.node_list:
            if nodo!=self.__ip:
                if self.node_control[self.node_list.index(nodo)]==True:
                    node = get_proxy(nodo)
                    try:
                          node.rename_directory_property(name)
                    except:
                        stabilized_system=False
         
    def delete_directory(self,name):
        self.delete_directory_property(name)
        for nodo in self.node_list:
            if nodo!=self.__ip:
                if self.node_control[self.node_list.index(nodo)]==True:
                    node = get_proxy(nodo)
                    try:
                          node.delete_directory_property(name)
                    except:
                        stabilized_system=False

    def state_directory(self,name):
        return self.state_directory_property(name)

    def give_me_sucesor(self, id):
        pos=id+1
        if pos>=len(self.node_list):
            pos=0
        while self.node_control[pos]!=True and pos!=id:
            pos+=1
        return pos

def create_finger_table():
    for i in range(8):
        key=node.id+pow(2,i)
        node.finger_table.setdefault(key,key)

def run():  
    while True:
        if not node.stabilized_system:
            if node.ip_boss == None:
                node.search_to_boss=True
                threading.Thread(target=get_signal, args=()).start()
                threading.Thread(target=search_boss, args=()).start()
                
                while True:
                    if node.search_to_boss==False:
                        if not node.leader_calls:
                            node.ip_boss=node.ip
                            node.id=0
                            node.node_list.append(node.ip)
                            node.node_control.append(True)
                            node.__successor=node.ip
                            node.__predecessor=node.ip
                            create_finger_table()
                            #self.get_files("Create")

                        break
                    elif node.NoSereLider==True:
                        node.ip_boss=="temporal"
                        node.NoSereLider=False
                        break
            elif node.ip_boss==node.ip:                                                      
                countdown(200)
                stabilize()
                if not update_fingertables_boss():
                    node.stabilized_system=False
                else:
                    node.stabilized_system=True
            #elif not check_ping(self.__ip_boss):
                #   self.there_boss=False
                #  threading.Thread(target=self.wait_update_boss, args=()).start()
                # threading.Thread(target=self.get_boss, args=()).start()
            else:
                listen()
                                
def get_signal():
    Pyro4.Daemon.serveSimple(
    {
        ResultConnection: "Connection"
    },
    host=node.ip,
    port=8003,
    ns=False)                     

def listen():
    Pyro4.Daemon.serveSimple(
    {
        Listen: "Stabilize"
    },
    host=node.ip,
    port=8005,
    ns=False)             

def search_boss():
    ip=node.ip
    while ip[len(ip)-1]!='.':
        ip=ip[0:len(ip)-1]

    for i in range(62,63):
        uri = "PYRO:Connection@"+ip+str(i)+":8003"
        if node.NoSereLider==True:
            node.search_to_boss=False
            break
        if node.NodosEncontrados.count(ip+str(i))==0 and ip+str(i)!=node.ip:  
            try:
                remote = Pyro4.Proxy(uri)
                data=remote.return_orden("Code #399#",node.ip,node.NodosEncontrados)
                if data=="Code #400#":
                    node.leader_calls=True
                    #i=255
                    break
                elif data=="Nodo aislado":
                        node.NodosEncontrados.extend(remote.give_me_nodos_encontrados())
                elif data=="Code #398":
                        ip_boss=remote.give_me_ip_boss()
                        uri = "PYRO:Stabilize@"+ip_boss+":8003"
                        remote = Pyro4.Proxy(uri)
                        result=remote.return_orden("Code #399#",node.ip,node.NodosEncontrados)                            
            except:
                continue
    node.search_to_boss=False  

def update_fingertables_boss():
    for nodo in node.node_list:
        if nodo!=node.ip: 
            if node.node_control[node.node_list.index(nodo)]:
                try:
                    uri = "PYRO:Stabilize@"+nodo+":8005"
                    remote = Pyro4.Proxy(uri)
                    remote.update_fingetables()
                except:
                    return False

def stabilize():
    first_node_active=Node
    for nodo in node.node_list:
        if nodo != node.ip:
            try: 
                uri = "PYRO:Stabilize@"+nodo+":8003"
                remote = Pyro4.Proxy(uri)
                remote.ping()
                
                if not node.node_control[node.node_list.index(nodo)]:
                        join(nodo)
                        if node.NodosEncontrados.count(nodo)!=0:
                            node.NodosEncontrados.remove(nodo)
                if first_node_active!=None:
                    first_node_active=nodo   
            
            except:
                if node.node_control[node.node_list.index(nodo)]==True:
                    leave(node.node_list.index(nodo))
                continue

        else:
            if first_node_active!=None:
                first_node_active=nodo 


        for nodo in node.NodosEncontrados:
            join(nodo)

        #Hay que actualizar el predecesor del primer nodo

        node.NodosEncontrados=[]

def leave(id):
    node.node_control[id]=False
    ip_predecessor=get_predecessor(node.node_list[id])
    ip_successor=get_successor(node.node_list[id])
    update_successor(ip_predecessor,ip_successor)
    update_predecessor(ip_successor,ip_predecessor)
    
    for nodo in node.node_list:
        if nodo != node.node_list[id] and nodo != node.ip:
            if node.node_control[id]==True:             
                try:
                    uri = "PYRO:Stabilize@"+nodo+":8005"
                    remote = Pyro4.Proxy(uri)
                    remote.leave_message(id)
                except:
                    print("Otro nodo salio del sistema ,se vera cuando lleguemos a el")

def join(ip):
    SoyNuevo=True
    if node.node_list.count(ip)==1:   #Te estas reconectando           
        node.node_control[node.node_list.index(ip)]=True
        SoyNuevo=False
    else:
        node.node_control.append(True)
        node.node_list.append(ip)
    sucesor=get_successor(ip)
    predecesor=get_predecessor(ip)
    update_successor(ip,sucesor)
    update_predecessor(ip,predecesor)
    update_successor(predecesor,ip)
    update_predecessor(sucesor,ip)
    
    for nodo in node.node_list:            
        if node.node_control[node.node_list.index(nodo)]:
            try:
                uri = "PYRO:Stabilize@"+nodo+":8005"
                remote = Pyro4.Proxy(uri)
                remote.join_to_system(node.node_control,node.node_list)
                remote.assign_boss(node.ip)
                remote.assign_id()
                #if nodo==ip:
                    # remote.update_file_hash(list(node.files_hash.keys()),list(node.files_hash.values()))

                    #if not soyNuevo:
                        #s.send(b"Reconectando")
                        

                    #else:
                    # s.send(b"Continue")
                    #data=s.recv(1024)
                    #while data != "":
                    #    data=s.recv(1024)
                    #    keys=json.loads(data)
                    #    data=s.recv(1024)
                        #   values=json.loads(data)
                        #   for i in range(0,len(keys)-1):
                        #      self.files_hash.setdefault(keys[i],values[i])           
                        #   data=s.recv(1024)
                # else:
                #    s.send(b"")

                # s.close()
            except:
                print("Otro nodo entro en el sistema ,se vera cuando lleguemos a el")

def get_predecessor(ip):
    pos=node.node_list.index(ip)
    if pos==0:
        pos==len(node.node_list)-1
    else:
        pos-=1
    while not node.node_list[pos]:
        if pos==0:
            pos==len(node.node_list)-1
        else:
            pos-=1
    return node.node_list[pos]

def get_successor(self,ip):
    pos=self.node_list.index(ip)
    if pos==len(self.node_list)-1:
        pos==0
    else:
        pos+=1
    while not self.node_list[pos]:
        if pos==len(self.node_list)-1:
            pos==0
        else:
            pos+=1
    return self.node_list[pos]

def update_successor(ip,new_successor):
    try:
        uri = "PYRO:Stabilize@"+ip+":8005"
        remote = Pyro4.Proxy(uri)
        remote.update_update_sucesor(new_successor)
    except:
        print("El nodo se desconecto del sistema")
             
def update_predecessor(ip,new_predecessor):
    uri = "PYRO:Stabilize@"+ip+":8005"
    remote = Pyro4.Proxy(uri)
    remote.update_predecesor(new_predecessor)

def countdown(num_of_secs):  #Temporizador que marca la revision de estabilidad del sistema
    while num_of_secs:
        m, s = divmod(num_of_secs, 60)
        min_sec_format = '{:02d}:{:02d}'.format(m, s)
        print(min_sec_format, end='/r')
        time.sleep(1)
        num_of_secs -= 1
          
        

machine_name = socket.gethostname()
machine_ip = socket.gethostbyname(machine_name)
node=Node(machine_ip,os.getcwd())
run()
