# **FTPDistribuido**
## **Autores:**
    Arnel Sánchez Rodríguez C-412
    Darián Ramón Mederos C-412
    Víctor Manuel Lantigua Cano C-412

# **Introducción**
El protocolo de transferencia de ficheros (o FTP, por sus siglas, en inglés) quedó especificado en la RFC 959, en el año 1985. Su objetivo es la reglamentación de las transmisiones de archivos entre máquinas remotas, y es, hoy por hoy, una de las aplicaciones más extendidas de Internet, junto con la WWW y el correo electrónico. 

La implementación clásica de un servicio FTP se basa en una arquitectura cliente / servidor. Es éste el encargado de alojar el sistema de directorios y archivos que serán accesibles por parte de aquel. Utilizando como cliente FileZilla nuestra tarea fue implementar un servidor que fuere capaz de comunicarse con el cliente y tener un sistema de archivos distribuido.

# **Estructura del servidor FTP**
Basado en la definición de RFC 959 hicimos una implementación de FTP. Tenemos la implementación del protocolo dividido en varios módulos:

* El setup del sistema (start.py)
* La clase encargada de gestionar los comandos y ejecutarlos, en otras palabras, la implementación del FTP (ftp.py)
* Una clase encargada de dejar registrado todas las acciones realizadas por los usuarios en busca de una mayor seguridad en nuestro sistema (log.py)
* Una clase estática con la lista de respuestas posibles para todos los comandos que propone la documentación de RFC (return_codes.py)
* Una clase estática que contiene todas las ayudas posibles que brindará nuestro sistema (help.py)
* Una clase que se encarga de manipular los archivos y la direcciones y comunicarse con el nodo de Chord asociado (directory_manager.py)
* Una clase Admin que se encarga de agregar o eliminar permisos a nuestro servidor FTP (admin.py)
* La clase Chord que se encarga de implementar dicho algoritmo (chord.py).
* El directorio Accesories contiene clases útiles a nuestro sistema para encargarse de responsabilidades secundarias a nuestro hilo principal de desarrollo.
* El directorio Reports contiene 3 archivos, **database.db** que contiene las cuentas de accesos de los distintos usuarios a nuestro sistema, **files.fl** que contiene la lista de archivos presente en nuestro sistema, **register.log** que contiene la lista de logs que se han sucedido en el sistema  desde su inicio.
* El directorio root es la carpeta raíz a partir de la que se va a forjar la jerarquía de nuestros sistema de ficheros.

## **[start.py](https://github.com/Distributed-FTP/FTPDistribuido/blob/master/Proyecto/start.py)**
Esta clase contiene la configuración inicial de nuestro servidor, mediante la utilización de sockets y de hilos se logra gestionar varias conexiones de distintos clientes al mismo servidor. Nos vimos forzados a implementar esta idea dado que FileZilla utiliza varias conexiones con un mismo usuario, por ejemplo, cada vez que se envía/recibe alguna información por la conexción de datos se hace necesario que se desconecte y conecte nuevamente. Para una conexión definimos un tiempo de espera de 5 segundos de manera que cuando haya inactividad deja de escuchar por ese hilo hasta una nueva conexión.

## **[ftp.py](https://github.com/Distributed-FTP/FTPDistribuido/blob/master/Proyecto/ftp.py)**
Esta clase implementa el protocolo FTP en sí, Cuando se inicia el servidor se envía al cliente un mensaje de bienvenida para que el cliente sepa que se recibió correctamente la conexión y ya se puede comenzar a intercambiar información. Se recibe el mensaje del socket y se procesa la orden, se deocdifica a UTF-8 y se analiza la primera palabra de la línea y así se busca en una lista cuál es el comando correcto. Si el comando no aparece en la lista se devuelve un mensaje que el comando no fue definido. Es importante destacar que el protocolo FTP trabaja con 2 conexiones por cada cliente, una conexión de control que es por donde se transfieren las respuestas de los comandos para facilitar la comunicación con el cliente y ua conexión de datos que es por donde se van a mover los archivos y demás información.

## **[directory_manager.py](https://github.com/Distributed-FTP/FTPDistribuido/blob/master/Proyecto/directory_manager.py)**
La clase de manager de directorios es la encargada de gestionar todo lo relacionado con directorios y archivos. Ella po sí sola se encarga de comunicarse con el nodo de Chord para que este le haga llegar el archivo solicitado.

## **[admin.py](https://github.com/Distributed-FTP/FTPDistribuido/blob/master/Proyecto/admin.py)**
La clase Admin contiene una pequeña implemetación de un pequeño cliente que permite manipular los accesos de los uaurios, o sea, añadir o eliminar nombres de usuarios y contraseñas de clientes.

### Comandos para modificar accesos
```
add_user <Username>: Añade nombre de usuario
add_pass <Password>: Añade contraseña a un nombre de usuario insertado antes
remove_user <Username>: Elimina nombre de usuario y su contraseña
```


## **Comandos implementados**
Login | Logout | Parámetros de transferencia | Acciones sobre ficheros | Ordenes informativas | Otras órdenes
---------|----------|---------|---------|---------|---------|
 USER | REIN | PORT | STOR | SYST | NOOP |
 PASS | QUIT | PASV | STOU | HELP |      |
 CWD  |      | MODE | RETR |      |      |
 CDUP |      | TYPE | LIST |      |      |
|     |      | STRU | NLST |      |      |
|     |      |      | APPE |      |      |
|     |      |      | RNFR |      |      |
|     |      |      | RNTO |      |      |
|     |      |      | DELE |      |      |
|     |      |      | RMD  |      |      |
|     |      |      | PWD  |      |      |
|     |      |      | ABOR |      |      |

## **Consideraciones tenidas en cuenta**
* A la hora de implementar el servidor FTP tenemos como raíz de directorio root, pero si se accede como usuario **anonymous** el root cambia y se accede a otra carpeta.
* En todos los nodos de Chord tenemos replicada la misma jerarquía de directorios, pero sin los archivos.
* A la hora de subir un archivo se sube el archivo desde la clase FTP hacia el path donde se debe ubicar, se le notifica a Chord, este coge el archivo lo alamcena en los nodos que tienen capacidad de almacenamiento y carga necesaria y luego lo borra del nodo que lo subió para aligerar la carga.
* A la hora de bajar un archivo se hace un proceso similar al de subida, pero primero se le notifica que se quiere bajar el archivo con path "/root/....." Chord busca en que nodo está y lo trae hacia el nodo que lo solicitó y lo ubica en su dirección, el servidor de FTP recbe la respuesta de que puede manipular el archivo, lo envía al cliente que lo solicitó y se le notifica a Chord que puede eliminarlo si no es su ubicación origial.
* Todo el tiempo mantenemos replicada la carpeta Reports para lograr tener todos los logs de la red en todos los nodos, todos los accesos a la red en todos los nodos y la jerarquía de archivos presentes en toda nuestra red de servidores.

## **Reportes**

### database.db
```

****
Arnel
****
Prueba123*
****

****
admin
****
admin123*
****

```

### files.fl
```
D~~/root/
D~~/root/anonymous/
F~~/root/file.txt/
```

### register.log
```
[2022/07/02 :: 22:34:00]:: Conexion aceptada en ('127.0.0.1', 52872)
[2022/07/02 :: 22:34:00]:: 127.0.0.1:52872:: El usuario ha insertado un comando no reconocido.
[2022/07/02 :: 22:34:00]:: 127.0.0.1:52872:: El usuario ha insertado un comando no reconocido.
[2022/07/02 :: 22:34:00]:: 127.0.0.1:52872:: Usuario Arnel necesita insertar contrasenna.
[2022/07/02 :: 22:34:00]:: 127.0.0.1:52872:: Usuario Arnel conectado.
[2022/07/02 :: 22:34:00]:: 127.0.0.1:52872:: El usuario Arnel accedio al directorio /root/.
[2022/07/02 :: 22:34:00]:: 127.0.0.1:52872:: El usuario Arnel ha activado el tipo I.
[2022/07/02 :: 22:34:00]:: 127.0.0.1:52872:: El usuario Arnel ha activado el modo pasivo.
[2022/07/02 :: 22:34:00]:: Conectando a ('127.0.0.1', 49299)
```

### Resumen de implementacion de Chord e interaccion con archivos

El DHT que utilizamos en nuestro proyecto fue chord , con el cual creamos la logica de estabilidad de nuestro sistema. Empezando por la eleccion de lider , escogimos utilizar la estrategia de que un nodo no conozca a el lider cuando se quiere conectar al sistema , el nodo buscara en el rango de la red a la que esta conectada por todos los posibles ips , esto lo hara con una conexion de cliente esperando encontrar un servidor del otro lado, para las conexiones entre nodos utilizamos la libreria Pyro4 , aunque antes utilizamos tambien sockets directamente.Cada nodo cuando se crea creara un Servidor y un cliente por un puerto especifico , el servidor con el objetivo de recibir alguna conexion de otro nodo que se quiera conectar a el y cliente para buscar algun nodo activo, si un nodo encuentra a otro ent le mandara un codigo para poder unirse a la red , si el nodo receptor es el lider entonces guarda el ip del nodo del que recibe la senal , asi como la lista que el nodo que ejerce de cliente encontro(mas adelante explico en que consiste) y le retorna un mensaje para que sepa que encontro al lider y no debe seguir buscando .En caso de que el nodo servidor no sea el lider pero lo conozca este se lo manda para que se conecte directamente al lider y pase el procedimiento explicado anteriormente.En caso de que un nodo se encuentre con otro nodo que no tiene lider el nodo encontrado se anade a una lista de nodos encontrados del nodo que lo encontro y de esta forma o siempre hay un lider o los nodos saben armar un sistema y escoger al lider.

Otro tema importante es la estabilidad , el lider es quien se encarga de comprobar la conexion de los nodos del sistema periodicamente y como ya dijimos antes es quien une al sistema los nodos que quieren conectarse ,asi como le avisa a los demas nodos del sistema algun nodo se desconecta del sistema.El lider mantiene actualizada la informacion de los demas nodos y sus finguertables. Los nodos que no son lider constantemente estan dando ping al lider , si el lider se cae ent el lider sera el nodo del sistema que menor id tenga.

En cuanto a los archivos cuando vamos a subir uno al servidor FTP lo guardamos en un nodo , lo replicamos en n nodos sucesores.De esta forma no hay manera que desconectando n-1 nodos el archivo no este disponible. Un archivo va a tener un id especifico el cual esta compuesto por el identificador del nodo original donde se creo , y un codigo hash que identificara el archivo para poderlo diferenciar de una posible edicion.Cada nodo esta preparado para ser el lider , tiene toda la informacion necesaria. Cada nodo tiene una lista de los hash de los archivos que contiene , ya sean archivos originales o copias . Mediante el diccionaario de nombre files_system controlamos en que nodos esta replicado un archivo . Las llaves del diccionario son los hash de los archivos almacenados en el nodo y los valores los ips donde esta replicado el nodo llave.Tambien pueden haber hash llaves de archivos que no estan contenidos en el nodo.Esto pasa cuando se edita un archivo , se deja el hashantiguo teniendo como value al hash nuevo para en los casos en que un nodo este entrando al sistema y tiene un archivo desactualizado saber donde se encuentra el actualizado.



