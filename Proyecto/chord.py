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

    def ping():
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

                 except:
                    if node.node_control[node.node_list.index(nodo)]==True:
                        leave(node.node_list.index(nodo))
                    continue

        for nodo in node.NodosEncontrados:
            join(nodo)
        
        node.NodosEncontrados=[]

def leave(id):
        node.node_control[id]=False
        ip_predecessor=get_predecessor(node.node_list[id])
        ip_successor=get_successor(node.node_list[id])
        update_successor(ip_predecessor,ip_successor)
        update_predecessor(ip_successor,ip_predecessor)
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            for nodo in self.node_list:
                if nodo!=self.node_list[id]:
                    if node_control[id]==True:             
                        try:
                            s.connect(nodo,8005)
                            s.send(b"LEAVE")
                            s.send(b"{}".__format__(str(id)))
                            s.close()
                        except:
                            print("Otro nodo salio del sistema ,se vera cuando lleguemos a el")

def join(self,ip):
        soyNuevo=True
        if not self.node_list.count(ip)==1:   #Te estas reconectando           
            node_control[self.node_list.index(ip)]=True
            soyNuevo=False
        else:
            node_control.append(True)
            self.node_list.append(ip)
        sucesor=self.get_successor(ip)
        predecesor=self.get_predecessor(ip)
        self.update_successor(ip,sucesor)
        self.update_predecessor(ip,predecesor)
        self.update_successor(predecesor,ip)
        self.update_predecessor(sucesor,ip)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            for nodo in self.node_list:            
                if node_control[self.node_list.index(nodo)]:
                    try:
                        s.connect(nodo,8005)
                        s.send(b"JOIN")
                        send_list=json.dumps(node_control)
                        s.send(b"{}".__format__(send_list.encode('utf-8')))
                        send_list=json.dumps(self.node_list)
                        s.send(b"{}".__format__(send_list.encode('utf-8')))
                        if soyNuevo:
                            s.send(b"{}".__format__(str(self.node_list.index(ip)).encode('utf-8')))
                        else:
                            s.send(b"")
                        if nodo==ip:
                            send_list=json.dumps(list(self.files_hash.keys()))
                            s.send(b"{}".__format__(send_list))
                            send_list=json.dumps(list(self.files_hash.values()))
                            s.send(b"{}".__format__(send_list))

                            if not soyNuevo:
                             s.send(b"Reconectando")
                             

                            else:
                             s.send(b"Continue")
                            data=s.recv(1024)
                            while data != "":
                                data=s.recv(1024)
                                keys=json.loads(data)
                                data=s.recv(1024)
                                values=json.loads(data)
                                for i in range(0,len(keys)-1):
                                   self.files_hash.setdefault(keys[i],values[i])           
                                data=s.recv(1024)
                        else:
                            s.send(b"")

                        
                        

                        s.close()
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
        remote.update_predecesor(new_successor)
       except:
        print("El nodo se desconecto del sistema")
             
def update_predecessor(ip,new_predecessor):
              uri = "PYRO:Stabilize@"+ip+":8005"
              remote = Pyro4.Proxy(uri)
              remote.update_predecesor(new_predecessor)

machine_name = socket.gethostname()
machine_ip = socket.gethostbyname(machine_name)
node=Node(machine_ip,os.getcwd())
run()
