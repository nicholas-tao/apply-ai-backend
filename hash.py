from cryptography.fernet import Fernet

def initialize():
    key = open('huid-key.txt', 'r').read().strip()
    if key == '':
        key = Fernet.generate_key()
        open('huid-key.txt', 'w').write(key.decode())
    return Fernet(key)

def user_safe_hash(uid):
    return initialize().encrypt(str.encode(uid)).decode()

def database_safe_hash(huid):
    return initialize().decrypt(str.encode(huid)).decode()