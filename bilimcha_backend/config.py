import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///instance/bilimcha.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "supersecret123")
