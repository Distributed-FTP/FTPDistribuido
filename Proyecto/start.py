import os
import socket, sys
from ftp import ServerFTP
from log import Log
from threading import Thread

IP = '0.0.0.0'
PORT = 21
path = os.getcwd()


def server_listener():
    global listen_sock
    log = Log()
    log.LogClear()
    log.LogMessageServer(f'FTP Server - {IP}:{PORT} \n')
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    log.LogMessageServer('Binding... \n')
    listen_sock.bind((IP, PORT))
    listen_sock.listen(5)
    log.LogMessageServer(f'Servidor iniciado en {listen_sock.getsockname( )}\n')
    while True:
        connection, address = listen_sock.accept()
        connection.settimeout(20)
        log.LogWarning(f'Conexion aceptada en {address}')
        f = ServerFTP(connection, address, IP, PORT, log, path )
        f.start()

if __name__ == "__main__":
    listener = Thread(target=server_listener)
    listener.start( )

    message = input().lower()
    if message == "q":
        listen_sock.close()
        os._exit(1)