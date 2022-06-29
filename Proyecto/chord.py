from errno import ELIBBAD
import hashlib
import os
import csv
from posixpath import split
import time
import datetime
from typing_extensions import Self
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
SistemaEstable=True

#esta variable es para saber el estado en que se encuentra chord , si buscando un elemento , si anadiendo un elemento o si esta reorganizando
#los nodos
estadoDChord=None


def check_ping(hostname):
  resp=ping(hostname)
  if resp==False or resp==None:
    return False
  else:
    return True

#Recordar pasar la peticiones a los demas nodos por si el lider se cae

class Node:
    def __init__(self,ip):
        self._id=None
        self._ip=ip
        self._archivos=list()  #se guardaran los archivos que esten almacenados en este nodo , mas alla que sea una replica . 
        self._archivosDelSistema=dict()  #Aqui se guardara el hash del archivo y en que nodos esta replicaado
        self._predecesor=None
        self._sucesor=None
        self.fingertable=dict()
        self._ipLider=None
        self.hayLider=False
        self.listaDNodos=[]
        self.peticiones=[]  # aqui se guardan las peticiones de los clientes
        self.ElliderLoLLama=False
        self.sistemaEstable=False
        self.finishCountDown=False

        #Todo Nodo debe saber si es el lider , en caso de que lo sea debe realizar acciones especificas
        # self.fingertable = {((self._id+(i**2))%2**160) : self._ip for i in range(160)} #!ID:IP

    #def agregarpeticion(self):
     #  self.peticiones

    #def procesapeticion(self):
       #for peticion in self.peticiones:
        # if peticio

    def countdown(self,num_of_secs):
     while num_of_secs:
        m, s = divmod(num_of_secs, 60)
        min_sec_format = '{:02d}:{:02d}'.format(m, s)
        print(min_sec_format, end='/r')
        time.sleep(1)
        num_of_secs -= 1
        
     self.finishCountDown=True
        

    def pidelo(self,hash):
         nodosQueLotienen= self._archivosDelSistema[hash]
         for idnodo in nodosQueLotienen:
           if self.listaDNodos[idnodo]==True:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
                     s.connect(self.listaDNodos[idnodo],8008)
                     s.send(b"dame archivo")
                     s.send("{}".format(hash))
                      ####Pedir ARCHIVO
                     archivo=s.recv(1024)
                       #Retornar el archivo
                     return

    def ejecutaDescarga(archivo,self):
           
           codigoHash=hashlib.sha256(archivo).hexdigest()
           if self._archivos.count(codigoHash)==1:
               ####Busca el archivo y retornarlo
               return archivo
           else:
             return self.pidelo()
           

    def recibePeticionesdelSistema(self):
        server = socket.socket(
               socket.AF_INET, socket.SOCK_STREAM)
          
        server.bind((self._ip,8008))
        server.listen()
        conn, addr = server.accept()
        if conn:
            data=conn.recv(1024)
            data=data.decode('utf-8')
            if data=='Inestable' and self.listaDNodos.count(addr[0])==1 and controlDNodos[self.listaDNodos.index(addr[0])]==True:
                SystemaEstable=False
                conn.close()
            elif data=="dame sucesor":
                 conn.send("{}".format(self._sucesor))
            elif data=="Save":
                 #######Aqui hay que recibir el archivo y guardarlo
                 ##if se guarda bien entonces
                 hashdelArchivo= hashlib.sha256().hexdigest()
                 self._archivos.append(hashdelArchivo)
                 conn.send(b"Save")
                 #ELse:
                 conn.send("")
            elif data=="Save Original":
                 #######Aqui hay que recibir el archivo y guardarlo
                 ##if se guarda bien entonces
                 
                 hashdelArchivo= hashlib.sha256().hexdigest()
                 self._archivos.append(hashdelArchivo)
                 conn.send(b"Save Original")
                 #ELse:
                 conn.send("")
            elif data=="Actualiza Archivos":
                  data=conn.recv(1024).decode('utf-8')
                  self._archivosDelSistema.keys= json.loads(data)
                  data=conn.recv(1024).decode('utf-8')
                  self._archivosDelSistema.values= json.loads(data)
            elif data=="edita Archivo":
                  hashAntiguo=conn.recv(1024).decode('utf-8')
                  self._archivos.remove(hashAntiguo)
                  #Remueve el archivo
                  data=conn.recv(1024).decode('utf-8')
                  hash=hashlib.sha256(data).hexdigest()
                  #GuardarArchivo
                  #Retroceder respuesta
                  
                  self._archivos.append(hash)
            elif data=="dame archivo":
                  hashAntiguo=conn.recv(1024).decode('utf-8')
                  ##Retorna el archivo con el hash
                  
        conn.close()


    def ejecutaSubida(self,archivo):  #Este metodo escoge el nodo que lo almacenara y le envia un mensaje para que lo guarde
          if self._archivos.count(hashlib.sha256(archivo).hexdigest())==0:
           with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
             ip=None
             cantidadDArchivos=0
             count=0
             for nodo in self.listaDNodos:
                if controlDNodos[count]==True:
                   try:
                    s.connect(nodo,8008)
                    s.send(b"Archivos")
                    data=s.recv(1024)
                    if count==0:
                       ip=nodo
                       cantidadDArchivos= int(data.decode('utf-8'))
                    elif int(data.decode('utf-8'))<cantidadDArchivos:
                        ip=nodo
                        cantidadDArchivos=int(data.decode('utf-8'))
                   except:
                     SistemaEstable=False
                     return False
                count+=1
                s.close()
             try:
               s.connect(ip,8008)
               s.send(b'Save Original')
               s.sendfile(archivo)
               data=s.recv(1024)
               if not data.decode('utf-8')=="Save Original":
                   return False
               s.close()
               hashdelArchivo= hashlib.sha256(archivo).hexdigest()
               self._archivos.append(hashdelArchivo)
               self._archivosDelSistema.setdefault(hashdelArchivo,[ip])
               cantidadDReplicas=4
               while cantidadDReplicas>0:#Replicacion
                s.connect(ip,8008)
                s.send(b'dame sucesor')
                data=s.recv(1024)
                ip=data.decode('utf-8')
                s.close()
                s.connect(ip,8008)
                s.send(b'Save')          #Hacer que los nodos confirmen cuando hayan realizado el almacenamiento
                s.sendfile(archivo)
                data=s.recv(1024)
                if not data.decode('utf-8')=="Save":
                   return False
                valueKey=self._archivosDelSistema.get(hashdelArchivo)
                valueKey.append(ip)
                self._archivosDelSistema.update(hashdelArchivo,valueKey)
                s.close()
                cantidadDReplicas-=1
             except:
                SistemaEstable=False
                return False
            
             return True

          else:
            print("El archivo ya existe en el sistema")

    def actualizaNodosDSistema(self):
          i=0
          with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
           for nodo in self.listaDNodos:
             if controlDNodos[i]==True:
                s.connect(nodo,8008)
                s.send(b'Actualiza Archivos')
                send_list=json.dumps(self._archivosDelSistema.keys())
                s.send(b"{}".__format__(send_list.encode('utf-8')))
                send_list=json.dumps(self._archivosDelSistema.values())
                s.send(b"{}".__format__(send_list.encode('utf-8')))
                s.close()
             i+=1

    def ejecutaEdicion(self,archivo,archivonuevo):
          nodos=self._archivosDelSistema[archivo]
          with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
             count=0
             for nodo in nodos:
                if controlDNodos[nodo]==True:
                  try:
                    s.connect(self.listaDNodos[nodo],8008)
                    s.send(b"edita Archivo")
                    hashAntiguo=None
                    hashnuevo=None
                    #s.send ####Enviar el has del archiv que se va a cambiar
                    #s.send ###Enviar el archivo 
                    data=s.recv(1024)
                    data=data.decode('utf-8')
                    if data=="Accepted":
                     nodosDArchivoAntiguo=self._archivosDelSistema[hashAntiguo]
                     nodosDArchivoAntiguo=nodosDArchivoAntiguo-nodo
                     self._archivosDelSistema[hashAntiguo]=nodosDArchivoAntiguo
                     if self._archivosDelSistema[hashAntiguo].count==0:
                         self._archivosDelSistema[hashAntiguo]=self._archivosDelSistema[hashAntiguo].append(hashnuevo)

                     if count==0:
                        self._archivosDelSistema.setdefault(hashnuevo,[nodo])
                     else:
                        self._archivosDelSistema[hashnuevo]= self._archivosDelSistema[hashnuevo].append(nodo)

                  except:
                    SistemaEstable=False
                count+=1


    def procesapeticiones(self):

      threading.Thread(target=self.countdown(), args=()).start()   #Este temporizador es para mirar estabilizar el sistema cada un tiempo determinado
      threading.Thread(target=self.recibePeticionesdelSistema(), args=()).start()
      
      while SistemaEstable and not self.finishCountDown:
         
         if self._ip==self._ipLider:
           if len(self.peticiones)>0:
             peticion=self.peticiones[0]
             if peticion=="subir":
                self.ejecutaSubida(peticion)
                self.actualizaNodosDSistema()
             if peticion=="descargar":
               self.ejecutaDescarga(peticion)

             if peticion=="editar":
               self.ejecutaEdicion(peticion,peticion)       

    def recepcionarpeticiones(self):
            servidor = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            servidor.bind((self._ip,8007))
            servidor.listen()
            while True:
             conn, addr = servidor.accept() # Establecemos la conexión con el cliente
             data=conn.recv(1024)
             self._peticiones.append(data)
          
    def creaFingertable(self):
         for i in range(6):
            key=self._id+pow(2,i)
            self.fingertable.setdefault(key,key)
         
    def recibiendoSenalDlider(self):
        SERVER_PORT= 8003  
        self.server = socket.socket(
               socket.AF_INET, socket.SOCK_STREAM)
          
        self.server.bind((self._ip,SERVER_PORT))
        self.server.listen()
        conn, addr = self.server.accept() # Establecemos la conexión con el cliente
        if conn:
             data=conn.recv(1024)
             if data.decode('utf-8')=="Estas activo?":
              conn.send(b'Nodo Soy FTP')
              self.ElliderLoLLama=True
              self._ipLider=addr[0]
              conn.close()
  
    def buscalider(self):
         threading.Thread(target=self.conectaNodosIndep(), args=()).start()
         ip=self._ip
         number=''
         while ip[len(ip)-1]!='.':
            number=ip[len(ip)-1]+number
            ip=ip[0:len(ip)-2]
         number=int(number)
         pos=2
         while pos<=number:
           if pos==number:
                 self._ipLider=self._ip
                 self.id=0
                 self.listaDNodos.append(self._ip)
                 controlDNodos.append(True)
                 self._sucesor=self._ip
                 self._predecesor=self._ip

           if check_ping(ip+str(pos)):
              break
           pos+=1   
#
    def run(self):  
      
     while True:
      
      if not self.sistemaEstable:

       if self._ipLider==self._ip:
         while self._ipLider==self._ip:
          self.stabilize()
          self.updatefingertables()
          self.sistemaEstable=True
       elif self._ipLider==None:
              threading.Thread(target=self.recibiendoSenalDlider, args=()).start()
              temporizador=7
              while True:
                if self.ElliderLoLLama:
                  break
                if temporizador==0:
                  self.buscalider()
                  break
                else: 
                   time.sleep(1)
                   temporizador-=1
        
       elif not check_ping(self._ipLider):
          self.hayLider=False
          threading.Thread(target=self.esperaActualizacionDlider, args=()).start()
          threading.Thread(target=self.seleccionalider, args=()).start()
       else:
          self.escucha()
      else:
          self.procesapeticiones()


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
                    if data.decode('utf-8')=="Nodo Soy FTP":
                      if not controlDNodos[self.listaDNodos.index(ip+str(i))]:
                         self.join(ip+str(i))
                      else: 
                       continue
                    else:
                      self.leave(self.listaDNodos.index(ip+str(i)))
                    s.close()
                 except:
                    if controlDNodos[self.listaDNodos.index(ip)]:
                     self.leave(self.listaDNodos.index(ip+str(i)))                    
              elif check_ping(ip+str(i)):
                      try :
                        s.connect(ip+str(i),8003)
                        s.send(b"Estas activo?")
                        data=s.recv(1024)
                        if data.decode('utf-8')=="Nodo Soy FTP":
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
     ip_predecesor=self.get_predecesor(self.listaDNodos[id])
     ip_sucesor=self.get_sucesor(self.listaDNodos[id])
     self.actualizasucesor(ip_predecesor,ip_sucesor)
     self.actualizapredecesor(ip_sucesor,ip_predecesor)
     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        for nodo in self.listaDNodos:
           if nodo!=self.listaDNodos[id]:
             if controlDNodos[id]==True:             
              try:
               s.connect(nodo,8005)
               s.send(b"LEAVE")
               s.send(b"{}".__format__(str(id)))
               s.close()
              except:
                print("Otro nodo salio del sistema ,se vera cuando lleguemos a el")

    def join(self,ip):
        soyNuevo=True
        if not self.listaDNodos.count(ip)==1:   #Te estas reconectando           
           controlDNodos[self.listaDNodos.index(ip)]=True
           soyNuevo=False
        else:
          controlDNodos.append(True)
          self.listaDNodos.append(ip)
        sucesor=self.get_sucesor(ip)
        predecesor=self.get_predecesor(ip)
        self.actualizasucesor(ip,sucesor)
        self.actualizapredecesor(ip,predecesor)
        self.actualizasucesor(predecesor,ip)
        self.actualizapredecesor(sucesor,ip)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
         for nodo in self.listaDNodos:
           if nodo!=ip:             
             if controlDNodos[self.listaDNodos.index(nodo)]:
              try:
               s.connect(nodo,8005)
               s.send(b"JOIN")
               send_list=json.dumps(controlDNodos)
               s.send(b"{}".__format__(send_list.encode('utf-8')))
               send_list=json.dumps(self.listaDNodos)
               s.send(b"{}".__format__(send_list.encode('utf-8')))
               if soyNuevo:
                s.send(b"{}".__format__(str(self.listaDNodos.index(ip)).encode('utf-8')))
               else:
                s.send(b"")
               s.close()
              except:
                print("Otro nodo entro en el sistema ,se vera cuando lleguemos a el")
      
    def escucha(self):
         servidor = socket.socket(
               socket.AF_INET, socket.SOCK_STREAM)
          
         servidor.bind((self._ip,8005))
         servidor.listen()
         conn, addr = servidor.accept()
         COMMAND=conn.recv(1024)
         if COMMAND.decode('utf-8')=="actualiza predecesor":
                  COMMAND=conn.recv(1024)
                  self._predecesor=COMMAND.decode('utf-8')
         elif COMMAND.decode('utf-8')=="actualiza sucesor":
                  COMMAND=conn.recv(1024)
                  self._sucesor=COMMAND.decode('utf-8')
         elif COMMAND.decode('utf-8')=="LEAVE":
                  COMMAND=conn.recv(1024)
                  controlDNodos[int(COMMAND.decode('utf-8'))]=False
         elif COMMAND.decode('utf-8')=="JOIN":
                  COMMAND=conn.recv(1024)
                  controlDNodos= json.loads(COMMAND.decode('utf-8'))
                  COMMAND=conn.recv(1024)
                  self.listaDNodos=json.loads(COMMAND.decode('utf-8'))
                  COMMAND=conn.recv(1024)
                  self._id=int(COMMAND.decode('utf-8'))
                  self._ipLider=addr[0]
         elif COMMAND.decode('utf-8')=="UpdateFingertables":
                  for i in range(6):
                   id=pow(2,i)+self._id
                   self.fingertable[id]=self.sucesor(id)
         conn.close()

    def sucesor(id,self):
      pos=id+1
      if pos>=len(self.listaDNodos):
         pos=0
      while controlDNodos[pos]!=True:
        pos+=1
      return pos

    def updatefingertables(self): #Luego poner el crear fingertables
          
          with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            for nodo in self.listaDNodos:
              if controlDNodos[self.listaDNodos.index(nodo)]:
                 s.connect(nodo,8005)
                 s.send(b"UpdateFingertables")
                 data=s.recv(1024)
                 

    def get_predecesor(self,ip):
       pos=self.listaDNodos.index(ip)
       if pos==0:
         pos==len(self.listaDNodos)-1
       else:
         pos-=1
       while not check_ping(self.listaDNodos[pos]):
           if pos==0:
             pos==len(self.listaDNodos)-1
           else:
             pos-=1
       return self.listaDNodos[pos]

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

    def get_sucesor(self,ip):
       pos=self.listaDNodos.index(ip)
       if pos==len(self.listaDNodos)-1:
         pos==0
       else:
         pos+=1
       while not check_ping(self.listaDNodos[pos]):
           if pos==len(self.listaDNodos)-1:
             pos==0
           else:
             pos+=1
       return self.listaDNodos[pos]
           

if __name__ == '__main__':
 nombre_equipo = socket.gethostname()
 direccionIP_equipo = socket.gethostbyname(nombre_equipo)
 nodo=Node(direccionIP_equipo)
 nodo.run()
   
  
  








