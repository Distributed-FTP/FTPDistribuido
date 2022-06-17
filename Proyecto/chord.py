#from typing_extensions import Self
from uuid import getnode as get_mac
import sys,subprocess
import os
import socket
from matplotlib.pyplot import get
import json
import threading


#Si el nodo i de la red esta activo se guarda True, esta lista servira para comprobar constantemente 
# si un nodo se desactivo o si un nodo se activo
controlDNodos=[]

#esta variable es para saber el estado en que se encuentra chord , si buscando un elemento , si anadiendo un elemento o si esta reorganizando
#los nodos
estadoDChord=None

#Esta lista es para guardar la relacion IP : Id de los nodos del sistema


def BuscaNodosEnRed():
 if len(sys.argv)!=2:
     print("psweep.py 10.0.0")
 else:
     cmdping="ping -cl "+sys.argv[1]

     for x in range (2,255):
         p = subprocess.Popen(cmdping+str(x),shell=True,stderr=subprocess.PIPE)

         while True:
             out=p.stderr.read(1)
             if out=='' and p.poll()!=None:
                 break
             if out != '':
                 sys.stdout.write(out)
                 sys.stdout.flush()

class Node:
    def __init__(self,ip):
        self._id=None
        self._ip=ip
        self._keys=list()  #Para cada nodo hay que saber las llaves que tiene asociadas en cada momento
        self._predecesor=None
        self._sucesor=None
        self.fingertable=None
        self._soyLider=False
        self._ultimoidAsignado=0
        self.listaDNodos=[]  
        #Todo Nodo debe saber si es el lider , en caso de que lo sea debe realizar acciones especificas
        # self.fingertable = {((self._id+(i**2))%2**160) : self._ip for i in range(160)} #!ID:IP


    def start_comunication(self):

       #if mac=='94-E2-3C-07-91-08':

        try:
            self._soyLider=True
            self.id=0
            self.listaDNodos.append("{}".format(self._ip))
            ultimoIdAsignado=0
            BUFFER_SIZE=1024
            self.server = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self._ip,12345))
            self.server.listen(10000)
            #self.server.settimeout(1000)
            conn, addr = self.server.accept() # Establecemos la conexión con el cliente 
            if conn: 
              while True:
            # Recibimos bytes, convertimos en str
               data = conn.recv(BUFFER_SIZE)
            # Verificamos que hemos recibido datos
               if not data:
                break
               else:
                if data.decode('utf-8')=="Nodo Soy FTP":
                 print(data)
                 print('[*] Datos recibidos: {}'.format(data.decode('utf-8'))) 
                 conn.send(b'{}'.__format__(self._id)) # Hacemos echo convirtiendo de nuevo a bytes
                 self.listaDNodos.append("{}".format(addr[0]))
                #else:
                conn.close()
                #ahora asignamos los sucesores , predecesores y fingertables
                self.completar_nodos()
                self.pasarInfoDlider() 



        except socket.error:
           # prRed('Error abriendo socket')
            return
        
       #else:
        SERVER_HOST = None
        SERVER_PORT = 12345

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

          s.connect((SERVER_HOST, SERVER_PORT))
          #nombre_d_equipo=socket.gethostname()
          #ip=socket.gethostbyname(nombre_d_equipo)

          s.send(b"Nodo Soy FTP")
          #s.send(b"{}".__format__(ip))
          data = s.recv(1024)
          iddecodificado=data.decode()
          
          self._id=iddecodificado
          
          self.server = socket.socket(
               socket.AF_INET, socket.SOCK_STREAM)
          
          self.server.bind((self._ip,SERVER_PORT))
          self.server.listen(10000)
          conn, addr = self.server.accept() # Establecemos la conexión con el cliente
          with conn:
              datapredecesor = conn.recv(BUFFER_SIZE)
              ippredecesor=datapredecesor.decode('utf-8')
              self._predecesor=ippredecesor
              datasucesor = conn.recv(BUFFER_SIZE)
              ipsucesor=datasucesor.decode('utf-8')
              self._sucesor=ipsucesor
              data=conn.recv(1024)
              ipdnodos=data.decode()
              listaDNodos=json.loads(ipdnodos)

          #threading.Thread(target=self.listenThread, args=()).start()
          #threading.Thread(target=self.fix_fingers, args=()).start()
          #threading.Thread(target=self.stabilize, args=()).start()
          #threading.Thread(target=self.update_successors, args=()).start()
          
          #nodo=Node(int(decodificado[13:len(decodificado)-1])+1)
          #data=s.recv(1024)
          #data=data.decode()
          #listaDNodos=json.loads(data)
          

    def completar_nodos(self):
        HOSTPORT=12345
        
        for IpDnodo in self.listaDNodos:
          if self._ultimoidAsignado==0:
            self._predecesor=self.listaDNodos[len(self.listaDNodos)-1]
            if self._ultimoidAsignado+1<len(self.listaDNodos):
                self._sucesor=self.listaDNodos[self._ultimoidAsignado+1]
          else: 
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

              s.connect((IpDnodo, HOSTPORT))
              
              s.sendall(b"{}".__format__(self.listaDNodos[self._ultimoidAsignado-1]))
              if self._ultimoidAsignado<len(self.listaDNodos)-1:
                s.sendall(b"{}".__format__(self.listaDNodos[self._ultimoidAsignado+1]))
              else:
                s.sendall(b"{}".__format__(self.listaDNodos[0]))
              s.close()
          self._ultimoidAsignado+=1
        

    def pasarInfoDlider(self):
        for ipnodo in self.listaDNodos:
            data=json.dumps(self.listaDNodos)
            listadIps=data.encode()
            self.server.send(listadIps)     

if __name__ == '__main__':
 nombre_equipo = socket.gethostname()
 direccionIP_equipo = socket.gethostbyname(nombre_equipo)
 nodo=Node(direccionIP_equipo)
 nodo.start_comunication()
 

def join(id):
  controlDNodos[id]=True
  i=id
  i+=1
  while not controlDNodos[i]:
      i+=1
      if i==64:
          i=0

  controlDNodos[id]._sucesor=controlDNodos[id]
  i=id
  i-=1
  while not controlDNodos[i]:
      i-=1
      if i==0:
          i=64
    
  controlDNodos[id]._predecesor=controlDNodos[i]
  
  #updatefingertables(id)
  

def leave(id):
    listaDNodos[id]._predecesor._sucesor=listaDNodos[id]._sucesor
    listaDNodos[id]._sucesor._predecesor=listaDNodos[id]._predecesor
    controlDNodos[id]=False
    listaDNodos[id]._sucesor._keys.extend(listaDNodos[id]._keys)
    #updatefingertables(id)






