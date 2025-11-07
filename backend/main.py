from pydantic import BaseModel, EmailStr
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from database import db
import bcrypt

load_dotenv()


app = FastAPI(title="Test API", version="1.0.0")

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

@app.get("/")
def home():
    return "Welcome to my API"

class SignupRequest(BaseModel):
    full_name: str = Field(..., example="Ade")
    email:  EmailStr = Field(..., example="ade@gmail.com")
    password: str = Field(..., example="ade123")
    user_id: int = Field(..., example=1)


@app.post('/api/signup')
def sign_up(input: SignupRequest):
    try:
        duplicate_query = text("""
            SELECT * FROM user_info
            WHERE email = :email
        """)

        existing = db.execute(duplicate_query, {"email": input.email})
        if existing:
            print("Email already exists!")

        query = text("""
            INSERT INTO userInfo (name, email, password)
            VALUES (:name, :email, :password)
        """)

        salt = bcrypt.gensalt()
        hashedPassword = bcrypt.hashpw(input.password.encode('utf-8'), salt)
        
        db.execute(query, {"full_name": input.full_name, "email": input.email, "password": hashedPassword, "user_id" : input.user_id})
        db.commit()

        return {"message": "User created successfully", 
               "user_id": {input.user_id,}}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    




class LoginRequest(BaseModel):
    email:  str = Field(..., example="ade@gmail.com")
    password: str = Field(..., example="ade123")

@app.post("/login")
def login(input: LoginRequest):
    try:
        query =text("""
            SELECT * FROM userInfo
            WHERE email = :email
        """)

        result = db.execute(query, {"email": input.email}).fetchone()

        if not result:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        verified_password = bcrypt.checkpw(input.password.encode('utf-8'), result.password.encode('utf-8'))

        if not verified_password:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        return {

            
            "message": "Login Successful!",
             "user": {
                    # "user_id": input.user_id,
                    # "full_name": input.full_name,
                    "email": input.email}}

            
            
        

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


class UserResponse(BaseModel):
    id: int = Field(..., example=1)
    full_name: str = Field(..., example="Ade")
    email:  str = Field(..., example="ade@gmail.com")
    

@app.post("/userResponse")
def user_response(input: UserResponse):
    try:
        query =text("""
            SELECT * FROM userInfo
            WHERE email = :email
        """)

        result = db.execute(query, {"email": input.email}).fetchone()

        if not result:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return {
            "message": "Login Successful!"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/states")
def states():
    try:
        get_states = text("""
            SELECT * from states;
        """)
        result = db.execute(get_states).mappings().all()
        if not result:
            return "No states yet. Try again later!"
        return {"states": result}
    except Exception as e:
        return {"details": str(e)}























