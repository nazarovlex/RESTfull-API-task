from databases import Database
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from passlib.context import CryptContext

DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/RESTfull_API_task"
database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Hashing function for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create OAuth 2.0 scheme object for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secret key for signing JWT token
SECRET_KEY = "some_mega_secret_key_for_extra_security"
# Token expiration time
ACCESS_TOKEN_EXPIRE_MINUTES = 60
