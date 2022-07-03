import os


class Admin():
    def __init__(self, path: str):
        self.username = ""
        self.path = path + "/Reports/database.db"
        self.password = ""

    def execute(self, request):
        list = request.split(' ')
        if list[0] == "add_user":
            self.username = list[1]
        elif list[0] == "add_pass":
            self.password = list[1]
            if self.username != "":
                with open(self.path, 'a') as f:
                    f.write(f"\r\n****\r\n{self.username}\r\n****\r\n{self.password}\r\n****\r\n")
                self.password = ""
                self.username = ""
        elif list[0] == "remove_user":
            self.username = list[1]
            users = ""
            with open(self.path, 'rb') as f:
                while True:
                    bytes_read = f.read()
                    if bytes_read == b'':
                        break
                    else:
                        users+=str(bytes_read)
            users = str(users).replace("b'", '')
            users = str(users).replace("'", '')
            users = users.split("\\r\\n****\\r\\n")
            write = ""
            for i in range(1,len(users)-1,3):
                if str(users[i])!=str(self.username):
                    write += f"\r\n****\r\n{users[i]}\r\n****\r\n{users[i+1]}\r\n****\r\n"
            with open(self.path, 'w') as f:
                f.write(write)
            self.password = ""
            self.username = ""
                    
                    
if __name__ == "__main__":
    admin = Admin(os.getcwd())
    while True:
        message = input().lower()
        if message == "q":
            os._exit(1)
        else:
            admin.execute(message)