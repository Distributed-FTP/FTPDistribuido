# Protocolo de comunicación entre nodos del Chord
# 1000: Get File
# 1001: Search File
# 1002: Search for Edit File
# 1003: Update File
# 1004: Edit File
# 1005: Update Info
# 1006: Save File
# 1007: Unstable Chord
# 1008: Get Successor
# 1009: Get Predecessor

class chord_protocol():
    def get_file():
        return b"1000: Get File"
    
    def search_file():
        return b"1001: Search File"
    
    def search_for_edit_file():
        return b"1002: Search for Edit File"
    
    def update_file():
        return b"1003: Update File"
    
    def edit_file():
        return b"1004: Edit File"
    
    def update_info():
        return b"1005: Update Info"
    
    def save_file():
        return b"1006: Save File"
    
    def unstable_chord():
        return b"1007: Unstable Chord"
    
    def get_successor():
        return b"1008: Get Successor"
    
    def get_predecessor():
        return b"1009: Get Predecessor"
    
    def get_replica():
        return b"1010: Get Replica"
    
    def ok():
        return b"2000: OK"
    
    def error():
        return b"3000: Error"