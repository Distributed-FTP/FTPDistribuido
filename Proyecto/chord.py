from asyncore import file_dispatcher
from audioop import add
from base64 import decode
from dataclasses import field
from errno import ELIBBAD
import hashlib
from itertools import count
from logging import RootLogger, root
from multiprocessing.sharedctypes import Value
import os
from posixpath import split
from sqlite3 import connect
from this import s
import time
from uuid import getnode
import socket
import json
import threading
from subprocess import Popen, PIPE
#from markupsafe import HasHTML
from requests import request 
from setuptools import Command 
from ping3 import ping
from Accessories.search_type import Search_Type
from Accessories.chord_communication_protocol import chord_protocol

#Si el nodo i de la red esta activo se guarda True, esta lista servira para comprobar constantemente 
# si un nodo se desactivo o si un nodo se activo
node_control=[]
stabilized_system=True
idNodoParaEnviarPeticion=0
#esta variable es para saber el estado en que se encuentra chord , si buscando un elemento , si anadiendo un elemento o si esta reorganizando
#los nodos
chord_status=None


def check_ping(host_name):
    ans=ping(host_name)
    if ans==False or ans==None:
        return False
    else:
        return True

#Recordar pasar la requests a los demas nodos por si el lider se cae

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

        
        
        #Todo Nodo debe saber si es el lider , en caso de que lo sea debe realizar acciones especificas
        # self.finger_table = {((self.__id+(i**2))%2**160) : self.__ip for i in range(160)} #!ID:IP

    #def agregarpeticion(self):
      #  self.requests

    #def procesapeticion(self):
        #for peticion in self.requests:
        # if peticio

    '''
        Actions
    '''
    def create_directory(self,name:str):
        os.mkdir(name)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
            for nodo in self.node_list:
                if nodo!=self.__ip:
                    if node_control[self.node_list.index(nodo)]==True:
                        try:
                            s.connect(nodo,8008)
                            s.send(b"Create Directory")
                            s.send(name)   
                        except:
                            stabilized_system=False

    def changeName_directory(self,name,new_name):
        os.rename(name,new_name)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
             for nodo in self.node_list:
                 if nodo!=self.__ip:
                    if node_control[self.node_list.index(nodo)]==True:
                        try:
                            s.connect(nodo,8008)
                            s.send(b"Rename")
                            s.send(name) 
                            s.send(new_name) 
                        except:
                            stabilized_system=False
         
    def delete_directory(self,name):
        os.rmdir(name)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
             for nodo in self.node_list:
                 if nodo!=self.__ip:
                    if node_control[self.node_list.index(nodo)]==True:
                        try:
                            s.connect(nodo,8008)
                            s.send(b"Remove")
                            s.send(name)  
                        except:
                            stabilized_system=False

    def state_directory(self,name):
        return os.stat(name)

    def find_file(self,hash,file,id,search_type: Search_Type,root):
        if search_type == Search_Type.DOWNLOAD:  
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
                keys=self.finger_table.keys()
                if keys.__contains__(id):
                    s.connect(self.node_list[self.finger_table[id]],8008)
                    s.send(chord_protocol.get_file())
                    s.send("{}".format(id))
                    s.send("{}".format(root))  
                    file=s.recv(1024)
                    if file=="Retorna":
                        s.close()
                        return file
                    else:
                     while file!="":
                      with open(root, "wb") as f:
                        f.write(file)
                        file=s.recv(1024)
                     s.close()
                     
                     return "File Download"
                     
                else:
                    dictionary=self.finger_table
                    value=dictionary.popitem()
                    value=value[1]
                    
                    while True:
                        if value<id:
                            break
                        else:
                            value=dictionary.popitem()
                            value=value[1]
                      
                    s.connect(self.node_list[value],8008)
                    s.send(chord_protocol.search_file())
                    s.send("{}".format(id))
                    s.send("{}".format(root))
                    data=s.recv(1024).decode('utf-8')
                    if data=="Retorna":
                        return data
                    else:
                      while data!="":
                       with open(root, "wb") as f:
                         f.write(data)
                         data=s.recv(1024)
                      s.close()

        elif search_type == Search_Type.EDIT:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
                keys=self.finger_table.keys()
                if keys.__contains__(id):
                    s.connect(self.node_list[self.finger_table[id]],8008)
                    s.send(chord_protocol.edit_file())
                    s.send("{}".format(str(id)))
                    s.send("{}".format(hash))
                    s.send("{}".format(root))
                    with open(root, 'rb') as f: 
                      s.sendfile(file)
                      s.send("")
                      f.close()
                    os.remove(root)
                else:
                    dictionary=self.finger_table
                    value=dictionary.popitem()
                    value=value[1]
                    
                    while True:
                        if value<id:
                            break
                        else:
                            value=dictionary.popitem()
                            value=value[1]
                          
                    s.connect(self.node_list[value],8008)
                    s.send(chord_protocol.search_for_edit_file())
                    s.send("{}".format(id))
                    s.send("{}".format(hash))
                    s.send("{}".format(root))
                    with open(root, 'rb') as f: 
                      s.sendfile(file)
                      s.send("")
                      f.close()
                    os.remove(root)

        elif search_type== Search_Type.STATE:
               with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
                keys=self.finger_table.keys()
                if keys.__contains__(id):
                    s.connect(self.node_list[self.finger_table[id]],8008)
                    s.send(b"STAT")
                    s.send(hash)
                    s.send(root)
                    result=s.recv(1024).decode('utf-8')
                    if result=="False":
                        return False
                    else:
                        return result                  
                else:
                    dictionary=self.finger_table
                    value=dictionary.popitem()
                    value=value[1]
                    
                    while True:
                        if value<id:
                            break
                        else:
                            value=dictionary.popitem()
                            value=value[1]
                          
                    s.connect(self.node_list[value],8008)
                    s.send(b"1011: STAT")
                    s.send("{}".format(id))
                    s.send("{}".format(hash))
                    s.send("{}".format(root))
                    return s.recv(1024).decode('utf-8')
        elif search_type == Search_Type.DELETE:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
                keys=self.finger_table.keys()
                if keys.__contains__(id):
                    s.connect(self.node_list[self.finger_table[id]],8008)
                    s.send(b"DELETE FILE")
                    s.send("{}".format(str(id)))
                    s.send("{}".format(hash))
                    s.send("{}".format(root))           
                    s.close()
                else:
                    dictionary=self.finger_table
                    value=dictionary.popitem()
                    value=value[1]
                    
                    while True:
                        if value<id:
                            break
                        else:
                            value=dictionary.popitem()
                            value=value[1]
                          
                    s.connect(self.node_list[value],8008)
                    s.send(b"SEARCH FOR DELETE")
                    s.send("{}".format(id))
                    s.send("{}".format(hash))
                    s.send("{}".format(root))
                    s.close()

        elif search_type == Search_Type.FILE_SIZE:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
                keys=self.finger_table.keys()
                if keys.__contains__(id):
                    s.connect(self.node_list[self.finger_table[id]],8008)
                    s.send(b"SIZE")
                    s.send("{}".format(root))          
                    data=s.recv(1024) 
                    s.close()
                    return data
                else:
                    dictionary=self.finger_table
                    value=dictionary.popitem()
                    value=value[1]
                    
                    while True:
                        if value<id:
                            break
                        else:
                            value=dictionary.popitem()
                            value=value[1]
                          
                    s.connect(self.node_list[value],8008)
                    s.send(b"SEARCH FILE_SIZE")
                    s.send("{}".format(id))
                    s.send("{}".format(root))
                    data=s.recv(1024)
                    return data         

    def get_size_file(self,root):
        
        file_id=self.files_hash.get(root)
        
        hash_code = file_id
        id=""
        while hash_code[0]!=",":
            id+=hash_code[0]
            hash_code=hash_code[1:len(hash_code)-1]
        hash_code=hash_code[1:len(hash_code)-1]

        return self.find_file(None, None, id, Search_Type.FILE_SIZE,root)

    def download_file(root,self):
        
        file_id=self.files_hash.get(root)
        
        hash_code = file_id
        id = ""
        while hash_code[0]!=",":
            id += hash_code[0]
            hash_code = hash_code[1:len(hash_code)-1]
        hash_code = hash_code[1:len(hash_code)-1]

        if self.__files.count(hash_code)==1:
            with open(root, 'rb') as f: 
                return True
        else:
             result=self.find_file(hash_code, None, id, Search_Type.DOWNLOAD,root)

             if result=="Retorna":
                 return False
             else:
               return True
    
    def upload_file(self,root):  #Este metodo escoge el nodo que lo almacenara y le envia un mensaje para que lo guarde
      
     with open(root, 'rb') as file: 
                
        cut_root=root
        while cut_root[len(cut_root)-1]!="/":
               cut_root=cut_root[0:len(cut_root)-1]
    
        if self.files_hash.keys().__contains__(root)==0:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
                ip=None
                count_files=0
                count=0
                for node in self.node_list:
                    if node_control[count]==True:
                        try:
                            s.connect(node,8008)
                            s.send(b"Archivos")
                            data=s.recv(1024)
                            if count==0:
                                ip = node
                                count_files= int(data.decode('utf-8'))
                            elif int(data.decode('utf-8'))<count_files:
                                ip = node
                                count_files=int(data.decode('utf-8'))
                        except:
                            stabilized_system=False
                            return False
                    count+=1
                    s.close()
                try:
                    if ip!=self.__ip:
                     id=self.node_list.index(ip)
                     s.connect(ip,8008)
                     s.send(chord_protocol.save_file())
                     s.send(str(id))
                     s.send(root)
                     s.sendfile(file)
                     s.send("")
                     data=s.recv(1024)
                     if data.decode('utf-8') != chord_protocol.save_file():
                        return False
                     id_file_return=int(s.recv(1024).decode('utf-8'))
                     self.files_hash.setdefault(root,id_file_return)
                    else:
                     id_file_return=self.__id+","+hash
                     hash=hashlib.sha256(file).hexdigest()
                     self.__files.append(hash)
                     self.__files_system.setdefault(hash,[ip])
                     self.files_hash.setdefault(root,id_file_return)
                    
                    for nodo in self.node_list:
                        if nodo!=self.__ip:
                            if node_control[self.node_list.index(nodo)]==True:
                                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
                                    s.connect(nodo,8008)
                                    s.send("UPLOAD")
                                    s.send(root)
                                    s.send(id_file_return)
                                    s.close()

                    s.close()
                    nodes_where_the_file_is=[]    
                    nodes_where_the_file_is.append(ip)
                    count_replicas=3
                    
                    while count_replicas>0:#Replicacion
                        if ip!=self.__ip:
                         s.connect(ip,8008)
                         s.send(chord_protocol.get_successor())
                         data=s.recv(1024)
                         ip=data.decode('utf-8')
                         s.close()
                        else:
                          ip=self.__successor
                        if ip!=self.__ip: 
                         s.connect(ip,8008)
                         s.send(chord_protocol.save_file())          #Hacer que los nodos confirmen cuando hayan realizado el almacenamiento
                         s.send(str(id))
                         s.send(root)
                         s.sendfile(file)
                         s.send("")
                         data=s.recv(1024)
                         if data.decode('utf-8')!="Save":
                            return False
                         data=s.recv(1024)
                         if nodes_where_the_file_is.count(ip)==0:
                           nodes_where_the_file_is.append(ip)
                         s.close()
                         count_replicas-=1
                         file_hash=hashlib.sha256(file).hexdigest()
                         for ip in nodes_where_the_file_is:
                            s.connect(ip,8008)
                            s.send(chord_protocol.update_info())
                            s.send(file_hash)
                            s.send(json.dumps(nodes_where_the_file_is))
                            s.close()        
                except:
                    stabilized_system=False
                    return False     
        
        file.close()
     return True
    
    def edit_file(self,root):
        
        file_id=self.files_hash.get(root)
        
        hash_code = file_id
        id=""
        while hash_code[0]!=",":
            id+=hash_code[0]
            hash_code=hash_code[1:len(hash_code)-1]
        hash_code=hash_code[1:len(hash_code)-1]

        if self.__files.count(hash_code)==1:
             with open(root, 'rb') as f: 
                hash_new=hashlib.sha256(f).hexdigest()
                self.files_hash.pop(root)
                self.files_hash.setdefault(root,id+","+hash_new)
                f.close()
             
             

        else:
          self.find_file(hash_code,None, id, Search_Type.EDIT,root)
    
    def change_name_file(self,root,rootNew):
         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
          file_id= self.files_hash.pop(root)
          self.files_hash.setdefault(rootNew,file_id)
          for nodo in self.node_list:
             if nodo!=self.__ip:
                if node_control[self.node_list.index(nodo)]==True:
                    s.connect(nodo,8008)
                    s.send("CHANGE NAME")
                    s.send(root)
                    s.send(rootNew)

    def delete_file(self,root):
       with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        file_id=self.files_hash.get(root)
        for nodo in self.node_list: 
            if nodo!=self.__ip:
                if node_control[self.node_list.index(nodo)]==True:
                    s.connect(nodo,8008)
                    s.send("DELETE")
                    s.send(root)
                    s.close
       
       self.files_hash.pop(root)

       hash_code = file_id
       id=""
       while hash_code[0]!=",":
            id+=hash_code[0]
            hash_code=hash_code[1:len(hash_code)-1]
       hash_code=hash_code[1:len(hash_code)-1]

       if self.__files.count(hash)==1:
              os.remove(root)               
              self.__files.remove(hash)
              for nodo in self.__files_system.get(hash):
                  if nodo!=self.__ip:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
                          s.connect(nodo,8008)
                          s.send(b"DELETE REPLICA")
                          s.send("{}".format(str(id)))
                          s.send("{}".format(hash))
                          s.send("{}".format(root))
                          s.close()
                     
       else:
         self.find_file(hash_code, None, id, Search_Type.DELETE,root)

    def get_requests_system(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.__ip,8008))
        server.listen()
        conn, addr = server.accept()
        if conn:
            data=conn.recv(1024)
            data=data.decode('utf-8')
            if data=='1007: Unstable Chord' and self.node_list.count(addr[0])==1 and node_control[self.node_list.index(addr[0])]==True:
                SystemaEstable=False
                conn.close()
            elif data=="1008: Get Successor":
                conn.send("{}".format(self.__successor))
            elif data=="1006: Save File":
                id=conn.recv(1024).decode('utf-8')
                root=conn.recv(1024).decode('utf-8')
                file_text=conn.recv(1024)
                hash=hashlib.sha256(file_text).hexdigest()
                if self.__files.count(hash)==0:
                 try:
                  while file_text!="":
                   with open(root, "wb") as file:
                    file.write(file_text)
                    file_text=conn.recv(1024)
                  self.__files.append(hash)
                  self.__files_system.setdefault(hash,[])
                  conn.send(b"Save")
                  conn.send(str(id)+","+hash)
                 except:
                    conn.send(b"Save")
                else:
                    conn.send(b"Save")
                    conn.send(b"Is")

            elif data=="1003: Update File":
                data=conn.recv(1024).decode('utf-8')
                self.__files_system.keys= json.loads(data)
                data=conn.recv(1024).decode('utf-8')
                self.__files_system.values= json.loads(data)
            elif data=="1004: Edit File":
                id=conn.recv(1024).decode('utf-8')
                hash=conn.recv(1024).decode('utf-8')
                root=conn.recv(1024).decode('utf-8')
                os.remove(root)
                data=conn.recv(1024).decode('utf-8')
                while data!="":
                    with open(root, "wb") as file:
                     file.write(data)
                     data=conn.recv(1024)

                with open(root, "wb") as file:
                 hash_new_file=hashlib.sha256(file).hexdigest()
                
                ###Editar el archivo y donde quiera que este replicado 
                #Eliminar El archivo , Guardar EL actual e informar a los demas nodos que lo tienen
                self.__files_system.setdefault(hash_new_file,self.__files_system.get(hash))    #anadir el nuevo hash junto a la lista de ips donde esta el archivo
                self.__files.remove(hash)
                self.__files.append(hash_new_file) ##Anadir el nuevo hash
                self.files_hash.pop(root)
                self.files_hash.setdefault(root,id+","+hash_new_file)

                for nodo in self.node_list:
                    if nodo!=self.__ip:
                        if node_control[self.node_list.index(nodo)]:
                         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:                         
                            s.connect(nodo,8008)
                            s.send(b"UPDATE FILE EDITION")
                            s.send(root)
                            s.send(hash_new_file)
                            s.close()
                 
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  #Actualizar las replicas
                    for replica in self.__files_system[hash]:
                        if replica!=self.__ip:
                            if node_control[self.node_list.index(replica)]==True:
                                s.connect(replica,8008)
                                s.send(chord_protocol.get_replica())
                                s.send(id)
                                s.send(hash)
                                s.send(root)
                                with open(root, 'rb') as f:
                                 s.sendfile(f)
                                 s.send("")
                                 f.close()
                                s.close()

                self.__files_system.pop(hash)
                self.__files_system.setdefault(hash,hash_new_file)
            elif data=="1010: Get Replica":
                id=conn.recv(1024).decode('utf-8') 
                hash=conn.recv(1024).decode('utf-8')
                root=conn.recv(1024).decode('utf-8')    
                os.remove(root)
                data=conn.recv(1024)
                while data !="":
                    with open(root, "wb") as file:
                     file.write(data)
                     data=conn.recv(1024)
                
                with open(root, "rb") as file:
                  hash_new_file=hashlib.sha256(file_text).hexdigest()
                
                  
                self.__files_system.setdefault(hash_new_file, self.__files_system[hash])   
                self.__files.remove(hash)
                self.__files.append(hash_new_file)
                self.__files_system.pop(hash)
                self.__files_system.setdefault(hash,hash_new_file)

            elif data=="1001: Search File":
                id=int(conn.recv(1024).decode('utf-8'))
                root=conn.recv(1024).decode('utf-8')
                archivo=self.find_file(None,None,id,Search_Type.DOWNLOAD,root)
                if archivo=="Retorna":
                    conn.send(archivo)
                else:
                    with open(root, 'rb') as f: 
                     conn.sendfile(f)
                     conn.send("")
                     f.close()
                    os.remove(root)

            elif data=="1002: Search for Edit File":
                  id=int(conn.recv(1024).decode('utf-8'))
                  hash=conn.recv(1024).decode('utf-8')
                  root=conn.recv(1024).decode('utf-8')
                  data=conn.recv(1024).decode('utf-8')
                  while data!="":
                    with open(root, "wb") as file:
                     file.write(data)
                     data=conn.recv(1024)
                  self.find_file(hash,None,id,Search_Type.EDIT,root)
                
            elif data=="1000: Get File":
                id=conn.recv(1024).decode('utf-8')
                root=conn.recv(1024).decode('utf-8')
                try: 
                  with open(root, 'rb') as f:
                   conn.sendfile(f)
                   conn.send("")
                   f.close()
                  os.remove(root)
                except:
                    conn.send("Retorna")
            elif data=="1005: Update Info":
                hash=conn.recv(1024).decode('utf-8')
                data=conn.recv(1024).decode('utf-8')
                data=json.loads(data)
                self.__files_system.setdefault(hash,data)
                
            elif data=="STAT":
                hash=conn.recv(1024).decode('utf-8')
                root=conn.recv(1024).decode('utf-8')
                if self.__files.count(hash)==1:
                     conn.send(os.stat(root))
                else:
                    conn.send(b"False")

            elif data=="1011: STAT":
                id=int(conn.recv(1024).decode('utf-8'))
                hash=conn.recv(1024).decode('utf-8')
                root=conn.recv(1024).decode('utf-8')
                conn.send(str(self.find_file(hash,None,id,Search_Type.STATE,root)))
            elif data=="Create Directory":
                name=conn.recv(1024).decode('utf-8')
                os.mkdir('/root'+name)
            elif data=="Rename":
                name=conn.recv(1024).decode('utf-8')
                new_name=conn.recv(1024).decode('utf-8')
                os.rename('/root'+name,new_name)
            elif data=="Remove":
                name=conn.recv(1024).decode('utf-8')
                os.remove('/root'+name)
            elif data=="CHANGE NAME":
                root=conn.recv(1024).decode('utf-8')
                rootNew=conn.recv(1024).decode('utf-8')
                file_id=self.files_hash.pop(root)
                self.files_hash.setdefault(rootNew,file_id)
            elif data=="DELETE REPLICA":
                id=conn.recv(1024).decode('utf-8')
                hash=conn.recv(1024).decode('utf-8')
                root=conn.recv(1024).decode('utf-8')
                os.remove(root)
                self.__files.remove(hash)
                self.__files_system.pop(hash)
            elif data=="SEARCH FOR DELETE":
                id=conn.recv(1024).decode('utf-8')
                hash=conn.recv(1024).decode('utf-8')
                root=conn.recv(1024).decode('utf-8')
                self.find_file(hash,None,id,Search_Type.DELETE,root)
            elif data=="DELETE FILE":
                id=conn.recv(1024).decode('utf-8')
                hash=conn.recv(1024).decode('utf-8')
                root=conn.recv(1024).decode('utf-8')
                os.remove(root)
                for nodo in self.__files_system[hash]:
                   if nodo!=self.__ip:
                      conn.close()
                      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
                          s.connect(nodo,8008)
                          s.send(b"DELETE REPLICA")
                          s.send("{}".format(str(id)))
                          s.send("{}".format(hash))
                          s.send("{}".format(root))
                          s.close()
                self.__files.remove(hash)
                self.__files_system.pop(hash) 
            elif data=="DELETE":
                root=conn.recv(1024).decode('utf-8')
                self.files_hash.pop(root)
                conn.close()
            elif data=="UPLOAD":
                root=conn.recv(1024).decode('utf-8')
                id=conn.recv(1024).decode('utf-8')
                self.files_hash.setdefault(root,id)
                conn.close()
            elif data=="UPDATE FILE EDITION":
                root=conn.recv(1024).decode('utf-8')
                new_id=conn.recv(1024).decode('utf-8')
                self.files_hash.pop(root)
                self.files_hash.setdefault(root,new_id)
                conn.close()
            elif data=="SIZE":
                root=conn.recv(1024).decode('utf-8')
                conn.send(os.path.getsize(os.getcwd()+root))
            elif data=="SEARCH FILE_SIZE":
                id=conn.recv(1024).decode('utf-8')
                root=conn.recv(1024).decode('utf-8')
                conn.send(self.find_file(None,None,id,Search_Type.FILE_SIZE,root))
            elif data=="New File":
                data=conn.recv(1024)
                while data != "":
                    data=conn.recv(1024)
                    keys=json.loads(data)
                    data=conn.recv(1024)
                    values=json.loads(data)
                    for i in range(0,len(keys)-1):
                     self.files_hash.setdefault(keys[i],values[i])           
                    data=conn.recv(1024)

        conn.close()

    def assign_requests(self):
          if len(self.requests)>0:
                 if node_control[idNodoParaEnviarPeticion]:
                  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                     s.connect(self.node_list[idNodoParaEnviarPeticion],8008)
                     s.send(b"Recibe peticion")
                     s.send(self.requests[0])
                 if idNodoParaEnviarPeticion==len(self.node_list)-1:
                      idNodoParaEnviarPeticion=0
                 else:
                    idNodoParaEnviarPeticion+=1

    def processes_request(self):
     # threading.Thread(target=self.countdown(), args=(900)).start()   #Este temporizador es para estabilizar el sistema cada un tiempo determinado
    #  threading.Thread(target=self.get_requests_system(), args=()).start()
      
      #while stabilized_system and not self.finish_countdown:
          
         # if self.__ip==self.__ip_boss:
           #   threading.Thread(target=self.get_requests(), args=()).start()
        #      threading.Thread(target=self.assign_requests(), args=()).start()    
              
              #request=self.requests[0]
           #   if request=="subir":
          #           self.upload_file(request)
          #           self.update_nodes()
           #   if request=="descargar":
          #            self.download_file(request)
          #    if request=="editar":
           #           self.edit_file(request,request)
           None
          
    def get_requests(self):
        server = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.__ip,8007))
        server.listen()
        while True:
            conn, addr = server.accept() # Establecemos la conexi??n con el ftp para recibir las peticiones
            data=conn.recv(1024)           ###Hay que ver como llegan las peticiones
            self.requests.append(data)

    def get_files(self,conn):
        new_files_keys=[]
        new_files_Values=[]
        files = ""
        with open(self.path + "/Reports/files.fl", 'rb') as f:
            while True:
                bytes_read = f.read()
                if bytes_read == b'':
                    break
                else:
                    files += str(bytes_read)
        file_list = files.split("\\n")
        for i in range(len(file_list)):
            file = str(file_list[i]).replace("b'", '')
            file_list[i] = str(file).replace("'", '')
        for i in range(len(file_list)):
            if file_list[i].__contains__("F~~"):
                file_list[i] = file_list[i].replace("F~~", '')
                
                root=str(self.path + file_list[i])
                os.stat(root)
                hash=hashlib.sha3_256(root.encode()).hexdigest()
                try:
                    if self.files_hash.get(root)==None:
                        self.files_hash.setdefault(root,str(self.__id)+","+hash)
                        new_files_keys.append(root)
                        new_files_Values.append(str(self.__id)+","+hash)
                        self.__files.append(hash)
                        self.__files_system.setdefault(hash,[self.__ip])
                    else:
                        os.remove(root)
                except:
                    None
            
        if len(new_files_keys)>0 and conn is not str:
                for nodo in self.node_list:
                 if nodo!=self.__ip and node_control[self.node_list.index(nodo)]:
                      if nodo==self.__ip_boss:
                            conn.send(b"New")   
                            conn.send(json.dumps(new_files_keys))
                            conn.send(json.dumps(new_files_keys))
                            conn.send("")
                      else:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect(nodo,8005)
                            s.send(b"New File")   
                            s.send(json.dumps(new_files_keys))
                            s.send(json.dumps(new_files_keys))
                            s.send("")
                           

        
        
    '''
        Boss Operations
    '''
    def get_boss(self):
        SERVER_PORT=8002
        countpos=0

        for ipnodo in self.node_list:
            if ipnodo==self.__ip:
                countpos+=1
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    while countpos<len(self.node_list):
                        try:
                            s.connect((self.node_list[countpos], SERVER_PORT))
                            s.send(b"Soy lider d nodos")
                            s.close()
                            countpos+=1
                        except:
                            print("Hay que estabilizar antes de que sigan funcionando los demas nodos, hay al menos uno que se desconecto")
                            
                        s.connect((self.__ip, SERVER_PORT))
                        s.send(b"Eres el lider")
                        s.close()

            elif check_ping(ipnodo):
                break
            countpos+=1
    
    def search_boss(self):
        ip=self.__ip
        while ip[len(ip)-1]!='.':
            ip=ip[0:len(ip)-1]
        
         
        for i in range(9,10):
                if self.NoSereLider==True:
                    self.search_to_boss=False
                    s.close()
                    break
                if self.__ip!= ip+str(i) and self.NodosEncontrados.count(ip+str(i))==0:  
                  try:
                   with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
                    s.connect((ip+str(i), 8003))
                    s.send(b"Code #399#")
                    data=s.recv(1024).decode('utf-8')
                    if data=="Code #400#":
                        self.leader_calls=True
                        s.send(json.dumps(self.NodosEncontrados))
                        i=255
                    elif data=="Nodo aislado":
                         nodosEncontradosporEl=json.loads(s.recv(1024))
                         set(self.NodosEncontrados.extend(nodosEncontradosporEl))

                    s.close()
                  except:
                    continue
        s.close()
        self.search_to_boss=False
        
    def wait_update_boss(self):
        SERVER_PORT = 8002

        self.server = socket.socket(
              socket.AF_INET, socket.SOCK_STREAM)
        
        self.server.bind((self.__ip,SERVER_PORT))
        self.server.listen()
        while not self.there_boss:
            conn, addr = self.server.accept() # Establecemos la conexi??n con el cliente
            if conn:
                data=conn.recv(1024)
                if data.decode('utf-8')=="Soy lider d nodos":
                    there_boss=True
                    self.__ip_boss=addr[0]
                elif data.decode('utf-8')=="Eres el lider":
                    self.__ip_boss=self.__ip
                    there_boss=True     
                conn.close()     
    
    def get_signal(self):
             
        SERVER_PORT= 8003  
        self.server = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
          
        self.server.bind((self.__ip,SERVER_PORT))
        self.server.listen()
        
        while True:
         conn, addr = self.server.accept() # Establecemos la conexi??n con el cliente
         if conn:
            data=conn.recv(1024).decode('utf-8')
            if data=="Code #399#":
                if self.__ip==self.__ip_boss:
                    self.NodosEncontrados.append(addr[0])
                    conn.send(b'Code #400#')
                    listaDOtrosNodosSueltos=conn.recv(1024)
                    self.NodosEncontrados.extend(json.loads(listaDOtrosNodosSueltos))

                elif self.__ip_boss==None:
                    conn.send(b"Nodo aislado") 
                    self.NodosEncontrados.append(self.__ip)
                    conn.send(json.dumps(self.NodosEncontrados)) 
                    self.NodosEncontrados=[]
                    self.NoSereLider=True
                    break
                else:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect(self.__ip_boss,8003)
                        s.send(b"Code #398#")
            elif data=="Code #398#":
                    if self.__ip==self.__ip_boss:
                        if self.node_list.count(addr[0])==1 and node_control[self.node_list.index(addr[0])]:
                               set(self.NodosEncontrados.extend(json.loads(s.recv(1024))))
                    else:
                        conn.send("")
            
            else:
                conn.send("")
            

         conn.close()
    
    
    '''
        Finger Table Operations
    '''
    def create_finger_table(self):
        for i in range(6):
            key=self.__id+pow(2,i)
            self.finger_table.setdefault(key,key) 
    
    def update_finger_tables(self): #Luego poner el crear finger_tables  
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            for nodo in self.node_list:
               if nodo!=self.__ip: 
                 if node_control[self.node_list.index(nodo)]:
                    s.connect(nodo,8005)
                    s.send(b"UpdateFingertables")
                    data=s.recv(1024)
    
    def state_file(self,root):
        
        file_id=self.files_hash.get(root)
        
        hash_code = file_id
        id=""
        while hash_code[0]!=",":
            id+=hash_code[0]
            hash_code=hash_code[1:len(hash_code)-1]
        hash_code=hash_code[1:len(hash_code)-1]

        if self.__files.count(hash_code)==1:
          os.stat(root)
        else:
           return self.find_file(hash_code,None, id, Search_Type.STATE,root)

    def remove_file(self,root):
        os.remove(root)

    '''
        Additional Actions
    '''
    def countdown(self,num_of_secs):  #Temporizador que marca la revision de estabilidad del sistema
        while num_of_secs:
            m, s = divmod(num_of_secs, 60)
            min_sec_format = '{:02d}:{:02d}'.format(m, s)
            print(min_sec_format, end='/r')
            time.sleep(1)
            num_of_secs -= 1
          
        self.finish_countdown=True
    
    def leave(self,id):
        node_control[id]=False
        ip_predecessor=self.get_predecessor(self.node_list[id])
        ip_successor=self.get_successor(self.node_list[id])
        self.update_successor(ip_predecessor,ip_successor)
        self.update_predecessor(ip_successor,ip_predecessor)
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
      
    def listen(self):
          servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          
          servidor.bind((self.__ip,8005))
          servidor.listen()
          conn, addr = servidor.accept()
          COMMAND=conn.recv(1024)
          if COMMAND.decode('utf-8')=="actualiza predecesor":
              COMMAND=conn.recv(1024)
              self.__predecessor=COMMAND.decode('utf-8')
          elif COMMAND.decode('utf-8')=="actualiza sucesor":
              COMMAND=conn.recv(1024)
              self.__successor=COMMAND.decode('utf-8')
          elif COMMAND.decode('utf-8')=="LEAVE":
              COMMAND=conn.recv(1024)
              node_control[int(COMMAND.decode('utf-8'))]=False
          elif COMMAND.decode('utf-8')=="Dime si esta":
              root=conn.recv(1024).decode('utf-8')
              COMMAND=conn.recv(1024).decode('utf-8')
              if list(self.__files_system.keys()).count(COMMAND)==1:
                  conn.send(b"Esta")
                  if len(self.__files_system.get(COMMAND))>1:
                      conn.send(json.dumps(self.__files_system.get(COMMAND)))
                      conn.send("")
                  else:
                      
                      hashnew=self.__files_system.get(COMMAND)
                      hashnew=hashnew[0]
                      conn.send(json.dumps(self.__files_system.get(hashnew)))
                      conn.send("Actualiza")
                      conn.send(hashnew)
                      with open(root, 'rb') as f:
                          conn.sendfile(f)
                          conn.send("")
                             
                  conn.send(b"Esta")
                  conn.send(json.dumps(self.__files_system.get(COMMAND)))
                
          elif COMMAND.decode('utf-8')=="JOIN":
              COMMAND=conn.recv(1024)
              node_control= json.loads(COMMAND.decode('utf-8'))
              COMMAND=conn.recv(1024)
              self.node_list=json.loads(COMMAND.decode('utf-8'))
              COMMAND=conn.recv(1024)
              if COMMAND.decode('utf-8')!="":
                  self.__id=int(COMMAND.decode('utf-8'))
                  self.create_finger_table()
              self.__ip_boss=addr[0]

              COMMAND=conn.recv(1024)
              keys= json.loads(COMMAND.decode('utf-8'))
              COMMAND=conn.recv(1024)
              values=json.loads(COMMAND.decode('utf-8'))
              
              for i in range(0,len(keys)-1):
                self.files_hash.setdefault(keys[i],values[i])

              COMMAND=conn.recv(1024)
              if COMMAND.decode('utf-8')=="Reconectando": 
                  new_files_keys=[]
                  new_files_Values=[]
                  files = ""
                  with open(self.path + "/Reports/files.fl", 'rb') as f:
                   while True:
                    bytes_read = f.read()
                    if bytes_read == b'':
                      break
                    else:
                     files += str(bytes_read)
                  file_list = files.split("\\n")
                  for i in range(len(file_list)):
                   file = str(file_list[i]).replace("b'", '')
                   file_list[i] = str(file).replace("'", '')
                  for i in range(len(file_list)):
                   if file_list[i].__contains__("F~~"):
                      file_list[i] = file_list[i].replace("F~~", '')
                      try:
                       root=str(self.path + file_list[i])
                       os.stat(root)
                       hash=hashlib.sha3_256(root.encode()).hexdigest()
                       if self.files_hash.get(root)==None:
                        
                        self.files_hash.setdefault(root,self.__id+","+hash)
                        new_files_keys.append(root)
                        new_files_Values.append(self.__id+","+hash)
                        self.__files.append(hash)
                        self.__files_system.setdefault(hash,[self.__ip])

                       else:
                         
                         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                              s.connect(self.__successor,8005)
                              s.send(b"Dime si esta")
                              s.send(root)
                              s.send(hash)
                              data=s.recv(1024).decode('utf-8')
                              if data=="Esta":
                                 lista=json.loads(s.recv(1024))
                                 self.__files_system.setdefault(hash,lista)
                                 data=s.recv(1024)
                                 if data=="Actualiza":
                                    os.remove(root)
                                    hashnew=s.recv(1024)
                                    self.__files.append(hashnew)
                                    self.__files_system.setdefault(hashnew,self.__files_system.pop(hash))
                                    self.__files_system.setdefault(hash,hashnew)
                                    data=s.recv(1024)
                                    while data!="":
                                      with open(root, "wb") as f:
                                       f.write(data)
                                       data=s.recv(1024)
                              else:
                                s.close()
                                s.connect(self.__predecessor,8005)
                                s.send(b"Dime si esta")
                                s.send(hash)
                                data=s.recv(1024).decode('utf-8')
                                if data=="Esta":
                                 lista=json.loads(s.recv(1024))
                                 self.__files_system.setdefault(hash,lista)
                                 self.__files.append(hash)
                                 data=s.recv(1024)
                                 if data=="Actualiza":
                                    os.remove(root)
                                    hashnew=s.recv(1024)
                                    self.__files.remove(hash)
                                    self.__files.append(hashnew)
                                    self.__files_system.setdefault(hashnew,self.__files_system.pop(hash))
                                    self.__files_system.setdefault(hash,hashnew)
                                    data=s.recv(1024)
                                    while data!="":
                                      with open(root, "wb") as f:
                                       f.write(data)
                                       data=s.recv(1024)
                                else:
                                    self.__files.append(hash)
                                    self.__files_system.setdefault(hash,[self.__ip])
                                    self.files_hash

                      except:
                        None

                  if len(new_files_keys)>0:
                    for nodo in self.node_list:
                     if nodo!=self.__ip and node_control[list(self.node_list).index(nodo)]:
                      if nodo==self.__ip_boss:
                            conn.send(b"New")   
                            conn.send(json.dumps(new_files_keys))
                            conn.send(json.dumps(new_files_keys))
                            conn.send("")
                      else:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect(nodo,8005)
                            s.send(b"New File")   
                            s.send(json.dumps(new_files_keys))
                            s.send(json.dumps(new_files_keys))
                            s.send("")
                  else:
                    conn.send("")
                    conn.close()
                  open
              elif COMMAND.decode('utf-8')!="":
                   self.get_files(conn)
                   conn.close()
                  
          elif COMMAND.decode('utf-8')=="UpdateFingertables":
              for i in range(6):
                  id=pow(2,i)+self.__id
                  self.finger_table[id]=self.sucesor(id)
          conn.close()

    def successor(self, id):
      pos=id+1
      if pos>=len(self.node_list):
          pos=0
      while node_control[pos]!=True:
          pos+=1
      return pos
                  
    def get_predecessor(self,ip):
        pos=self.node_list.index(ip)
        if pos==0:
            pos==len(self.node_list)-1
        else:
            pos-=1
        while not check_ping(self.node_list[pos]):
            if pos==0:
                pos==len(self.node_list)-1
            else:
                pos-=1
        return self.node_list[pos]

    def get_successor(self,ip):
        pos=self.node_list.index(ip)
        if pos==len(self.node_list)-1:
            pos==0
        else:
            pos+=1
        while not check_ping(self.node_list[pos]):
            if pos==len(self.node_list)-1:
                pos==0
            else:
                pos+=1
        return self.node_list[pos]
                    
    def update_successor(ip,new_successor):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, 8005))
            s.send(b"actualiza sucesor")
            
            s.send(b'{}'.__format__(new_successor.encode()))
            s.close()
             
    def update_predecessor(ip,new_predecessor):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, 8005))
            s.send(b"actualiza predecesor")
            
            s.send(b'{}'.__format__(new_predecessor.encode()))
            s.close() 

     

    def stabilize(self):    
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        for nodo in self.node_list:
            if nodo != self.__ip:
                 try: 
                   s.connect(nodo,8005)
                   s.close()
                   if node_control[self.node_list.index(nodo)]==False:
                          self.join(nodo)
                          if self.NodosEncontrados.count(nodo)!=0:
                                  self.NodosEncontrados.remove(nodo)

                 except:
                    if node_control[self.node_list.index(nodo)]==True:
                        self.leave(self.node_list.index(nodo))

        for nodo in self.NodosEncontrados:
            self.join(nodo)
        
        self.NodosEncontrados=[]


    def update_nodes(self):
        i=0
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
            for node in self.node_list:
                if node_control[i]==True:
                    s.connect(node,8008)
                    s.send(b'Actualiza Archivos')
                    send_list=json.dumps(self.__files_system.keys())
                    s.send(b"{}".__format__(send_list.encode('utf-8')))
                    send_list=json.dumps(self.__files_system.values())
                    s.send(b"{}".__format__(send_list.encode('utf-8')))
                    s.close()
                i+=1

    def run(self):  
        while True:
            if not self.stabilized_system:
                if self.__ip_boss==self.__ip:
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
                                self.__id=0
                                self.node_list.append(self.__ip)
                                node_control.append(True)
                                self.__successor=self.__ip
                                self.__predecessor=self.__ip
                                self.create_finger_table()
                                self.get_files("Create")

                            break
                        elif self.NoSereLider==True:
                                 self.__ip_boss=="temporal"
                                 self.NoSereLider=False
                                 break
                                
                            
                elif not check_ping(self.__ip_boss):
                    self.there_boss=False
                    threading.Thread(target=self.wait_update_boss, args=()).start()
                    threading.Thread(target=self.get_boss, args=()).start()
                else:
                    self.listen()
            else:
                self.processes_request()


if __name__ == '__main__':
    machine_name = socket.gethostname()
    machine_ip = socket.gethostbyname(machine_name)
    node=Node(machine_ip,os.getcwd())
    node.run()