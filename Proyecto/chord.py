from itertools import count
from pickle import TRUE
from platform import node
from random import Random, random
import socket
import os
import threading
import Pyro4
import time
import hashlib
from datetime import datetime
from Accessories.search_type import Search_Type

@Pyro4.expose
class UpdateDirectoriesManager(object):
    def create_directory(self,root):
        os.mkdir(directory_path + root)

    def change_name_directory(self,root,new_name):
        os.rename(directory_path + root, directory_path + new_name)

    def delete_directory(self,root):
        os.rmdir(directory_path + root)
    
    def update_data_file(self,data):
        with open(directory_path + "/Reports/files.fl", 'w') as f:
            f.write(data)

@Pyro4.expose
class FindFile(object):

  def id_file_delete(self,root):
      node.files_hash.pop(directory_path + root)

  def delete_replica(self,root,hash):
        os.remove(directory_path + root)
        node.files.remove(hash)
        node.files_system.pop(hash)

  def delete_file(self,root,hash):
    os.remove(directory_path + root)
    for nodo in node.files_system[hash]:
        if nodo!=node.ip:
            uri = "PYRO:FindFile@"+nodo+":8013"
            remote = Pyro4.Proxy(uri)
            remote.delete_replica(root,hash)
                          
    node.files.remove(hash)
    node.files_system.pop(hash) 

  def search_for_delete(self,id,hash,root):
    find_file(hash,None,id,Search_Type.DELETE,root)
  
  def cant_archivos(self):
    return len(node.files_system)

  def save_file(self,name,write_mode,content):
    with open(directory_path + name, write_mode) as file:
        file.write(content)
    
    hash=hashlib.sha256(name+str(datetime.now())).hexdigest()
    if node.files.count(hash)==0:
     node.files.append(hash)
    if list(node.files_system.keys()).count(hash)==0:
     node.files_system.setdefault(hash,[])

  def upload_root(self,name,id_file):
    node.files_hash.setdefault(directory_path + name,id_file)

  def give_me_sucesor(self):
    return node.successor

  def update_replicas(self,hash,nodes):
    node.files_system.setdefault(hash,nodes)

  def rename_file(self,name,new_name):
    id_file=node.files_hash.pop(directory_path + name)
    node.files_hash.setdefault(directory_path + new_name,id_file)

  def return_state(self,hash,name):
     if node.files.count(hash)==1:
        return os.stat(directory_path + name)
     else:
        return False

  def search_for_state(self,id,hash,name):
     return find_file(hash,None,id,Search_Type.STATE,directory_path + name)

  def update_file_edit(self,name,hash_new):
     node.files_hash.pop(directory_path + name)
     node.files_hash.setdefault(directory_path + name,hash_new)

  def direct_edit(self,hash,name,write_mode,content,first):
   if first:
       os.remove(directory_path + name)
   if content!=b"":
    with open(directory_path + name, write_mode) as file:
            file.write(content)
   else:
              hash_new=hashlib.sha256(name+str(datetime.now())).hexdigest()
              node.files_system.setdefault(hash_new,node.files_system.get(hash))    #anadir el nuevo hash junto a la lista de ips donde esta el archivo
              node.files.remove(hash)
              node.files.append(hash_new) ##Anadir el nuevo hash
              node.files_hash.pop(name)
              node.files_hash.setdefault(name,id+","+hash_new)

              for nodo in node.node_list:
                    if nodo!=node.ip:
                        if node.node_control[node.node_list.index(nodo)]:
                            uri = "PYRO:FindFile@"+nodo+":8013"
                            remote = Pyro4.Proxy(uri)
                            remote.update_file_edit(name,id+","+hash_new)

  def search_edit(self,hash,id,root,write_mode,content,first):
     find_file(hash=hash,write_mode=write_mode,id=id,Search_Type=Search_Type.EDIT,name=root,content=content,first=first)

  def get_file(self,name,read_mode):
      with open(name, read_mode) as f:
             while True:
                bytes_read = f.read()
                if bytes_read == b'':
                    break
                else:
                    files += str(bytes_read)
                    uri = "PYRO:FindFile@"+nodo+":8013"
                    remote = Pyro4.Proxy(uri)
                    remote.TT(bytes_read)

  def search_file(self,hash,read_mode,id,root):
    find_file(hash,read_mode,id,Search_Type.DOWNLOAD,root)

@Pyro4.expose
class Listen(object):
    def update_predecesor(self,predecesor):
        node.predecessor=predecesor

    def update_sucesor(self,sucesor):
        node.successor=sucesor

    def update_fingetables(self):
        for i in range(0,8):
            id=pow(2,i)+node.id
            node.finger_table[id]=node.give_me_sucesor(id)

    def leave_message(self,id):
        node.node_control[id]=False

    def join_to_system(self,node_control_boss,node_list_boss):
        node.node_control=node_control_boss
        node.node_list=node_list_boss
    
    def assign_boss(self,ip_boss):
        node.ip_boss=ip_boss

    def assign_id(self):
        node.id=node.node_list.index(node.ip)

@Pyro4.expose
class SearchBoss(object):
      
    def new_boss(self,ip_boss):
        node.ip_boss=ip_boss
        node.there_boss=True

    def ping(self):
        return

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
    
    def ping(self):
        return

@Pyro4.expose
class FilesManager(object):
    
    def edit(self,name:str, write_mode: str, content: bytes,first:bool):
      if first:  
        file_id=node.files_hash.get(name)
        
        hash_code = file_id
        id=""
        while hash_code[0]!=",":
            id+=hash_code[0]
            hash_code=hash_code[1:len(hash_code)-1]
        hash_code=hash_code[1:len(hash_code)-1]

        if node.files.count(hash_code)==1:
             
             os.remove(name)
             with open(name,write_mode) as f: 
                f.write(content)
                ipDondeEsta=node.ip
             
             if content==b"":
              hash_new=hashlib.sha256(name+str(datetime.now())).hexdigest()
              node.files_system.setdefault(hash_new,node.files_system.get(hash_code))    #anadir el nuevo hash junto a la lista de ips donde esta el archivo
              node.files.remove(hash)
              node.files.append(hash_new) ##Anadir el nuevo hash
              node.files_hash.pop(name)
              node.files_hash.setdefault(name,id+","+hash_new)

              for nodo in node.node_list:
                    if nodo!=node.ip:
                        if node.node_control[node.node_list.index(nodo)]:
                            uri = "PYRO:FindFile@"+nodo+":8013"
                            remote = Pyro4.Proxy(uri)
                            remote.update_file_edit(name,id+","+hash_new)                         
                            

        else:
           ipDondeEsta=find_file(hash_code,write_mode, id, Search_Type.EDIT,name,content,first)
        
      else:
        uri = "PYRO:FindFile@"+ipDondeEsta+":8013"
        remote = Pyro4.Proxy(uri)
        remote.direct_edit(hash_code,name,write_mode,content)
                      
    def delete(self, root:str):
        file_id=node.files_hash.get(root)
        for nodo in node.node_list: 
            if nodo!=node.ip:
                if node.node_control[node.node_list.index(nodo)]==True:
                    uri = "PYRO:FindFile@"+nodo+":8013"
                    remote = Pyro4.Proxy(uri)
                    remote.id_file_delete(root)
                                 
        node.files_hash.pop(root)

        hash_code = file_id
        id=""
        while hash_code[0]!=",":
            id+=hash_code[0]
            hash_code=hash_code[1:len(hash_code)-1]
        hash_code=hash_code[1:len(hash_code)-1]

        if node.files.count(hash)==1:
              os.remove(root)               
              node.files.remove(hash)
              for nodo in node.files_system.get(hash):
                  if nodo!=node.ip:
                     uri = "PYRO:FindFile@"+nodo+":8013"
                     remote = Pyro4.Proxy(uri)
                     remote.delete_replica(root,hash_code)
        else:
         find_file(hash_code, None, id, Search_Type.DELETE,root)
    
    def rename(self, name:str, new_name:str):
          file_id= node.files_hash.pop(name)
          node.files_hash.setdefault(new_name,file_id)
          for nodo in node.node_list:
             if nodo!=node.ip:
                if node.node_control[self.node_list.index(nodo)]:
                    uri = "PYRO:FindFile@"+nodo+":8013"
                    remote = Pyro4.Proxy(uri)
                    remote.rename_file(name,new_name)
        
    def state(self, name:str):
        file_id=self.files_hash.get(name)
        
        hash_code = file_id
        id=""
        while hash_code[0]!=",":
            id+=hash_code[0]
            hash_code=hash_code[1:len(hash_code)-1]
        hash_code=hash_code[1:len(hash_code)-1]

        if node.files.count(hash_code)==1:
           return os.stat(name)
        else:
           return find_file(hash_code,None, id, Search_Type.STATE,name)
    
    def upload(self, name:str, write_mode: str, content: bytes,first:bool):
        if first:
            ip=None
            count_files=0
            count=0
            for nodo in node.node_list:
                if node.node_control[count]==True and nodo!=node.ip:
                    try:
                        uri = "PYRO:FindFile@"+nodo+":8013"
                        remote = Pyro4.Proxy(uri)
                        CantArchivos=remote.cant_archivos()
                        if count==0:
                            ip = nodo
                            count_files=CantArchivos
                        elif CantArchivos<count_files:
                            ip = nodo
                            count_files=CantArchivos
                    except:
                        stabilized_system=False
                        return False
                    count+=1
            try:    
                hash=hashlib.sha256(name+str(datetime.now())).hexdigest()
                if ip!=node.ip:
                    id=node.node_list.index(ip)
                    uri = "PYRO:FindFile@"+ip+":8013"
                    remote = Pyro4.Proxy(uri)
                    remote.save_file(id,name,write_mode,content)
                    id_file_return=id+","+hash                    
                else:
                    print("entro")
                    with open(name, write_mode) as file:
                        file.write(content)
                    if node.files.count(hash)==0:
                        node.files.append(hash)
                    if list(node.files_system.keys()).count(hash)==0:
                        node.files_system.setdefault(hash,[])
                    id_file_return=node.id+","+hash
                
                node.files_hash.setdefault(name,id_file_return)
                
                for nodo in node.node_list:
                    if nodo!=node.ip:
                        if node.node_control[node.node_list.index(nodo)]==True:
                            uri = "PYRO:FindFile@"+nodo+":8013"
                            remote = Pyro4.Proxy(uri)
                            remote.upload_root(name,id_file_return)
                                
                nodes_where_the_file_is=[]    
                nodes_where_the_file_is.append(ip)
                count_replicas=3
                
                while count_replicas>0:#Replicacion
                    if ip!=self.ip:
                        uri = "PYRO:FindFile@"+ip+":8013"
                        remote = Pyro4.Proxy(uri)
                        ip=remote.give_me_sucesor()   
                    else:
                        ip=node.successor
                    
                    if ip!=node.ip: 
                        uri = "PYRO:FindFile@"+ip+":8013"
                        remote = Pyro4.Proxy(uri)
                        remote.save_file(name,write_mode,content)  
                        if nodes_where_the_file_is.count(ip)==0:
                            nodes_where_the_file_is.append(ip)
                    
                        count_replicas-=1
                        
                        for ip in nodes_where_the_file_is:
                            uri = "PYRO:FindFile@"+ip+":8013"
                            remote = Pyro4.Proxy(uri)
                            remote.update_replicas(hash,nodes_where_the_file_is)  
            except:
                stabilized_system=False
                return False                   
    
    def download(self, name:str, read_mode: str):
        file_id=node.files_hash.get(name)
        
        hash_code = file_id
        id = ""
        while hash_code[0]!=",":
            id += hash_code[0]
            hash_code = hash_code[1:len(hash_code)-1]
        hash_code = hash_code[1:len(hash_code)-1]

        if node.files.count(hash_code)==1:
            with open(name, read_mode) as f:
             while True:
                bytes_read = f.read()
                if bytes_read == b'':
                    break
                else:
                    files += str(bytes_read)
                    uri = "PYRO:FindFile@"+nodo+":8013"
                    remote = Pyro4.Proxy(uri)
                    remote.TT(bytes_read)

        else:
             find_file(hash_code,read_mode, id, Search_Type.DOWNLOAD,name)
    
@Pyro4.expose
class DirectoriesManager(object):
    def create_directory(self, name:str, db_root:str, db_data:str):
        os.mkdir(name)
        with open(db_root, 'w') as f:
            f.write(db_data)
        for nodo in node.node_list:
            if node.node_control[node.node_list.index(nodo)] and node.ip!=nodo:
                uri = "PYRO:UpdateDirectoriesManager@"+nodo+":8012"
                remote = Pyro4.Proxy(uri)
                list_name = name.split('/root/')
                remote.create_directory("/root/"+list_name[1])
                remote.update_data_file(db_data)

    def change_name_directory(self, name:str, new_name:str, db_root:str, db_data:str):
        os.rename(name, new_name)
        with open(db_root, 'w') as f:
            f.write(db_data)
        for nodo in node.node_list:
            if node.node_control[node.node_list.index(nodo)] and node.ip!=nodo:
                list_name = name.split('/root/')
                list_new_name = new_name.split('/root/')
                uri = "PYRO:UpdateDirectoriesManager@"+nodo+":8012"
                remote = Pyro4.Proxy(uri)
                remote.change_name_directory("/root/" + list_name[1], "/root/" + list_new_name[1])
                remote.update_data_file(db_data)
         
    def delete_directory(self, name:str, db_root:str, db_data:str):
        os.rmdir(name)
        with open(db_root, 'w') as f:
            f.write(db_data)
        for nodo in node.node_list:
            if node.node_control[node.node_list.index(nodo)] and node.ip!=nodo:
                list_name = name.split('/root/')
                uri = "PYRO:UpdateDirectoriesManager@"+nodo+":8012"
                remote = Pyro4.Proxy(uri)
                remote.delete_directory("/root/" + list_name[1])
                remote.update_data_file(db_data)

    def state_directory(self,name):
        return os.stat(name)


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
        self.there_boss=True
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
    count=0
    while True:
        if not node.stabilized_system:
            if node.ip_boss == None and not node.leader_calls:
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
                countdown(10)
                stabilize()
                if not update_fingertables_boss():
                    node.stabilized_system=False
                else:
                    node.stabilized_system=True
            elif count==0 :
                    threading.Thread(target=listen, args=()).start()
                    threading.Thread(target=wait_update_boss, args=()).start()
                    time.sleep(2)
                    count+=1
            else:     
                if node.ip_boss!=None and node.there_boss:
                    if not check_ping() :
                        node.there_boss=False
                        threading.Thread(target=get_boss, args=()).start()
                                                
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
    first_node_active=None
    last_active_node=None
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
                last_active_node=nodo
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
            last_active_node=nodo
    
    update_predecessor(first_node_active,last_active_node)

    node.NodosEncontrados=[]

def leave(id):
    node.node_control[id]=False
    ip_predecessor=get_predecessor(node.node_list[id])
    ip_successor=get_successor(node.node_list[id])
    if ip_predecessor!=node.ip:
        update_successor(ip_predecessor,ip_successor)
    else:
        node.successor=ip_successor
      
    if ip_successor!=node.ip:
        update_predecessor(ip_successor,ip_predecessor)
    else:
        node.predecessor=ip_predecessor
    
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
    if ip!=node.ip:    
        update_successor(ip,sucesor)
        update_predecessor(ip,predecesor)
    else:
        node.sucessor=sucesor
        node.predecessor=predecesor
    
    if predecesor!=node.ip:
        update_successor(predecesor,ip)
    else:
        node.sucessor=ip
    
    if sucesor!=node.ip:
        update_predecessor(sucesor,ip)
    else:
        node.predecessor=ip
    for nodo in node.node_list:         
        if node.node_control[node.node_list.index(nodo)] and nodo!= node.ip:
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
        pos=len(node.node_list)-1
    else:
        pos-=1
    while not node.node_control[pos]:
        if pos==0:
            pos=len(node.node_list)-1
        else:
            pos-=1
    return node.node_list[pos]

def get_successor(ip):
    pos=node.node_list.index(ip)
    if pos==len(node.node_list)-1:
        pos=0
    else:
        pos+=1
    while not node.node_control[pos]:
        if pos==len(node.node_list)-1:
            pos=0
        else:
            pos+=1
    return node.node_list[pos]

def update_successor(ip,new_successor):
    try:
        uri = "PYRO:Stabilize@"+ip+":8005"
        remote = Pyro4.Proxy(uri)
        remote.update_sucesor(new_successor)
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

def check_ping():
    try:
        uri = "PYRO:Connection@"+node.ip_boss+":8003"
        remote = Pyro4.Proxy(uri)
        remote.ping()
    except:
        return False
    return True
     
def get_boss():
    for nodo in node.node_list:
        if not node.there_boss: 
            if nodo!=node.ip and node.node_control[node.node_list.index(nodo)]:
                if nodo!=node.ip_boss:
                    uri = "PYRO:SearchBoss@"+nodo+":8002"
                    remote = Pyro4.Proxy(uri)
                    remote.ping()
                    remote.new_boss(nodo)
                    for nd in node.node_list:
                        if not node.there_boss and nodo!=node.ip and node.node_control[node.node_list.index(nodo)] and nd!=nodo:
                            remote.new_boss(nodo)
                else:
                    continue
        else:
            break
    if not node.there_boss:
        node.ip_boss = node.ip

def wait_update_boss():
    Pyro4.Daemon.serveSimple(
    {
        SearchBoss: "SearchBoss"
    },
    host=node.ip,
    port=8002,
    ns=False)  
        
def createServerDM():
    Pyro4.Daemon.serveSimple(
    {
       DirectoriesManager : "DirectoriesManager"
    },
    host=node.ip,
    port=8010,
    ns=False)

def createServerFM():
    Pyro4.Daemon.serveSimple(
    {
       FilesManager : "FilesManager"
    },
    host=node.ip,
    port=8011,
    ns=False)

def createServerUDM():
    Pyro4.Daemon.serveSimple(
    {
       UpdateDirectoriesManager : "UpdateDirectoriesManager"
    },
    host=node.ip,
    port=8012,
    ns=False)

def createServerFF():
    Pyro4.Daemon.serveSimple(
    {
       FindFile : "FindFile"
    },
    host=node.ip,
    port=8013,
    ns=False)

def find_file(self,hash,write_mode,id,search_type: Search_Type,root,content=None,first=None):
        if search_type == Search_Type.DOWNLOAD:  
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
                keys=self.finger_table.keys()
                if list(keys).count(id)==1:
                    uri = "PYRO:FindFile@"+node.node_list[self.finger_table[id]]+":8013"
                    remote = Pyro4.Proxy(uri)
                    remote.get_file(root,write_mode)
                     
                else:
                    dictionary=self.finger_table
                    value=dictionary.popitem()
                    value=value[1]
                    
                    while True:
                        if value<id:
                            break
                        else:
                            value=dictionary.popitem()
                            value=value[1]

                    uri = "PYRO:FindFile@"+node.node_list[self.finger_table[id]]+":8013"
                    remote = Pyro4.Proxy(uri)
                    remote.search_file(hash,write_mode,id,root) 
                

        elif search_type == Search_Type.EDIT:
                keys=self.finger_table.keys()
                if list(keys).count(id)==1:
                    uri = "PYRO:FindFile@"+node.node_list[self.finger_table[id]]+":8013"
                    remote = Pyro4.Proxy(uri)
                    return remote.direct_edit(hash,root,write_mode,content,first)
                else:
                    dictionary=self.finger_table
                    value=dictionary.popitem()
                    value=value[1]
                    
                    while True:
                        if value<id:
                            break
                        else:
                            value=dictionary.popitem()
                            value=value[1]
                          
                    
                    uri = "PYRO:FindFile@"+node.node_list[value]+":8013"
                    remote = Pyro4.Proxy(uri)
                    return remote.search_edit(hash,id,root,write_mode,content,first)
                 

        elif search_type== Search_Type.STATE:
                
                keys=node.finger_table.keys()
                if list(keys).count(id)==1:
                    uri = "PYRO:FindFile@"+node.node_list[value]+":8013"
                    remote = Pyro4.Proxy(uri)
                    return remote.return_state(hash,root)
                               
                else:
                    dictionary=self.finger_table
                    value=dictionary.popitem()
                    value=value[1]
                    
                    while True:
                        if value<id:
                            break
                        else:
                            value=dictionary.popitem()
                            value=value[1]

                    uri = "PYRO:FindFile@"+node.node_list[value]+":8013"
                    remote = Pyro4.Proxy(uri)
                    return remote.search_for_state(id,hash,root) 
                
                    
        elif search_type == Search_Type.DELETE:
           
                keys=node.finger_table.keys()
                if list(keys).count(id)==1:
                    uri = "PYRO:FindFile@"+node.node_list[self.finger_table[id]]+":8013"
                    remote = Pyro4.Proxy(uri)
                    remote.id_file_delete(root,hash)
                else:
                    dictionary=node.finger_table
                    value=dictionary.popitem()
                    value=value[1]
        
                    while True:
                        if value<id:
                            break
                        else:
                            value=dictionary.popitem()
                            value=value[1]
                          
                    
                    uri = "PYRO:FindFile@"+node.node_list[value]+":8013"
                    remote = Pyro4.Proxy(uri)
                    remote.search_for_delete(id,hash,root)


if __name__ == "__main__":  
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_server = s.getsockname()[0]
    s.close()
    node=Node(ip_server,os.getcwd())
    directory_path = os.getcwd()
    threading.Thread(target=createServerDM, args=()).start()
    threading.Thread(target=createServerFM, args=()).start()
    threading.Thread(target=createServerUDM, args=()).start()
    threading.Thread(target=createServerFF, args=()).start()
    run()