
import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_NAME = os.environ.get("DATABASE_NAME", "devhabit.db")

# JWT
JWT_SECRET = os.environ.get("JWT_SECRET_KEY")
JWT_ALGORITHM = os.environ.get("ALGORITHM", "HS256")

# Api Version
API_VERSION = os.environ.get("API_VER_STR", "/api/v1")

# Secret key for middleware
SECRET_KEY = os.environ.get("SECRET_KEY")

# Oauth
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", None)