from fastapi import FastAPI
from typing import Optional
from routers import users, auth

app = FastAPI(
    title="FunWorld API",
    description="Learning FastAPI project",
    version="0.1.0"
)
# Include routers for authentication and user management
app.include_router(users.router)
app.include_router(auth.router)

#### `read_root` endpoint to return a welcome message
@app.get("/")
def read_root():
    return {
        "code": 200,
        "status": "success",
        "message": "Start Learning FastAPI",
        "data":  {
            "greeting": "Hello, World!"
        }
    }

#### `hello_user` endpoint to greet the user
@app.get("/hello")
def hello_user(name: Optional[str] = None, age: Optional[int] = None):
    if name is None:
        greeting = "Hello, User!"
    elif name and age is not None:
        greeting = f"Hello, {name}! You are {age} years old."
    else:
        greeting = f"Hello, {name}!"
    return {
        "code": 200,
        "status": "success",
        "message": "User Greeting",
        "data": {
            "greeting": greeting,
        }
    }
