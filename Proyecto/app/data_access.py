import psycopg2


class ServerDataBase():
    def __init__(self):
        print('Conectando a la base de datos PostgreSQL...')
        self.connection = psycopg2.psycopg2.connect(host="localhost", database="FTPDistributedDB", user="postgres", password="biUrwej1obwok")

        cur = self.connection.cursor()
                
        print('La version de PostgreSQL es la:')
        cur.execute('SELECT version()')

        version = cur.fetchone()
        print(version)
    
    def get_permissions_from_a_user(self, username, password):
        cur = self.connection.cursor()

        cur.execute('')

        return cur.fetch()