#from typing_extensions import Self
from base64 import encode
from copyreg import constructor
from itertools import count
from pickle import TRUE
from typing_extensions import Self
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
hayLider=False
#esta variable es para saber el estado en que se encuentra chord , si buscando un elemento , si anadiendo un elemento o si esta reorganizando
#los nodos
estadoDChord=None

#Esta lista es para guardar la relacion IP : Id de los nodos del sistema


def ping(x):
 if len(sys.argv)!=2:
     print("psweep.py 10.0.0")
     return False
 else:
     cmdping="ping -cl "+sys.argv[1]

     
     p = subprocess.Popen(cmdping+str(x),shell=True,stderr=subprocess.PIPE)

     while True:
             out=p.stderr.read(1)
             if out=='' and p.poll()!=None:
                 break
             if out != '':
                 return True
                 #sys.stdout.write(out)
                 #sys.stdout.flush()
 return False

class Node:
    def __init__(self,ip):
        self._id=None
        self._ip=ip
        self._keys=list()  #Para cada nodo hay que saber las llaves que tiene asociadas en cada momento
        self._predecesor=None
        self._sucesor=None
        self.fingertable=dict()
        self._ipLider=None
        self._ultimoidAsignado=0
        self.listaDNodos=[]
          
        #Todo Nodo debe saber si es el lider , en caso de que lo sea debe realizar acciones especificas
        # self.fingertable = {((self._id+(i**2))%2**160) : self._ip for i in range(160)} #!ID:IP


    def start_comunication(self):

       #if mac=='94-E2-3C-07-91-08':

        try:
            self._ipLider=self._ip
            self._id="0"
            self.listaDNodos.append("{}".format(self._ip))
            controlDNodos.append(True)
            ultimoIdAsignado=0
            BUFFER_SIZE=1024
            self.server = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self._ip,12345))
            self.server.listen(10000)
            self.server.settimeout(15000)
            #self.server.settimeout(1000)
            conn, addr = self.server.accept() # Establecemos la conexión con el cliente 
            if conn: 
              while True:
                
            # Recibimos bytes, convertimos en str
               data = conn.recv(BUFFER_SIZE)
            # Verificamos que hemos recibido datos
               #if not data:
               # break
               #else:
               if data.decode('utf-8')=="Nodo Soy FTP":
                 print(data)
                 print('[*] Datos recibidos: {}'.format(data.decode('utf-8'))) 
                 conn.send(bytes(str(self._id),'utf8')) # Hacemos echo convirtiendo de nuevo a bytes
                 self.listaDNodos.append("{}".format(addr[0]))
                 conn.close()
                #else:
               conn.settimeout(10000)
               conn,addr = self.server.accept() # Establecemos la conexión con el cliente
                
                #ahora asignamos los sucesores , predecesores y fingertables
              self.creaFingertable()
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
          self.creaFingertable()
          
        print("Sistema listo para Comenzar")
        self.run()

          #nodo=Node(int(decodificado[13:len(decodificado)-1])+1)
          #data=s.recv(1024)
          #data=data.decode()
          #listaDNodos=json.loads(data)
          
    def creaFingertable(self):
         for i in range(8):
            key=self._id+pow(2,i)
            self.fingertable.setdefault(key,key)

    def run(self): 
      SERVER_HOST = None
      SERVER_PORT = 8002
      
      if self._ipLider==self._ip:
         while self._ipLider==self._ip:
          threading.Thread(target=self.actualizaNodoLider, args=()).start()
          threading.Thread(target=self.stabilize, args=()).start()
          threading.Thread(target=self.buscaNuevosNodos, args=()).start()
      else:
         
         if not ping(self._ipLider):

          hayLider=False
          self.seleccionalider()
          threading.Thread(target=self.esperaActualizacionDlider, args=()).start()

         #threading.Thread(target=self.buscaLider, args=()).start()
         #threading.Thread(target=self.stabilize, args=()).start()
         #threading.Thread(target=self.listenThread, args=()).start()
         #if self._soyLider
          #print("ya")
         
         # threading.Thread(target=self.fix_fingers, args=()).start()
         
         # threading.Thread(target=self.update_successors, args=()).start()
    
    def esperaActualizacionDlider(self):
          SERVER_PORT = 8002

          self.server = socket.socket(
               socket.AF_INET, socket.SOCK_STREAM)
          
          self.server.bind((self._ip,SERVER_PORT))
          self.server.listen()
          while not hayLider:
           conn, addr = self.server.accept() # Establecemos la conexión con el cliente
           if conn:
            data=conn.recv(1024)
            if data.decode()=="Soy lider d nodos":
                hayLider=True
                self._ipLider=addr[0]     
           conn.close()       
            

    def actualizaNodoLider(self):
      
       with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
         
         idnodo=0
         for nodoip in self.listaDNodos:
          if controlDNodos[idnodo]:
           s.connect((nodoip, 8002))
           s.send(b"{}".__format__(encode(self._id)))
           s.close()
          idnodo+=1

    def seleccionalider(self):
         SERVER_PORT=8002
         countpos=0

         for ipnodo in self.listaDNodos:
            if ipnodo==self._ip:
                countpos+=1
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                 while countpos<len(self.listaDNodos):

                   s.connect((self.listaDNodos[countpos], SERVER_PORT))
                   s.send(b"Soy lider d nodos")
                   s.close()
                   countpos+=1

            elif ping(ipnodo):
                break
            countpos+=1
                      

    def stabilize(self):  #Metodo para que el lider identifique nodos nuevos que quieran conectarse o para reconectar a alguno que estaba inactivo
            idnodo=0
            for ipnodo in self.listaDNodos:
              if ipnodo!=self._ip:
                 if ping(ipnodo):
                   if not controlDNodos[idnodo]:
                      self.join(ipnodo,idnodo)
                 elif controlDNodos[idnodo]:
                     self.leave(ipnodo,idnodo)
                    
              idnodo+=1

    
         
    
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
          controlDNodos.append(True)
          self._ultimoidAsignado+=1

    def buscaNuevosNodos(self):  #Falta completar el funcionamiento , que se una al sistema y que actualice a los otros nodos de la info del lider
      nuevosnodos=[]
      if len(sys.argv)!=2:
          print("psweep.py 10.0.0")
          
      else:
       cmdping="ping -cl "+sys.argv[1]

       for x in range(2,255):
        p = subprocess.Popen(cmdping+str(x),shell=True,stderr=subprocess.PIPE)

        while True:
             out=p.stderr.read(1)
             if out=='' and p.poll()!=None:
                 break
             if out != '':
                 if self.listaDNodos.count(out)==0:
                     nuevosnodos.append(out)
                 #sys.stdout.write(out)
                 #sys.stdout.flush()
        
             

       

    def pasarInfoDlider(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

         HOSTPORT=12345   
         count=0
        
         for ipnodo in self.listaDNodos:
            if count==0:
                continue
            s.connect((ipnodo, HOSTPORT))
            data=json.dumps(self.listaDNodos)
            listadIps=data.encode()
            s.send(listadIps)
            s.close()
            count+=1     

    def join(self,id,ip):
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
         
           try:
            s.connect((ip, 8004))
            s.send(b"soy el lider")
            data=s.recv(1024)
            if data.decode()=="Nodo Soy FTP":
                
                data=json.dumps(self.listaDNodos)
                listadIps=data.encode()
                s.send(listadIps)
                if self.listaDNodos.count(ip)==0:
                  s.send(b"eres nuevo")
                else:
                  s.send(b"no eres nuevo")

            s.close()
           except:
            print("El nodo {} no es servidor".format(ip))

    #def reajustarNodo():
  

    def leave(self,id):
     controlDNodos[id]=False
     ip_predecesor=get_predecesor(self.listaDNodos[id])
     ip_sucesor=get_sucesor(self.listaDNodos[id])
     actualizasucesor(ip_predecesor,ip_sucesor)
     actualizapredecesor(ip_sucesor,ip_predecesor)
    #updatefingertables(id)

def get_predecesor(ip):
     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
            s.connect((ip, 8005))
            s.send(b"dime predecesor")
            data=s.recv(1024)
            s.close()
            return data.decode()

def actualizasucesor(ip,nuevo_sucesor):
          with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
            s.connect((ip, 8005))
            s.send(b"actualiza sucesor")
            
            s.send(b'{}'.__format__(nuevo_sucesor.encode()))
            s.close()
            
def actualizapredecesor(ip,nuevo_predecesor):
          with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
            s.connect((ip, 8005))
            s.send(b"actualiza predecesor")
            
            s.send(b'{}'.__format__(nuevo_predecesor.encode()))
            s.close()

def get_sucesor(ip):
     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
            s.connect((ip, 8005))
            s.send(b"dime sucesor")
            data=s.recv(1024)
            s.close()
            return data.decode()
            
            


if __name__ == '__main__':
 nombre_equipo = socket.gethostname()
 direccionIP_equipo = socket.gethostbyname(nombre_equipo)
 nodo=Node(direccionIP_equipo)
 nodo.start_comunication()
   
  #updatefingertables(id)
  








