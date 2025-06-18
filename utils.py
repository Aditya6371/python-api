from jose import jwt, JWTError
import db as database

secret_key = "your_secret_key"
algorithm = "HS256"

def create_jwt_token(data: dict):
    return jwt.encode(data, secret_key, algorithm=algorithm)

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError:
        return None
    
def verify_user_auth_token(auth_token: str):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    if not auth_token:
        return False
    try:
        payload = verify_jwt_token(auth_token)
        if payload:
            userId = payload.get("user_name")
            cursor.execute('SELECT * FROM users WHERE username = ?', (userId,))
            user = cursor.fetchone()
            if user and user['auth_token'] == auth_token:   
                return True
            else:
                return False
            
    except Exception as e:
        print(f"Token verification failed: {str(e)}")
    finally:
        cursor.close()
        conn.close()
    return False