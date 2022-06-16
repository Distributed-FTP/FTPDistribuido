#from typing_extensions import Self
from uuid import getnode as get_mac
import sys,subprocess
import os
#import nis as ni
import socket


 


#Si el nodo i de la red esta activo se guarda True, esta lista servira para comprobar constantemente 
# si un nodo se desactivo o si un nodo se activo 
controlDNodos=[]


#esta variable es para saber el estado en que se encuentra chord , si buscando un elemento , si anadiendo un elemento o si esta reorganizando
#los nodos
estadoDChord=None    
listaDNodos=list()

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
   
BuscaNodosEnRed()


class Node:
    def __init__(self,ip):
        self._id=None
        self._ip=ip
        self._keys=list()  #Para cada nodo hay que saber las llaves que tiene asociadas en cada momento
        self._predecesor=None
        self._sucesor=None
        self.fingertable=None
       # self.fingertable = {((self._id+(i**2))%2**160) : self._ip for i in range(160)} #!ID:IP


    def start_comunication(self):
        try:
            BUFFER_SIZE=1024
            self.server = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self._ip,12345))
            self.server.listen(1) 
            try:
             self.server.settimeout(1000)
             conn, addr = self.server.accept() # Establecemos la conexión con el cliente 
            except:
                print("El servidor queda deshabilitado")

           
            if conn:
              print('[*] Conexión establecida') 
              while True:
            # Recibimos bytes, convertimos en str
               data = conn.recv(BUFFER_SIZE)
            # Verificamos que hemos recibido datos
               if not data:
                break
               else:
                print(data)
                print('[*] Datos recibidos: {}'.format(data.decode('utf-8'))) 
               conn.send(data) # Hacemos echo convirtiendo de nuevo a bytes
        except socket.error:
            prRed('Error abriendo socket')
            return


if __name__ == '__main__':
 ID_equipo=0
 nombre_equipo = socket.gethostname()
 direccionIP_equipo = socket.gethostbyname(nombre_equipo)
 nodo=Node(direccionIP_equipo)
 nodo.start_comunication()

#def createNodes():
 #   i =0 
  #  nuevonodo=Node("127.70.30.{}".format(i),i)
   # listaDNodos.append(nuevonodo)
   # controlDNodos.append(True)
   # i+=1
   # while i<64:
   #     nuevonodo=Node("127.70.30.{}".format(i),i)
   #    if i<=63 :
   #      listaDNodos[i-1]._sucesor=nuevonodo
   #      listaDNodos.append(nuevonodo)
   ##      controlDNodos.append(True)
    #     nuevonodo._predecesor=listaDNodos[i-1]
    #listaDNodos[63]._sucesor=listaDNodos[0]
    #listaDNodos[0]._predecesor=listaDNodos[63]

#def updatefingertables()
 

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

Nodo= Node()

def DameIP():
        interfaces = ni.interfaces()
        if 'eth0' in interfaces: #LAN
            return ni.ifaddresses('eth0')[2][0]['addr']
        elif 'enp0s31f6' in interfaces: #WIFI
            return ni.ifaddresses('enp0s31f6')[2][0]['addr']
        else:
            ni.ifaddresses(interfaces[0])[2][0]['addr']

def ObtenerID(self):
        mac = get_mac() #Retorna la direccion mac como entero de 48 bits
        My_id = str(mac).join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
                            for x in range(30))
        sha = hashlib.sha1()
        sha.update(My_id.encode('ascii'))
        self.MyId = int(sha.hexdigest() ,16)
        return  int(sha.hexdigest() ,16)




