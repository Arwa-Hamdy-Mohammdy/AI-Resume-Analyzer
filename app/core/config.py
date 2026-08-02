import os
from dotenv import load_dotenv

load_dotenv()

# JWT Configuration
SECRET_KEY = "your_super_secret_key_change_this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Hugging Face Configuration
HF_TOKEN = os.getenv("HF_TOKEN")