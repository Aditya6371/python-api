import sqlite3
from typing import Optional
from fastapi import APIRouter, HTTPException
import db as database

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

#### `get_all_user` endpoint to retrieve all user
@router.get("/all_users")
def get_all_users():
    conn = database.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT * FROM users
        ''')
    except Exception as e:
        conn.close()
        return {
            "code": 500,
            "status": "error",
            "message": f"Failed to retrieve users: {str(e)}",
            "data": {}
        }
    # Fetch all users
    users = cursor.fetchall()   
    if not users:
        conn.close()
        return {
            "code": 204,
            "status": "No Content",
            "message": "No users found",
            "data": {}
        }
    # Convert Row objects to dict for easier JSON serialization
    cursor.close()
    conn.close()
    return {
        "code": 200,
        "status": "success",
        "message": "All users retrieved successfully",
        "data": {
            "users": [dict(user) for user in users]  # Convert Row objects to dict
        }
    }

#### `get_user` endpoint to retrieve a user by ID
@router.get("/get_user")
def get_user(id: Optional[int] = None):
    if id is None:
        raise HTTPException(status_code=400, detail="User ID must be provided")
    conn = database.get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT * FROM users WHERE id = ?
        ''', (id,))
        user = cursor.fetchone()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user: {str(e)}")
    
    if user is None:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    cursor.close()
    conn.close()
    return {
        "code": 200,
        "status": "success",
        "message": "User retrieved successfully",
        "data": {
            "user": dict(user)  # Convert Row object to dict
        }
    }

#### Delete user endpoint to delete a user by ID or all users
@router.delete("/delete_user")
def delete_user(id: Optional[int] = None, all_delete: Optional[bool] = False, delete_table: Optional[bool] = False):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Handle table deletion
        if delete_table:
            database.drop_tables()
            return {
                "code": 200,
                "status": "success",
                "message": "Table deleted successfully",
                "data": {}
            }
            
        # Handle all users deletion
        if all_delete:
            cursor.execute('DELETE FROM users')
            conn.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="No users found to delete")
            return {
                "code": 200,
                "status": "success",
                "message": "All users deleted successfully",
                "data": {}
            }
            
        # Handle single user deletion
        if id is None:
            raise HTTPException(status_code=400, detail="User ID must be provided")
            
        cursor.execute('DELETE FROM users WHERE id = ?', (id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {
            "code": 200,
            "status": "success",
            "message": "User deleted successfully",
            "data": {}
        }
        
    except sqlite3.OperationalError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database operation error: {str(e)}")
    except sqlite3.DatabaseError as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        cursor.close()
        conn.close()