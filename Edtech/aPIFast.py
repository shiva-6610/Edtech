from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import pandas as pd
import os

app = FastAPI()



client = MongoClient("mongodb://localhost:27017/")
db = client["USER"]
users_collection = db["users"]

class RegisterModel(BaseModel):
    username: str
    password: str
    preferences: list[str] = []

class LoginModel(BaseModel):
    username: str
    password: str

@app.get("/")
def home():
    return {"message": "API is running"}

@app.post("/Register")
def register(user: RegisterModel):
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    user_data = {
        "username": user.username,
        "password": user.password,
        "preferences": user.preferences
    }
    inserted = users_collection.insert_one(user_data)
    return {"message": "User registered successfully", "user_id": str(inserted.inserted_id)}

@app.post("/Login")
def login(user: LoginModel):
    found_user = users_collection.find_one({"username": user.username})
    if not found_user or found_user["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Login successful", "username": user.username}

@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    contents = await file.read()
    df = pd.read_csv(pd.io.common.BytesIO(contents))

    # Optionally: save to local folder
    upload_folder = "uploaded_csvs"
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)
    df.to_csv(file_path, index=False)

    return {"message": f"CSV uploaded and saved as {file.filename}", "rows": len(df)}



#python -m uvicorn filename:app --reload
#streamlit run frontend.py
#{
  #"username": "shivani",
  #"password": "12345",
  #"preferences": ["AIML"]
#}
