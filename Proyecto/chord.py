import socket
import os
import threading
import Pyro4
#Server= Pyro4.Daemon(
  #      host="192.168.43.62",
  #      port=8003,
  #      ns=False
   # )

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class ResultConnection(object):
    
  def add(self, a, b):
        return a + b

@Pyro4.expose
class Node:
    def __init__(self, ip, path):
        self.id=0
        self.ip=ip
        self.files=list()  #se guardaran los archivos que esten almacenados en este nodo , mas alla que sea una replica . 
        self.files_system=dict()  #Aqui se guardara el hash del archivo y en que otros nodos esta
        self.predecessor=None
        self.successor=None
        self.finger_table=dict()
        self.ip_boss=False
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

    

def run():  
        while True:
            if not nodo.stabilized_system:
                if nodo.ip_boss == False:
                    nodo.search_to_boss=True
                    threading.Thread(target=get_signal, args=()).start()
                    threading.Thread(target=search_boss, args=()).start()
                    
                    
                    while True:
                        if nodo.search_to_boss==False:
                            if not nodo.leader_calls:
                                nodo.ip_boss=nodo.ip
                                nodo.id=0
                                #self.node_list.append(self.__ip)
                                #node_control.append(True)
                                #self.__successor=self.__ip
                                #self.__predecessor=self.__ip
                                #self.create_finger_table()
                                #self.get_files("Create")

                            break
                        elif nodo.NoSereLider==True:
                                 nodo.ip_boss=="temporal"
                                 nodo.NoSereLider=False
                                 break
                elif nodo.ip_boss==nodo.ip:
                    while True:
                        continue
                    if nodo.ip_boss==nodo.__ip:                                               
                        nodo.stabilize()
                        nodo.update_finger_tables()
                        nodo.stabilized_system=True
                                
def get_signal():
             
        Pyro4.Daemon.serveSimple(
        {
            ResultConnection: "Stabilize"
        },
        host=nodo.ip,
        port=8002,
        ns=False
    )                     

def search_boss():
        ip=nodo.ip
        while ip[len(ip)-1]!='.':
            ip=ip[0:len(ip)-1]
    
        for i in range(253,254):
                uri = "PYRO:Stabilize@"+ip+str(i)+":8003"
                if nodo.NoSereLider==True:
                    nodo.search_to_boss=False
                    break
                if nodo.ip!= ip+str(i) and nodo.NodosEncontrados.count(ip+str(i))==0:  
                  try:
                    remote = Pyro4.Proxy(uri)
                    data=remote.add(2,3)
                    if data=="Code #400#":
                        nodo.leader_calls=True
                        i=255
                    elif data=="Nodo aislado":
                         print("")
                         #   continue
                    
                  except:
                     print("continue")
        
            
                nodo.search_to_boss=False  

machine_name = socket.gethostname()
machine_ip = socket.gethostbyname(machine_name)
nodo=Node(machine_ip,os.getcwd())
run()

 
