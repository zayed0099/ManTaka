import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_NAME = os.environ.get("DATABASE_NAME", "devhabit.db")

# JWT
JWT_SECRET = os.environ.get("SECRET_KEY")
JWT_ALGORITHM = os.environ.get("ALGORITHM", "HS256")

# Api Version
API_VERSION = os.environ.get("API_VER_STR", "/api/v1")