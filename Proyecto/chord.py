from socket import socket
import Pyro4
import threading

def dame():
 uri = "PYRO:example.calculator@192.168.43.62:8002"
 remote_calculator = Pyro4.Proxy(uri)
 print(remote_calculator.add(1,2))

threading.Thread(target=dame, args=()).start()

 
