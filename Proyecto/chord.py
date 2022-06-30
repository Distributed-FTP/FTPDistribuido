from base64 import decode
from errno import ELIBBAD
import hashlib
from multiprocessing.sharedctypes import Value
import os
import csv
from posixpath import split
from this import s
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
        self._archivosDelSistema=dict()  #Aqui se guardara el hash del archivo y en que otros nodos esta
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

    def countdown(self,num_of_secs):  #Temporizador que marca la revision de estabilidad del sistema
     while num_of_secs:
        m, s = divmod(num_of_secs, 60)
        min_sec_format = '{:02d}:{:02d}'.format(m, s)
        print(min_sec_format, end='/r')
        time.sleep(1)
        num_of_secs -= 1
        
     self.finishCountDown=True
        

    def buscaArchivo(self,hash,archivo,id,TipoDBusqueda):
      if TipoDBusqueda=="Descarga":  
      
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
         keys=self.fingertable.keys()
         if keys.__contains__(id):
            s.connect(self.listaDNodos[self.fingertable[id]],8008)
            s.send(b"dame archivo")
            s.send("{}".format(hash))
            archivo=s.recv(1024*5)
            s.close()
            return archivo
         else:
             idNodos= self.fingertable.values()
             pos=len(idNodos)-1
             value=idNodos[pos]
             while True:
                 if value<id:
                   break
                 else:
                    pos-=1
                    value=idNodos[pos]
                   
             s.connect(self.listaDNodos[value],8008)
             s.send(b"busca archivo")
             s.send("{}".format(id))
             s.send("{}".format(hash))
             return s.recv(1024).decode('utf-8')
      elif TipoDBusqueda=="Edicion":
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
         keys=self.fingertable.keys()
         if keys.__contains__(id):
            s.connect(self.listaDNodos[self.fingertable[id]],8008)
            s.send(b"edita archivo")
            s.send("{}".format(str(id)))
            s.send("{}".format(hash))
            s.sendfile(archivo)           
            s.close()
         else:
             idNodos= self.fingertable.values()
             pos=len(idNodos)-1
             value=idNodos[pos]
             while True:
                 if value<id:
                   break
                 else:
                    pos-=1
                    value=idNodos[pos]
                   
             s.connect(self.listaDNodos[value],8008)
             s.send(b"busca archivo para edicion")
             s.send("{}".format(id))
             s.send("{}".format(hash))
             s.sendfile(archivo)
             

    def ejecutaDescarga(idArchivo,self):
           codigoHash=idArchivo
           id=""
           while codigoHash[0]!=",":
                  id+=codigoHash[0]
                  codigoHash=codigoHash[1:len(codigoHash)-1]
           codigoHash=codigoHash[1:len(codigoHash)-1]
           
           if self._archivos.count(codigoHash)==1:
               with open(codigoHash, 'rb') as f:
                return f
           
           else:
             return self.buscaArchivo(codigoHash,None,id,"Descarga")
           

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
                 archivo=conn.recv(1024*5).decode('utf-8')
                 hash=hashlib.sha256(archivo).hexdigest()
                 with open(hash, "wb") as file:
                    file.write(archivo)
                 self._archivos.append(hash)
                 self._archivosDelSistema.setdefault(hash,[])
                 conn.send(b"Save")
                 conn.send(str(self._id)+","+hash)
            elif data=="Actualiza Archivos":
                  data=conn.recv(1024).decode('utf-8')
                  self._archivosDelSistema.keys= json.loads(data)
                  data=conn.recv(1024).decode('utf-8')
                  self._archivosDelSistema.values= json.loads(data)
            elif data=="edita archivo":
                  id=conn.recv(1024).decode('utf-8')
                  hash=conn.recv(1024).decode('utf-8')
                  idArchivo=id+","+hash
                  archivo=conn.recv(1024*5).decode('utf-8')
                  os.remove(idArchivo)
                  hashArchivoNuevo=hashlib.sha256(archivo).hexdigest()
                  with open(str(self.id)+","+hashArchivoNuevo, "wb") as file:
                    file.write(archivo)
                  
                  ###Editar el archivo y donde quiera que este replicado 
                  #Eliminar El archivo , Guardar EL actual e informar a los demas nodos que lo tienen
                  self._archivosDelSistema.setdefault(hashArchivoNuevo,self._archivosDelSistema[hash])    #anadir el nuevo hash junto a la lista de ips donde esta el archivo
                  self._archivos.remove(hash)
                  self._archivos.append(hashArchivoNuevo) ##Anadir el nuevo hash
                  
                  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
                   for replica in self._archivosDelSistema[hash]:
                    if replica!=self._ip:
                     if controlDNodos[self.listaDNodos.index(replica)]==True:
                         s.connect(replica,8008)
                         s.send(b"edita replica")
                         s.send(hash)
                         s.sendfile(archivo)

                  self._archivos.append(hash)
                  self._archivosDelSistema[hash]=hashArchivoNuevo
            elif data=="edita replica":
                  hash=conn.recv(1024).decode('utf-8')  
                  archivo=conn.recv(1024)
                  hashArchivoNuevo=hashlib.sha256(archivo).hexdigest()
                  with open(self._id+","+hashArchivoNuevo, "wb") as file:
                    file.write(archivo)
                  self._archivosDelSistema[hash]=hashArchivoNuevo  
                  self._archivosDelSistema.setdefault(hashArchivoNuevo,self._archivosDelSistema[hash])   
                  self._archivos.remove(hash)
                  self._archivos.append(hashArchivoNuevo) 

            elif data=="busca archivo":
                  id=int(conn.recv(1024).decode('utf-8'))
                  hash=conn.recv(1024).decode('utf-8')
                  archivo=self.buscaArchivo(hash,None,id,"Descarga")
                  conn.sendfile(archivo)
            elif data=="busca archivo para edicion":
                  id=int(conn.recv(1024).decode('utf-8'))
                  hash=conn.recv(1024).decode('utf-8')
                  archivo=conn.recv(1024).decode('utf-8')  ##Recibir el archivo de alguna forma
                  self.buscaArchivo(hash,archivo,id,"Edicion")
                  ###Mandar el archivo  conn.sendfile
            elif data=="dame archivo":
                  codigoHash=conn.recv(1024).decode('utf-8')
                  with open(codigoHash, 'rb') as f:
                   conn.sendfile(f)
            elif data=="actualiza Info":
                  hash=conn.recv(1024).decode('utf-8')
                  data=conn.recv(1024).decode('utf-8')
                  data=json.loads(data)
                  self._archivosDelSistema.setdefault(hash,data)
                  return True
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
               s.send(b'Save')
               s.sendfile(archivo)
               data=s.recv(1024)
               if not data.decode('utf-8')=="Save":
                   return False
               idDNodoARetornar=int(s.recv(1024).decode('utf-8'))
               s.close()
               NodosDondeEstaElarchivo=[]
               hashdelArchivo= hashlib.sha256(archivo).hexdigest()
               self._archivos.append(hashdelArchivo)
               NodosDondeEstaElarchivo.append(ip)
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
                NodosDondeEstaElarchivo.append(ip)
                s.close()
                cantidadDReplicas-=1
               for ip in NodosDondeEstaElarchivo:
                 s.connect(ip,8008)
                 s.send("actualiza Info")
                 s.send(hashdelArchivo)
                 s.send(json.dumps(NodosDondeEstaElarchivo))
                 s.close()        

             except:
                SistemaEstable=False
                return False
            
             return idDNodoARetornar

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

    def ejecutaEdicion(self,idArchivo,archivonuevo):
          codigoHash=idArchivo
          id=""
          while codigoHash[0]!=",":
                  id+=codigoHash[0]
                  codigoHash=codigoHash[1:len(codigoHash)-1]
          codigoHash=codigoHash[1:len(codigoHash)-1]
          
          self.buscaArchivo(codigoHash,archivonuevo,id,"Edicion")

    def procesapeticiones(self):

      idParaPeticion=0
      threading.Thread(target=self.countdown(), args=()).start()   #Este temporizador es para mirar estabilizar el sistema cada un tiempo determinado
      threading.Thread(target=self.recibePeticionesdelSistema(), args=()).start()
      
      while SistemaEstable and not self.finishCountDown:
         
         if self._ip==self._ipLider:
           
           while len(self.peticiones)>0:
               

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
         
         #threading.Thread(target=self.conectaNodosIndep(), args=()).start()
         
         ip=self._ip
         number=''
         while ip[len(ip)-1]!='.':
            number=ip[len(ip)-1]+number
            ip=ip[0:len(ip)-1]
         number=int(number)
         pos=2
        # while pos<=number:
         #  if pos==number:
         #        self._ipLider=self._ip
         #        self.id=0
         #        self.listaDNodos.append(self._ip)
         #        controlDNodos.append(True)
         #        self._sucesor=self._ip
         #        self._predecesor=self._ip

        #   if check_ping(ip+str(pos)):
         #     break
          # pos+=1   
         self._ipLider=self._ip
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
              temporizador=1
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
          ip=ip[0:len(ip)-1]
       
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
               if nodo==ip and not soyNuevo:
                 s.send(b"Reconectando")
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
         elif COMMAND.decode('utf-8')=="Dime si esta":
                  COMMAND=conn.recv(1024).decode('utf-8')
                  if self._archivos.count(COMMAND)==1:
                     conn.send(b"Esta")
                  else:
                     archivo=self._archivosDelSistema[COMMAND][0] ##CargarArchivo
                     with open(str(self.id)+archivo,'rb') as file:
                       conn.sendfile(file)
                     NodosEnLosQueEsta= json.dumps(self._archivosDelSistema[archivo]) ##Indexar en el hash del archivo
                     conn.send(NodosEnLosQueEsta)
                     
                     
         elif COMMAND.decode('utf-8')=="JOIN":
                  COMMAND=conn.recv(1024)
                  controlDNodos= json.loads(COMMAND.decode('utf-8'))
                  COMMAND=conn.recv(1024)
                  self.listaDNodos=json.loads(COMMAND.decode('utf-8'))
                  COMMAND=conn.recv(1024)
                  if COMMAND.decode('utf-8')!="":
                    self._id=int(COMMAND.decode('utf-8'))
                  self._ipLider=addr[0]
                  COMMAND=conn.recv(1024)
                  if COMMAND.decode('utf-8')=="Reconectando":
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                         nuevosArchivos=[]
                         for archivo in self._archivos:
                          if len(self._archivosDelSistema[archivo])>1:
                              s.connect(self._archivosDelSistema[archivo][2],8005)
                              s.send(b"Dime si esta")
                              s.send(archivo)
                              data=s.recv(1024).decode('utf-8')
                              if data!="Esta":
                                  os.remove(str(self.id)+","+archivo)
                                  archivo=s.recv(1024*5)
                                  hash=hashlib.sha256(archivo).hexdigest()
                                  with open(str(self.id)+","+hash, "wb") as file:
                                     file.write(archivo)
                                  nodosEnlosqueEsta=json.loads(s.recv(1024).decode('utf-8'))
                                  nuevosArchivos.append(data)
                                  self._archivosDelSistema.setdefault(data,nodosEnlosqueEsta)

                              else:
                                 nuevosArchivos.append(archivo)

                              
                        self._archivos=nuevosArchivos
                  else:
                    self.creaFingertable()
                             
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
   
  
  








