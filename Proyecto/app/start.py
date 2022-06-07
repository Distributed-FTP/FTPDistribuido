from numpy import byte
from ftp import ServerFTP

IP = '127.0.0.1'
PORT = 2331
PASIVE = False

server = ServerFTP(IP, PORT)

print(f'FTP Server - {IP}:{PORT} \n')

print('Binding... \n')

server.bind()
server.accept()
server.welcome_message()

while True:
    if PASIVE:
        server.accept()
        server.welcome_message()
        
    
    print("Waiting instructions \n")

    data = server.receive()
    
    data = data.decode('utf-8',errors='ignore')
    if not data: break

    data = str(data).replace("b'", '')
    data = data.replace("\\r\\n", '')
    data = data.replace("\r\n", '')
    
    print("Received instruction: {0}\n".format(data))

    data_arr = data.split(' ')

    cmd = data_arr[0]
    
    #Login
    if "USER" in cmd:
        server.user_command(data)
    elif "PASS" in cmd:
        server.pass_command(data)
    elif "ACCT" in cmd:
        server.acct_command(data)
    elif "CWD" in cmd:
        server.cwd_command(data)
    elif "CDUP" in cmd:
        server.cdup_command(data)
    elif "SMNT" in cmd:
        server.smnt_command()
    
    #Logout
    elif "REIN" in cmd:
        server.rein_command()
    elif "QUIT" in cmd:
        server.quit_command()
    
    #Transfer parameters
    elif "PORT" in cmd:
        server.port_command(data)
        PASIVE = True
    elif "PASV" in cmd:
        server.pasv_command()
    elif "MODE" in cmd:
        server.mode_command()
    elif "TYPE" in cmd:
        server.type_command(data)
    elif "STRU" in cmd:
        server.stru_command()

    #File action commands
    elif "ALLO" in cmd:
        server.allo_command(data)
    elif "REST" in cmd:
        server.rest_command(data)
    elif "STOR" in cmd:
        server.stor_command(data)
    elif "STOU" in cmd:
        server.stou_command(data)
    elif "RETR" in cmd:
        server.retr_command(data)
    elif "LIST" in cmd:
        server.list_command()
    elif "NLST" in cmd:
        server.nlst_command()
    elif "APPE" in cmd:
        server.appe_command(data)
    elif "RNFR" in cmd:
        server.rnfr_command(data)
    elif "RNTO" in cmd:
        server.rnto_command(data)
    elif "DELE" in cmd:
        server.dele_command(data)
    elif "RMD" in cmd:
        server.rmd_command(data)
    elif "MKD" in cmd:
        server.mkd_command(data)
    elif "PWD" in cmd:
        server.pwd_command(data)
    elif "ABOR" in cmd:
        server.abor_command(data)

    #Informational commands
    elif "SYST" in cmd:
        server.syst_command()
    elif "STAT" in cmd:
        server.stat_command()
    elif "HELP" in cmd:
        server.help_command()

    #Miscellaneous commands
    elif "SITE" in cmd:
        server.site_command()
    elif "NOOP" in cmd:
        server.noop_command()
    else:
        server.command_not_found()