class Return_Codes():
    def Code_110():
        return '110 Respuesta de marcador de reinicio.\r\n'
    
    def Code_120(data):
        return f'120 El servicio estará en funcionamiento en {int(data)} minutos.\r\n'
    
    def Code_125():
        return '125 La conexión de datos ya está abierta; comenzando transferencia.\r\n'
    
    def Code_150():
        return '150 Estado del fichero correcto; va a abrirse la conexión de datos.\r\n'
    
    def Code_200():
        return '200 Orden correcta.\r\n'
    
    def Code_202():
        return '202 Orden no implementada, no necesaria en este sistema.\r\n'
    
    def Code_211(data):
        return f'211 {data}\r\n'

    def Code_212():
        return '212 Estado del directorio.\r\n'

    def Code_213():
        return '213 Estado del fichero.\r\n'

    def Code_214(data):
        return f'214 {data}\r\n'
         
    def Code_215(data):
        return f'215 {str(data)} system type.\r\n'
         
    def Code_220():
        return '220 Servicio preparado para nuevo usuario.\r\n'

    def Code_221():
        return '221 Cerrando la conexión de control.\r\n'
         
    def Code_225():
        return '225 Conexión de datos abierta; no hay transferencia en proceso.\r\n'

    def Code_226():
        return '226 Cerrando la conexión de datos.\r\n'
         
    def Code_227(data):
        return f'227 Iniciando modo pasivo en {data}.\r\n'

    def Code_230():
        return '230 Usuario conectado, continúe.\r\n'

    def Code_250():
        return '250 La acción sobre fichero solicitado finalizó correctamente.\r\n'

    def Code_257(data):
        return f'257 "{str(data)}" creada.\r\n'

    def Code_331(data):
        return f'331 Usuario {str(data)} OK, necesita contraseña.\r\n'

    def Code_332():
        return '332 Necesita una cuenta para entrar en el sistema.\r\n'

    def Code_350():
        return '350 La acción requiere más información.\r\n'

    def Code_421():
        return '421 Servicio no disponible, cerrando la conexión de control.\r\n'
         
    def Code_425():
        return '425 No se puede abrir la conexión de datos.\r\n'

    def Code_426():
        return '426 Conexión cerrada; transferencia interrumpida.\r\n'

    def Code_450():
        return '450 Acción no realizada.\r\n'
         
    def Code_451():
        return '451 Acción interrumpida. Error local.\r\n'

    def Code_452():
        return '452 Acción no realizada.\r\n'
         
    def Code_500():
        return '500 Error de sintaxis, comando no reconocido.\r\n'
         
    def Code_501():
        return '501 Error de sintaxis en parámetros o argumentos.\r\n'

    def Code_502():
        return '502 Orden no implementada.\r\n'

    def Code_503():
        return '503 Secuencia de órdenes incorrecta.\r\n'

    def Code_504():
        return '504 Orden no implementada para ese parámetro.\r\n'
         
    def Code_530():
        return '530 No está conectado.\r\n'

    def Code_532():
        return '532 Necesita una cuenta para almacenar ficheros.\r\n'

    def Code_550():
        return '550 Acción no realizada, Fichero no disponible.\r\n'
         
    def Code_551():
        return '551 Acción interrumpida. Tipo de página desconocido.\r\n'

    def Code_552():
        return '552 Acción interrumpida. Se ha sobrepasado el espacio disponible de almacenamiento.\r\n'
         
    def Code_553():
        return '553 Acción no realizada. Nombre de fichero no permitido.\r\n'