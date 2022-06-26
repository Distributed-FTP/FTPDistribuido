import os
import csv
import time
import datetime
from uuid import getnode as get_mac
import sys,subprocess
import os
import socket
import json
import threading
from subprocess import Popen, PIPE 
import re
import redis
from setuptools import Command 
from ping3 import ping


#Si el nodo i de la red esta activo se guarda True, esta lista servira para comprobar constantemente 
# si un nodo se desactivo o si un nodo se activo
controlDNodos=[]
SystemaEstable=True

#esta variable es para saber el estado en que se encuentra chord , si buscando un elemento , si anadiendo un elemento o si esta reorganizando
#los nodos
estadoDChord=None

def check_ping(hostname):
  resp=ping(hostname)
  if resp==False or resp==None:
    return False
  else:
    return True

class Node:
    def __init__(self,ip):
        self._id=None
        self._ip=ip
        self._keys=dict() #cada llave de un archivo esta conformada por el id del nodo al que perteneces concatenado con una funcion hash , ya que pueden haber dos archivos con el mismo nombre y no ser el mismo.
                         #por cada llave se guarda una lista con los id de los nodos en los que esta replicado el elemento
        self._predecesor=None
        self._sucesor=None
        self.fingertable=dict()
        self._ipLider=None
        self.hayLider=False
        self.listaDNodos=[]
        self.peticiones=[]  # aqui se guardan las peticiones de los clientes
       

        #Todo Nodo debe saber si es el lider , en caso de que lo sea debe realizar acciones especificas
        # self.fingertable = {((self._id+(i**2))%2**160) : self._ip for i in range(160)} #!ID:IP

    #def agregarpeticion(self):
     #  self.peticiones

    #def procesapeticion(self):
       #for peticion in self.peticiones:
        # if peticio


    def procesapeticiones(self):
      
      while SystemaEstable :
          peticion=self.procesapeticion()
          if peticion=="subir":
           threading.Thread(target=self.ejecutaSubida(), args=()).start()
          if peticion=="descargar":
           threading.Thread(target=self.ejecutaDescarga(), args=()).start()
          if peticion=="editar":
           threading.Thread(target=self.ejecutaEdicion(), args=()).start()
          

    #def procesapeticion(self):
          

    def recepcionarpeticiones(self):
            servidor = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            servidor.bind((self._ip,8007))
            servidor.listen()
            while True:
             conn, addr = servidor.accept() # Establecemos la conexión con el cliente
             data=conn.recv(1024)
             self._peticiones.append(data)

       
    def start_comunication(self):
        try:
            #pin=check_ping('192.168.128.254')
            #MinNodos=1   #esta variable solo es para saber el minimo de nodos que deben estar en el sistema para levantarlo en un principio 
            self._ipLider=self._ip
            self._id=0
            self.listaDNodos.append(self._ip)
            controlDNodos.append(True)
            BUFFER_SIZE=1024
            self.server = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self._ip,12345))
            self.server.listen()
            while(MinNodos>0):
             #self.server.settimeout(1000)
             conn, addr = self.server.accept() # Establecemos la conexión con el cliente 
             if conn:   
            # Recibimos bytes, convertimos en str
               data = conn.recv(BUFFER_SIZE)
            # Verificamos que hemos recibido datos
               if not data:
                 continue
               
               if data.decode('utf-8')=="Nodo Soy FTP":
                 print(data)
                 print('[*] Datos recibidos: {}'.format(data.decode('utf-8'))) 
                 conn.send(bytes(str(len(self.listaDNodos)),'utf8')) # Hacemos echo convirtiendo de nuevo a bytes
                 self.listaDNodos.append(addr[0])
                 pin=check_ping(addr[0])
                 conn.close()
                 MinNodos-=1
               else:
                continue
                #conn.settimeout(10000)
                #conn,addr = self.server.accept() # Establecemos la conexión con el cliente
                
                #ahora asignamos los sucesores , predecesores y fingertables
            self.server.close()
            self.creaFingertable()
            self.completar_nodos()
            self.pasarInfoDlider() 

        except socket.error:
#           # prRed('Error abriendo socket') 
            return
        
       
        SERVER_HOST = 'DESKTOP-P0GKUJT'
        SERVER_PORT = 12345

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

          s.connect((SERVER_HOST, SERVER_PORT))
          #nombre_d_equipo=socket.gethostname()
          #ip=socket.gethostbyname(nombre_d_equipo)
          s.send(b"Nodo Soy FTP")
          #s.send(b"{}".__format__(ip))
          data = s.recv(1024)
          self._id=int(data.decode('utf-8'))
          s.close()

        SERVER_PORT= 8000  #Puerto para actualizar la informacion de los nodos al principio
        self.server = socket.socket(
               socket.AF_INET, socket.SOCK_STREAM)
          
        self.server.bind((self._ip,SERVER_PORT))
        self.server.listen()
        conn, addr = self.server.accept() # Establecemos la conexión con el cliente
        
        with conn:
              datapredecesor = conn.recv(BUFFER_SIZE)
              ippredecesor=datapredecesor.decode('utf-8')
              self._predecesor=int(ippredecesor)
              datasucesor = conn.recv(BUFFER_SIZE)
              ipsucesor=datasucesor.decode('utf-8')
              self._sucesor=int(ipsucesor)
              data=conn.recv(1024)
              self._ipLider=data.decode('utf-8')
              data=conn.recv(1024)
              ipdnodos=data.decode('utf-8')
              listaDNodos=json.loads(ipdnodos)
              data=conn.recv(1024)
              NodosActivos=data.decode('utf-8')
              listaDNodos=json.loads(NodosActivos)
              conn.close()
        self.creaFingertable()
          
        print("Sistema listo para Comenzar")
        self.run()

          #nodo=Node(int(decodificado[13:len(decodificado)-1])+1)
          #data=s.recv(1024)
          #data=data.decode()
          #listaDNodos=json.loads(data)
          
    def creaFingertable(self):
         for i in range(6):
            key=self._id+pow(2,i)
            self.fingertable.setdefault(key,key)

    def macDNodo(self):
      mac= os.system('arp -n ' + str(self._ip))
      return mac
  
    #def liderinactivo(self):
         

    def run(self):  ###Arreglar metodo , hay casos en los que un nodo puede dar ping y el servidor no estar levantado
      
     while True:

      if self._ipLider==self._ip:
         while self._ipLider==self._ip:
          self.stabilize()
      else:
         if not check_ping(self._ipLider):
          self.hayLider=False
          threading.Thread(target=self.esperaActualizacionDlider, args=()).start()
          threading.Thread(target=self.seleccionalider, args=()).start()
          
         if self._ipLider!=self._ip:
          self.actividad()
                               
         
            #Antes de continuar todos tienen que saber quien es el lider 

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
          while not self.hayLider:
           conn, addr = self.server.accept() # Establecemos la conexión con el cliente
           if conn:
            data=conn.recv(1024)
            if data.decode('utf-8')=="Soy lider d nodos":
                hayLider=True
                self._ipLider=addr[0]
            elif data.decode('utf-8')=="Eres el lider":
                self._ipLider=self._ip
                hayLider=True     
           conn.close()       
            
    def stabilize(self):
    
       ip=self._ip
       while ip[len(ip)-1]!='.':
          ip=ip[0:len(ip)-2]
       
       with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
         for i in range(2,255):
           if self._ip!= ip+str(i): 
              if self.listaDNodos.count(ip+str(i))==1:
                 try:
                    s.connect((ip+str(i), 8003))
                    s.send(b"Estas activo?")
                    data=s.recv(1024)
                    if data.decode('utf-8')=="estoy":
                       continue
                    else:
                      self.leave(self.listaDNodos.index(ip+str(i)))
                    s.close()
                 except:
                    self.leave(self.listaDNodos.index(ip+str(i)))                    
              elif check_ping(ip+str(i)):
                      try :
                        s.connect(ip+str(i),8003)
                        s.send(b"Estas activo?")
                        data=s.recv(1024)
                        if data.decode('utf-8')=="estoy":
                            self.join(ip+str(i))
                        s.close()
                      except:
                         s.close()
                         continue
              s.close()

    def seleccionalider(self):
         SERVER_PORT=8002
         countpos=0

         for ipnodo in self.listaDNodos:
            if ipnodo==self._ip:
                countpos+=1
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                 while countpos<len(self.listaDNodos):
                  try:
                   s.connect((self.listaDNodos[countpos], SERVER_PORT))
                   s.send(b"Soy lider d nodos")
                   s.close()
                   countpos+=1
                  except:
                     print("Hay que estabilizar antes de que sigan funcionando los demas nodos, hay al menos uno que se desconecto")
                     
                 s.connect((self._ip, SERVER_PORT))
                 s.send(b"Eres el lider")
                 s.close()

            elif check_ping(ipnodo):
                break
            countpos+=1

    def leave(self,id):
     controlDNodos[id]=False
     ip_predecesor=get_predecesor(self.listaDNodos[id])
     ip_sucesor=get_sucesor(self.listaDNodos[id])
     actualizasucesor(ip_predecesor,ip_sucesor)
     actualizapredecesor(ip_sucesor,ip_predecesor)
     #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
      

      #self.updatefingertables(id,ip_sucesor,"leave")


    def actividad(self):
        server = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self._ip,8003))
        server.listen()
        conn, addr = self.server.accept()
    
    def completar_nodos(self):
            HOSTPORT=8000
          #if len(self.listaDNodos)==1:
            #self._predecesor=self.listaDNodos[len(self.listaDNodos)-1]
            #if self._ultimoidAsignado+1<len(self.listaDNodos):
           #     self._sucesor=self.listaDNodos[self._ultimoidAsignado+1]
          #else: 
            
            
            count=0
            for IpDnodo in self.listaDNodos:
               if count==0:
                 self._predecesor=self.listaDNodos[len(self.listaDNodos)-1]
                 self._sucesor=self.listaDNodos[count+1]
                 self._ipLider=self._ip
               else:
                try:
                 with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                  s.connect((IpDnodo, HOSTPORT))
                  s.sendall(b"{}".__format__(str(self.listaDNodos[count-1]).encode('utf-8')))
                  if count<len(self.listaDNodos)-1:
                    s.sendall(b"{}".__format__(str((count+1)).encode('utf-8')))
                  else:
                    s.sendall(b"{}".__format__(str(self.listaDNodos[0]).encode('utf-8')))
                  s.close()
                  controlDNodos.append(True)
                except:
                  print("error")
               count+=1
        
    def pasarInfoDlider(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

         HOSTPORT=8000   
         count=0
        
         for ipnodo in self.listaDNodos:
            if count==0:
                continue
            s.connect((ipnodo, HOSTPORT))
            data=json.dumps(self.listaDNodos)
            listadIps=data.encode('utf-8')
            s.send(listadIps)
            data=json.dumps(controlDNodos)
            NodosActivos=data.encode('utf-8')
            s.send(NodosActivos)
            s.close()
            count+=1    

    #def join(self,id,ip):
        


        #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
         

         #  try:
          #  s.connect((ip, 8004))
           # s.send(b"soy el lider")
           # data=s.recv(1024)
           # if data.decode('utf-8')=="Nodo Soy FTP":
                
           #     data=json.dumps(self.listaDNodos)
           #     listadIps=data.encode()
           #     s.send(listadIps)
           #     if self.listaDNodos.count(ip)==0:
           #       s.send(b"eres nuevo")
           #     else:
           #       s.send(b"no eres nuevo")

            #s.close()
           #except:
          #  print("El nodo {} no es servidor".format(ip))

    #def reajustarNodo():
      
    def escucha(self):
         servidor = socket.socket(
               socket.AF_INET, socket.SOCK_STREAM)
          
         servidor.bind((self._ip,8007))
         servidor.listen()
         conn, addr = self.server.accept()
         COMMAND=conn.recv(1024)
         if COMMAND.decode('utf-8')=="dime predecesor":
                  conn.send(self._predecesor)
         elif COMMAND.decode('utf-8')=="dime sucesor":
                    conn.send(self._sucesor)
         elif COMMAND.decode('utf-8')=="actualiza predecesor":
                  COMMAND=conn.recv(1024)
                  self._predecesor=COMMAND.decode('utf-8')
         elif COMMAND.decode('utf-8')=="actualiza sucesor":
                  COMMAND=conn.recv(1024)
                  self._sucesor=COMMAND.decode('utf-8')

    
     

    def updatefingertables(self,id,evento):
          with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
           if evento=="leave":
            while(id>=0) :
             s.connect((self.listaDNodos[id], 8006))
             s.send(b"leave {}".__format__(id.encode()))
             s.close()
             id-=1
           else:
             while(id>=0) :
              s.connect((self.listaDNodos[id], 8006))
              s.send(b"join {}".__format__(id.encode()))
              s.close()
              id-=1

def get_predecesor(ip):
     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
            s.connect((ip, 8005))
            s.send(b"dime predecesor")
            data=s.recv(1024)
            s.close()
            return data.decode('utf-8')

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
            return data.decode('utf-8')
           

if __name__ == '__main__':
 nombre_equipo = socket.gethostname()
 direccionIP_equipo = socket.gethostbyname(nombre_equipo)
 nodo=Node(direccionIP_equipo)
 nodo.start_comunication()
   
  
  








