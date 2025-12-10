# import bcrypt

def hash_password(password: str):
    # salt = bcrypt.gensalt()
    # hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    # return hashed_password.decode('utf-8')
    return password

def verify_password(entered_password: str, stored_password: str):
    # return bcrypt.checkpw(entered_password.encode('utf-8'), stored_password.encode('utf-8'))
    return entered_password == stored_password
