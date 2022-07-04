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
class Listen(object):
    def update_predecesor(predecesor):
        node.predecessor=predecesor

    def update_sucesor(sucesor):
        node.successor=sucesor

    def update_fingetables():
        for i in range(0,8):
            id=pow(2,i)+node.id
            node.finger_table[id]=node.give_me_sucesor(id)

    def leave(id):
       node.node_control[id]=False

    


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
        self.id=0
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
   
    def create_finger_table(self):
        for i in range(6):
            key=self.id+pow(2,i)
            self.finger_table.setdefault(key,key)

    def give_me_sucesor(self, id):
      pos=id+1
      if pos>=len(self.node_list):
          pos=0
      while self.node_control[pos]!=True and pos!=id:
          pos+=1
      return pos


def run():  
        while True:
            if not node.stabilized_system:
                if node.ip_boss == None:
                    node.search_to_boss=True
                    #threading.Thread(target=get_signal, args=()).start()
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
                                node.create_finger_table()
                                #self.get_files("Create")

                            break
                        elif node.NoSereLider==True:
                                node.ip_boss=="temporal"
                                node.NoSereLider=False
                                break
                elif node.ip_boss==node.ip:
                         
                          if node.ip_boss==node.ip:                                               
                           node.stabilize()
                           node.update_finger_tables()
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
            ResultConnection: "Stabilize"
        },

        host=node.ip,
        port=8003,
        ns=False
    )                     

def listen():

        Pyro4.Daemon.serveSimple(
        {
            Listen: "Stabilize"
        },

        host=node.ip,
        port=8005,
        ns=False
    )             

def search_boss():
    ip=node.ip
    while ip[len(ip)-1]!='.':
        ip=ip[0:len(ip)-1]

    for i in range(134,136):
            uri = "PYRO:Stabilize@"+ip+str(i)+":8003"
            if node.NoSereLider==True:
                node.search_to_boss=False
                break
            if node.NodosEncontrados.count(ip+str(i))==0:  
                try:
                    remote = Pyro4.Proxy(uri)
                    data=remote.return_orden("Code #399#",node.ip,node.NodosEncontrados)
                    if data=="Code #400#":
                        node.leader_calls=True
                        i=255
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

machine_name = socket.gethostname()
machine_ip = socket.gethostbyname(machine_name)
node=Node(machine_ip,os.getcwd())
run()
