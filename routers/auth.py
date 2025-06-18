from fastapi import APIRouter
from models import RegisterUsermodel, LoginUsermodel
import db as database
import utils

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={404: {
            "status" : 404,
            "message": "Not found",
            "data": {
                "description": "Not found"
            }
        }
    },
)

#### `login` endpoint to authenticate a user
@router.post("/login")
def login(user: LoginUsermodel):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT * FROM users WHERE username = ? AND password = ?
        ''', (user.username, user.password))
        found_user = cursor.fetchone()
        
        if found_user is None:
            return {
                "code": 401,
                "status": "error",
                "message": "Invalid credentials",
                "data": {}
            }
            
        # Update the user's active status
        cursor.execute('''
            UPDATE users SET is_active = 1 WHERE id = ?
        ''', (found_user['id'],))
        # Generate a JWT token for the user
        token = utils.create_jwt_token({"userId": found_user['id']})
        # Update the user's auth token
        cursor.execute('''
            UPDATE users SET auth_token = ? WHERE id = ?
        ''', (token ,found_user['id'],))
        conn.commit()
        
        return {
            "code": 200,
            "status": "success",
            "message": "Login successful",
            "data": {
                "username": f"Hello, {found_user['username']}!",
                "auth_token": token,
            }
        }
    finally:
        cursor.close()
        conn.close()
    


#### `register` endpoint to create a new user
@router.post("/register")
def register(user: RegisterUsermodel):
    database.create_tables()
    conn = database.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, password, email, full_name, age, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user.username, user.password, user.email, user.full_name, user.age, user.is_active))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return {
            "code": 400,
            "status": "error",
            "message": f"Registration failed: {str(e)}",
            "data": {}
        }
    finally:
        cursor.close()
        conn.close()
    return {
        "code": 201,
        "status": "success",
        "message": "User registered successfully",
        "data": {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "age": user.age,
            "is_active": user.is_active
        }
    }

#### `logout` endpoint to log out a user
@router.post("/logout")
def logout(id: int):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT * FROM users WHERE id = ?
        ''', (id,))
        user = cursor.fetchone()
        cursor.execute('''
            UPDATE users SET is_active = 0 WHERE id = ?
        ''', (id,))
        cursor.execute('''
            UPDATE users SET auth_token = NULL WHERE id = ?
        ''', (id,))
        conn.commit()
        if user is None:
            return {
                "code": 404,
                "status": "error",
                "message": "User not found",
                "data": {
                    
                }
            }

    except Exception as e:  
        conn.rollback()
        return {
            "code": 500,
            "status": "error",
            "message": f"Logout failed: {str(e)}",
            "data": {}
        }
    finally:
        cursor.close()
        conn.close()

    return {
        "code": 200,
        "status": "success",
        "message": "Logout successful",
        "data": {}
    }