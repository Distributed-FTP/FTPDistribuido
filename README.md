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

## **[start.py](https://github.com/Distributed-FTP/FTPDistribuido/blob/master/Proyecto/start.py)**
Esta clase contiene la configuración inicial de nuestro servidor, mediante la utilización de sockets y de hilos se logra gestionar varias conexiones de distintos clientes al mismo servidor. Nos vimos forzados a implementar esta idea dado que FileZilla utiliza varias conexiones con un mismo usuario, por ejemplo, cada vez que se envía/recibe alguna información por la conexción de datos se hace necesario que se desconecte y conecte nuevamente. Para una conexión definimos un tiempo de espera de 5 segundos de manera que cuando haya inactividad deja de escuchar por ese hilo hasta una nueva conexión.

## **[ftp.py](https://github.com/Distributed-FTP/FTPDistribuido/blob/master/Proyecto/ftp.py)**
Esta clase implementa el protocolo FTP en sí, Cuando se inicia el servidor se envía al cliente un mensaje de bienvenida para que el cliente sepa que se recibió correctamente la conexión y ya se puede comenzar a intercambiar información. Se recibe el mensaje del socket y se procesa la orden, se deocdifica a UTF-8 y se analiza la primera palabra de la línea y así se busca en una lista cuál es el comando correcto. Si el comando no aparece en la lista se devuelve un mensaje que el comando no fue definido. Es importante destacar que el protocolo FTP trabaja con 2 conexiones por cada cliente, una conexión de control que es por donde se transfieren las respuestas de los comandos para facilitar la comunicación con el cliente y ua conexión de datos que es por donde se van a mover los archivos y demás información.

## **[log.py](https://github.com/Distributed-FTP/FTPDistribuido/blob/master/Proyecto/log.py)**
Esta clase contiene varios métodos que escriben todas las operaciones que realiza un cliente en el archivo "register.log", le decidimos dar un formato con bastante información, ya que contiene la fecha y hora, el IP y PUERTO por el que se realizó la operación y si es una operación que requiere que el usuario se haya autenticado también se almacena el nombre del usuario.

## **[return_codes.py](https://github.com/Distributed-FTP/FTPDistribuido/blob/master/Proyecto/return_codes.py)**
En esta clase tenemos definido todos los códigos de respuesta que daría nuestro sistema al ejecutar cualquier operación, ya sea su resultado satisfactorio o no.

## **[help.py](https://github.com/Distributed-FTP/FTPDistribuido/blob/master/Proyecto/help.py)**
La clase de ayuda contiene las ayduas, valga la redundancia, de todos los comandos que tenemos implementados. Así como una ayuda general que le dice al usuario que parámetros pasarle al comando HELP para acceder a alguna en específico.

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

# **Chord**
.............