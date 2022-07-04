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

   def return_orden(o,message,node):  
            #if message=="Code #399#":
             #   if self.nodo.__ip==self.nodo.__ip_boss:
              #      self.nodo.NodosEncontrados.append(node.__ip)
               #     self.nodo.NodosEncontrados.extend(node.NodosEncontrados)
                #    return 'Code #400#'

               # elif self.nodo.__ip_boss==None:
                #    node.NodosEncontrados.append(self.nodo.__ip)
                 #   node.NodosEncontrados.extend(self.nodo.NodosEncontrados)
                 #   node.NoSereLider=True
                 #   return "Nodo aislado"
                
               # else:
                #     uri = 'PYRO:Stabilize@'+node.__ip_boss+':8003'
                 #    remote = Pyro4.Proxy(uri)
                 #    return remote.return_orden("Code #398#",node)
                     
           # elif message=="Code #398#":
            #        if self.nodo.__ip==self.nodo.__ip_boss:
             #                  set(self.nodo.NodosEncontrados.extend(node.NodosEncontrados))
              #                 set(self.nodo.NodosEncontrados.append(node.__ip))

               #     return 'Code #400#'
               print("Entro")

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
            if not node.stabilized_system:
                if node.ip_boss == False:
                    node.search_to_boss=True
                    threading.Thread(target=get_signal, args=()).start()
                    #threading.Thread(target=search_boss, args=()).start()
                    
                    
                    while True:
                        if node.search_to_boss==False:
                            if not node.leader_calls:
                                node.ip_boss=node.ip
                                node.id=0
                                #self.node_list.append(self.__ip)
                                #node_control.append(True)
                                #self.__successor=self.__ip
                                #self.__predecessor=self.__ip
                                #self.create_finger_table()
                                #self.get_files("Create")

                            break
                        #elif node.NoSereLider==True:
                         #       node.ip_boss=="temporal"
                          #      node.NoSereLider=False
                           #     break
               # elif node.ip_boss==node.ip:
                #          while True:
                 #          continue
                      #    if node.ip_boss==node.__ip:                                               
                       #    node.stabilize()
                        #   node.update_finger_tables()
                         #  node.stabilized_system=True
                                
def get_signal():

        Pyro4.Daemon.serveSimple(
        {
            ResultConnection: "Chord"
        },

        host=node.ip,
        port=8003,
        ns=False
    )                     

def search_boss():
    ip=node.ip
    while ip[len(ip)-1]!='.':
        ip=ip[0:len(ip)-1]

    for i in range(100,101):
            uri = "PYRO:Chord@"+ip+str(i)+":8003"
            if node.NoSereLider==True:
                node.search_to_boss=False
                break
            if node.ip!= ip+str(i) and node.NodosEncontrados.count(ip+str(i))==0:  
                try:
                    remote = Pyro4.Proxy(uri)
                    data=remote.return_orden("Code #399#",node,"")
                    if data=="Code #400#":
                        node.leader_calls=True
                        i=255
                    elif data=="Nodo aislado":
                            print("")
                            #   continue
                
                except:
                    print("continue")
                    continue
    
        
            node.search_to_boss=False  

machine_name = socket.gethostname()
machine_ip = socket.gethostbyname(machine_name)
node=Node(machine_ip,os.getcwd())
run()

 
