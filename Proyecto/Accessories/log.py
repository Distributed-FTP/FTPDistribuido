from datetime import datetime
import os
from colorama import init, Fore, Style

class Log():
    def __init__(self):
        self.path = os.getcwd() + "/register.log"
    
    def LogMessageServer(self, data):
        print(Fore.BLUE + Style.BRIGHT + data + Style.RESET_ALL)
    
    def LogClear(self):
        with open(self.path, 'w') as f:
            f.write("")
    
    def LogError(self, ip, port, data):
        date = datetime.now()
        year = str(date.year)
        month = str(date.month)
        if int(month) < 10:
            month = "0" + month
        day = str(date.day)
        if int(day) < 10:
            day = "0" + day
        hour = str(date.hour)
        if int(hour) < 10:
            hour = "0" + hour
        minute = str(date.minute)
        if int(minute) < 10:
            minute = "0" + minute
        second = str(date.second)
        if int(second) < 10:
            second = "0" + second
        data = f"[{year}/{month}/{day} :: {hour}:{minute}:{second}]:: {ip}:{port}:: {data}\n" 
        with open(self.path, 'a') as f:
            f.write(data)
        print(Fore.RED + data + Style.RESET_ALL)
    
    def LogOk(self, ip, port, data):
        date = datetime.now()
        year = str(date.year)
        month = str(date.month)
        if int(month) < 10:
            month = "0" + month
        day = str(date.day)
        if int(day) < 10:
            day = "0" + day
        hour = str(date.hour)
        if int(hour) < 10:
            hour = "0" + hour
        minute = str(date.minute)
        if int(minute) < 10:
            minute = "0" + minute
        second = str(date.second)
        if int(second) < 10:
            second = "0" + second
        data = f"[{year}/{month}/{day} :: {hour}:{minute}:{second}]:: {ip}:{port}:: {data}\n" 
        with open(self.path, 'a') as f:
            f.write(data)
        print(Fore.GREEN + data + Style.RESET_ALL)

    def LogWarning(self, data, ip = None, port = None):
        date = datetime.now()
        year = str(date.year)
        month = str(date.month)
        if int(month) < 10:
            month = "0" + month
        day = str(date.day)
        if int(day) < 10:
            day = "0" + day
        hour = str(date.hour)
        if int(hour) < 10:
            hour = "0" + hour
        minute = str(date.minute)
        if int(minute) < 10:
            minute = "0" + minute
        second = str(date.second)
        if int(second) < 10:
            second = "0" + second
        if ip == None and port == None:
            data = f"[{year}/{month}/{day} :: {hour}:{minute}:{second}]:: {data}\n"
        else:
            data = f"[{year}/{month}/{day} :: {hour}:{minute}:{second}]:: {ip}:{port}:: {data}\n" 
        with open(self.path, 'a') as f:
            f.write(data)
        print(Fore.YELLOW + data + Style.RESET_ALL) 