import os
import socket, sys
from chord import Node
from directory_manager import Directory_Manager
from ftp import ServerFTP
from Accessories.log import Log
from threading import Thread

IP = '0.0.0.0'
PORT = 21
path = os.getcwd()


def server_listener():
    global listen_sock
    log = Log(path)
    log.LogClear()
    log.LogMessageServer(f'FTP Server - {IP}:{PORT} \n')
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    log.LogMessageServer('Binding... \n')
    listen_sock.bind((IP, PORT))
    listen_sock.listen(5)
    log.LogMessageServer(f'Servidor iniciado en {listen_sock.getsockname( )}\n')
    while True:
        node = Node(IP)
        directory_manager = Directory_Manager(path, node)
        connection, address = listen_sock.accept()
        connection.settimeout(5)
        log.LogWarning(f'Conexion aceptada en {address}')
        f = ServerFTP(connection, address, IP, PORT, log, path, directory_manager)
        f.start()

if __name__ == "__main__":
    listener = Thread(target=server_listener)
    listener.start( )
    message = input().lower()
    if message == "q":
        listen_sock.close()
        os._exit(1)