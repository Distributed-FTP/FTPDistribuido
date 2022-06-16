import socket, sys
from ftp import ServerFTP
from threading import Thread

IP = '0.0.0.0'
PORT = 21

def server_listener():
    global listen_sock
    print(f'FTP Server - {IP}:{PORT} \n')
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Binding... \n')
    listen_sock.bind((IP, PORT))
    listen_sock.listen(5)
    print(f'Servidor iniciado en {listen_sock.getsockname( )}')
    while True:
        connection, address = listen_sock.accept()
        connection.settimeout(20)
        print(f'Conexion aceptada en {address}')
        f = ServerFTP(connection, address, IP, PORT )
        f.start()

if __name__ == "__main__":
    listener = Thread(target=server_listener)
    listener.start( )

    if sys.version_info[0] < 3:
        input = raw_input

    message = input().lower()
    if message == "q":
        listen_sock.close()
        sys.exit()