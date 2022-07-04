import Pyro4
import hashlib


def get_proxy(id):
    Pyro4.Proxy(f'PYRONAME:CHORD{id}')
    with Pyro4.Proxy(f'PYRONAME:CHORD{id}') as p:
        try:
            p._pyroBind()
            return p
        except:
            return None


def hashing(bits, string):
    try:
        hash = hashlib.sha256(string.encode('utf-8', 'ignore')).hexdigest()
        hash = int(hash, 16) % pow(2, bits)
        return hash
    except:
        return None