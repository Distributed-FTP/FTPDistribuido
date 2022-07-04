import Pyro4

#Server= Pyro4.Daemon(
  #      host="192.168.43.62",
  #      port=8003,
  #      ns=False
   # )



uri = "PYRO:example.calculator@192.168.43.62:8002"

remote_calculator = Pyro4.Proxy(uri)
print(remote_calculator.add(1,2))
