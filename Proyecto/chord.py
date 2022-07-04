from socket import socket
import Pyro4
import socket
import os
import threading
#Server= Pyro4.Daemon(
  #      host="192.168.43.62",
  #      port=8003,
  #      ns=False
   # )

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class ResultConnection(object):
   def __init__(self,node):
       self.nodo=node

   def return_orden(self,message,node):  
            if message=="Code #399#":
                if self.nodo.__ip==self.nodo.__ip_boss:
                    self.nodo.NodosEncontrados.append(node.__ip)
                    self.nodo.NodosEncontrados.extend(node.NodosEncontrados)
                    return 'Code #400#'

                elif self.nodo.__ip_boss==None:
                    node.NodosEncontrados.append(self.nodo.__ip)
                    node.NodosEncontrados.extend(self.nodo.NodosEncontrados)
                    node.NoSereLider=True
                    return "Nodo aislado"
                
                else:
                     uri = 'PYRO:Stabilize@'+node.__ip_boss+':8003'
                     remote = Pyro4.Proxy(uri)
                     return remote.return_orden("Code #398#",node)
                     
            elif message=="Code #398#":
                    if self.nodo.__ip==self.nodo.__ip_boss:
                               set(self.nodo.NodosEncontrados.extend(node.NodosEncontrados))
                               set(self.nodo.NodosEncontrados.append(node.__ip))

                    return 'Code #400#'

@Pyro4.expose
class Node:
    def __init__(self, ip, path):
        self.__id=0
        self.__ip=ip
        self.__files=list()  #se guardaran los archivos que esten almacenados en este nodo , mas alla que sea una replica . 
        self.__files_system=dict()  #Aqui se guardara el hash del archivo y en que otros nodos esta
        self.__predecessor=None
        self.__successor=None
        self.finger_table=dict()
        self.__ip_boss=None
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

    def run(self):  
        while True:
            if not self.stabilized_system:
                if self.__ip_boss==self.__ip:
                    while True:
                        continue
                    if self.__ip_boss==self.__ip:                                               
                        self.stabilize()
                        self.update_finger_tables()
                        self.stabilized_system=True
                elif self.__ip_boss==None:
                    self.search_to_boss=True
                    threading.Thread(target=self.get_signal, args=()).start()
                    threading.Thread(target=self.search_boss, args=()).start()
                    
                    while True:
                        if self.search_to_boss==False:
                            if not self.leader_calls:
                                self.__ip_boss=self.__ip
                                #self.__id=0
                                #self.node_list.append(self.__ip)
                                #node_control.append(True)
                                #self.__successor=self.__ip
                                #self.__predecessor=self.__ip
                                #self.create_finger_table()
                                #self.get_files("Create")

                            break
                        elif self.NoSereLider==True:
                                 self.__ip_boss=="temporal"
                                 self.NoSereLider=False
                                 break
                                
    def get_signal(self):
             
        Pyro4.Daemon.serveSimple(
        {
            ResultConnection: "Stabilize"
        },
        host=self.__ip,
        port=8003,
        ns=False
    )                     

    def search_boss(self):
        ip=self.__ip
        while ip[len(ip)-1]!='.':
            ip=ip[0:len(ip)-1]
    
        for i in range(253,254):
                uri = 'PYRO:Stabilize@'+ip+str(i)+':8003'
                if self.NoSereLider==True:
                    self.search_to_boss=False
                    break
                if self.__ip!= ip+str(i) and self.NodosEncontrados.count(ip+str(i))==0:  
                  try:
                    remote = Pyro4.Proxy(uri)
                    remote._pyroBind()
                    data=remote.return_orden("Code #399#",self,None)
                    if data=="Code #400#":
                        self.leader_calls=True
                        i=255
                    elif data=="Nodo aislado":
                         print("")
                         #   continue
                    
                  except:
                     print("continue")
        
            
                self.search_to_boss=False  

if __name__ == '__main__':
    machine_name = socket.gethostname()
    machine_ip = socket.gethostbyname(machine_name)
    node=Node(machine_ip,os.getcwd())
    node.run()

uri = "PYRO:example.calculator@192.168.43.62:8002"

remote_calculator = Pyro4.Proxy(uri)
print(remote_calculator.add(1,2))
