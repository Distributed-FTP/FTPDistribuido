class Help_Commands():
    def ALL():
        return "All commands"
    
    def USER():
        command = "NOMBRE DE USUARIO (USER)"
        description = "El argumento es una cadena Telnet que identifica al usuario. Esta identificación es la que requiere el servidor para acceder a su sistema de ficheros. Normalmente esta será la primera orden a transmitir una vez establecida la conexión de control (algunos ordenadores lo pueden requerir). El servidor puede requerir información adicional como una contraseña y/o cuenta. Los servidores pueden permitir una nueva orden USER en cualquier momento para cambiar el control de acceso y/o la información de la cuenta. Esto tiene el efecto de descartar cualquier información anterior sobre usuario, contraseña y cuenta y comienza la secuencia de acceso otra vez. Todos lo parámetros de la transferencia permanecen sin cambios y cualquier transferencia de fichero en curso se completa bajo los anteriores parámetros de control de acceso."
        return command + "\n" + description
    
    def PASS():
        command = "CONTRASEÑA (PASS)"
        description = "El argumento es una cadena Telnet especificando la contraseña del usuario. Esta orden debe ir inmediatamente precedida por la orden USER y, para algunos ordenadores, completa la identificación del usuario para el control de acceso. Como la información de la contraseña es un dato confidencial, es preferible, en general, \"enmascararla\" o evitar mostrarla en pantalla. Parece que el servidor no tiene un medio a prueba de tontos para conseguir esto. Por tanto es responsabiliad del proceso user-FTP el ocultar la información sobre la contraseña."
        return command + "\n" + description
    
    def CWD():
        command = "CAMBIO DE DIRECTORIO DE TRABAJO (CWD)"
        description = "Esta orden permite al usuario trabajar en un directorio o conjunto de datos [data set] diferente para almacenar o recuperar información sin alterar su información de entrada o de cuenta. Los parámetros de transferencia permanecen sin cambios. El argumento es un nombre de ruta especificando el directorio o alguna otra agrupación de ficheros dependiente del sistema."
        return command + "\n" + description
        
    def CDUP():
        command = "CAMBIAR AL DIRECTORIO PADRE (CDUP)"
        description = "Esta orden es un caso especial de CWD y se incluye para simplificar la implementación de programas para transferir árboles de directorios entre sistemas operativos que tienen diferentes formas de nombrar al directorio padre."
        return command + "\n" + description
    
    def REIN():
        command = "REINICIALIZAR (REIN)"
        description = "Esta orden termina una orden USER, descargando todos los datos del entrada/salida y la información de cuenta, excepto que si hay alguna transferencia en proceso permite que termine. Todos los parámetros se inician con sus valores por defecto y la conexión de control se deja abierta. El estado alcanzado es idéntico al que se tiene inmediatamente después de abrir la conexión de control. Posiblemente se espere una orden USER a continuación de esta."
        return command + "\n" + description
        
    def QUIT():
        command = "DESCONECTAR (QUIT)"
        description = "Esta orden termina una orden USER y si no hay en proceso ninguna transferencia, cierra la conexión de control. Si hay una transferencia de fichero en proceso, la conexión permanecerá abierta hasta que el servidor envíe una respuesta con el resultado de la transferencia y luego se cierra. Si el proceso de usuario está transfiriendo ficheros para varios usuarios (USERs) pero no quiere cerrar la conexión y reabrirla para cada usuario, se debería usar el comndo REIN en lugar de QUIT. Un cierre inesperado de la conexión de control provoca que el servidor actúe como si hubiera recibido las órdenes interrumpir (ABOR) y desconectar (QUIT)."
        return command + "\n" + description
        
    def PORT():
        command = "PUERTO DE DATOS (PORT)"
        description = "El argumento es una especificación ordenador-puerto para el puerto que será usado en la conexión de datos. Hay valores por defecto tanto para el puerto de usuario como para el del servidor y, bajo circunstancias normales, esta orden y su respuesta no son necesarias. Si se usa esta orden, el argumento es la concatenación de una dirección IP (32 bits) y un puerto TCP (16 bits). Esta información está repartida en campos de 8 bits y el valor de cada campo se transmite como un número decimal (representado como una cadena de caracteres). Los campos están separados por comas. Una orden PORT podría ser algo así:\n\nPORT h1,h2,h3,h4,p1,p2\n\ndonde h1 es el número decimal correspondiente a los 8 bits más altos de la dirección IP del ordenador."
        return command + "\n" + description
    
    def PASV():
        command = "PASIVO (PASV)"
        description = "Esta orden solicita al server-DTP que \"escuche\" en un puerto de datos (que no es el puerto por defecto) y espere a recibir una conexión en lugar de iniciar una al recibir una orden de transferencia. La respuesta a este comando incluye la dirección IP y el puerto donde este servidor está esperando a recibir la conexión."
        return command + "\n" + description
        
    def MODE():
        command = "MODO DE TRANSFERENCIA (MODE)"
        description = "El argumento es un único carácter Telnet especificando un modo de transferencia de los descritos en la sección Modos de Transmisión.\n\nLos posibles códigos son los siguientes:\n\nS - Flujo\n\nB - Bloque\n\nC - Comprimido\n\nEl modo por defecto es Flujo."
        return command + "\n" + description
        
    def TYPE():
        command = "TIPO DE REPRESENTACION (TYPE)"
        description = "El argumento especifica un tipo de representación tal y como se describió en la sección Representación de Datos y Almacenamiento. Algunos tipos requieren un segundo parámetro. El primer parámetro es un único carácter Telnet y el segundo, para ASCII y EBCDIC, también; el segundo parámetro para tamaño de byte local es un entero decimal. Los parámetros están separados por un <SP> (espacio, código ASCII 32).\n\nSe asignan los siguientes códigos para tipos:\nA - ASCII |    | N - No para imprimir\n        |-><-| T - Formateo con caracteres Telnet\nE - EBCDIC|    | C - Control de carro (ASA)\n        /    \\nI - Imagen\n\nL <tamaño de byte> - Tamaño de byte local\n\nLa representación por defecto es ASCII no para imprimir. Si se cambia el parámetro de formato y más tarde sólo el primer argumento, el formato vuelve a ser el inicial por defecto (no para imprimir)."
        return command + "\n" + description
        
    def STRU():
        command = "ESTRUCTURA DEL FICHERO (STRU)"
        description = "El argumento es un único carácter Telnet especificando una estructura de fichero de las descritas en la sección Representación de Datos y Almacenamiento.\n\nExisten los siguientes códigos para la estructura:\n\nF - Fichero (sin estructurar en registros)\nR - Estructurado en registros P - Estruturado en páginas\n\nLa estructura por defecto es Fichero."
        return command + "\n" + description
                
    def STOR():
        command = "ALMACENAR (STOR)"
        description = "Esta orden hace que el server-DTP lea los datos transferidos por la conexión de datos y los guarde en un fichero en el servidor. Si el fichero especificado en el nombre de ruta existe en el servidor, su contenido se debe reemplazar con los datos recibidos. Se crea un fichero nuevo en el servidor si el indicado no existía ya."
        return command + "\n" + description
        
    def STOU():
        command = "ALMACENAR UNICO (STOU)"
        description = "Not Implemented"
        description = "Esta orden se comporta igual que STOR sólo que el fichero resultante se crea en el directorio actual con un nombre único para ese directorio."
        return command + "\n" + description
        
    def RETR():
        command = "RECUPERAR (RETR)"
        description = "Esta orden hace que el server-DTP transfiera una copia del fichero especificado en el nombre de ruta al proceso que está al otro lado de la conexión de datos. El estado y el contenido del fichero en el servidor debe permanecer tal y como estaba."
        return command + "\n" + description
        
    def LIST():
        command = "LISTAR (LIST)"
        description = "Esta orden hace que el servidor envíe una listado de los ficheros a través del proceso de transferencia de datos pasivo. Si el nombre de ruta u otra agrupación de ficheros, el servidor debe transferir una lista de los ficheros en el directorio indicado. Si el nombre de ruta especifica un fichero, el servidor debería enviar información sobre el fichero. Si no se indica argumento alguno, implica que se quiere listar el directorio de trabajo actual o directorio por defecto. Los datos se envían a traves de la conexión de datos con tipo ASCII o EBCDIC. (El usuario se debe asegurar del tipo con TYPE).  Como la información sobre un fichero puede variar mucho de un sistema a otro, es muy difícil que ésta pueda ser procesada automáticamente, pero puede ser útil para una persona."
        return command + "\n" + description
        
    def NLST():
        command = " LISTAR NOMBRES (NLST)"
        description = "Not Implemented"
        description = "Esta orden hace que se envíe un listado de directorio desde el servidor. El nombre de ruta indica un directorio u otra agrupación de ficheros específica del sistema; si no hay argumento, se asume el directorio actual. Los datos se transfieren en formato ASCII o EBCDIC a través de la conexión de datos separados unos de otros por <CRLF> o <NL>. (Una vez más el usuario se debe asegurar con TYPE). La función de esta orden es devolver información que pueda ser usada por un programa para procesar posteriormente los ficheros automáticamente. Por ejemplo, implementando una función que recupere varios ficheros."
        return command + "\n" + description
        
    def APPE():
        command = "AÑADIR (con creación) (APPE)"
        description = "Not Implemented"
        description = "Esta orden hace que el server-DTP reciba datos a través de la conexión de control y los guarde en un fichero en el servidor. Si el fichero especificado en el nombre de ruta existe, los datos se añaden a ese fichero; si no, se crea un fichero nuevo en el servidor."
        return command + "\n" + description
        
    def RNFR():
        command = "RENOMBRAR DE (RNFR)"
        description = "Esta orden indica el fichero que queremos cambiar de nombre en el servidor. Debe ir inmediatamente seguida de la orden \"renombrar a\" con el nuevo nombre para el fichero."
        return command + "\n" + description
        
    def RNTO():
        command = "RENOMBRAR A (RNTO)"
        description = "Esta orden especifica el nuevo nombre para el fichero indicado mediante el comando RNFR. Las dos órdenes seguidas hacen que el fichero cambie de nombre."
        return command + "\n" + description
        
    def DELE():
        command = "BORRAR (DELE)"
        description = "Esta orden borra en el servidor el fichero indicado en el nombre de ruta. Si se quiere tener un nivel extra de protección (del tipo \"¿Seguro qu quiere borrar el fichero?\"), la debería proporcionar el proceso user-FTP."
        return command + "\n" + description
        
    def RMD():
        command = "BORRAR DIRECTORIO (RMD)"
        description = "Esta orden borra en el servidor el directorio indicado."
        return command + "\n" + description
        
    def MKD():
        command = "CREAR DIRECTORIO (MKD)"
        description = "Esta orden crea el directorio indicado en el servidor."
        return command + "\n" + description
        
    def PWD():
        command = "MOSTRAR EL DIRECTORIO DE TRABAJO (PWD)"
        description = "Esta orden hace que el servidor nos devuelva en la respuesta el nombre del directorio actual."
        return command + "\n" + description
        
    def ABOR():
        command = "INTERRUMPIR (ABOR)"
        description = "Este comando pide al servidor que interrumpa la orden de servicio FTP previa y cualquier transferencia de datos asociada. La orden de interrupción puede requerir alguna \"acción especial\", tratada más adelante, para forzar el reconocimiento de la orden por el servidor. No se hará nada si la orden anterior ha finalizado (incluyendo la transferencia de datos). El servidor no cierra la conexión de control, pero puede que sí cierre la conexión de datos. Hay dos posibles casos para el servidor al recibir esta orden: la orden de servicio FTP está ya terminada, o aún está en ejecución."
        return command + "\n" + description
        
    def SYST():
        command = "SISTEMA (SYST)"
        description = "Esta orden devuelve el tipo de sistema operativo del servidor."
        return command + "\n" + description
        
    def HELP():
        command = "AYUDA (HELP)"
        description = "Esta orden hace que el servidor envíe información sobre la implementación del FTP a través de la conexión de control. La orden puede tener un argumento que debe ser un nombre de orden y así devuelve información más específica como respuesta."
        return command + "\n" + description
        
    def NOOP():
        command = "NO OPERACION (NOOP)"
        description = "Esta orden no afecta a ningún parámetro ni orden introducida previamente. No hace nada más que provocar que el servidor envíe una respuesta OK."
        return command + "\n" + description