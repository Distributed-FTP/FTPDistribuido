
#Si el nodo i de la red esta activo se guarda True, esta lista servira para comprobar constantemente 
# si un nodo se desactivo o si un nodo se activo 
controlDNodos=[]

#esta variable es para saber el estado en que se encuentra chord , si buscando un elemento , si anadiendo un elemento o si esta reorganizando
#los nodos
estadoDChord=None    
listaDNodos=list()

class Node:
    def init(self,ip,id):
        self._id=id
        self._ip=ip
        self._keys=list()  #Para cada nodo hay que saber las llaves que tiene asociadas en cada momento
        self._predecesor=None
        self._sucesor=None
        self.fingertable=None

def createNodes():
    i =0 
    nuevonodo=Node("127.70.30.{}".format(i),i)
    listaDNodos.append(nuevonodo)
    controlDNodos.append(True)
    i+=1
    while i<64:
        nuevonodo=Node("127.70.30.{}".format(i),i)
        if i<=63 :
         listaDNodos[i-1]._sucesor=nuevonodo
         listaDNodos.append(nuevonodo)
         controlDNodos.append(True)
         nuevonodo._predecesor=listaDNodos[i-1]
    listaDNodos[63]._sucesor=listaDNodos[0]
    listaDNodos[0]._predecesor=listaDNodos[63]

def updatefingertables()
 

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
  updatefingertables(id)
  

def leave(id):
    listaDNodos[id]._predecesor._sucesor=listaDNodos[id]._sucesor
    listaDNodos[id]._sucesor._predecesor=listaDNodos[id]._predecesor
    controlDNodos[id]=False
    listaDNodos[id]._sucesor._keys.extend(listaDNodos[id]._keys)
    updatefingertables(id)

createNodes()


