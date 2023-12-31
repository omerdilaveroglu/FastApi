from datetime import datetime, timedelta
from typing import Annotated
from Entities.models import TokenData
from Entities.models import User
from Entities.models import UserInDB
from fastapi import Depends, HTTPException, status,Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
import sqlite3
import pandas as pd
import uuid

sample_api_key = "your-api-key"

def db_connect():
    return sqlite3.connect("db.sqlite3")

conn = db_connect()
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS USERS (
          id TEXT PRIMARY KEY,
          first_name TEXT KEY NOT NULL, 
          last_name TEXT NOT NULL,
          email TEXT NOT NULL UNIQUE,
          sex TEXT NOT NULL,
          hashed_password TEXT NOT NULL,
          disabled INTEGER NOT NULL,
          creation_date DATETIME NOT NULL,
          closing_date DATETIME
)""")
conn.commit()
conn.close()

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#user db de mecut mu kontrolu yapılır. Mevcutsa bilgileri dönülür
def get_user(email: str):
    db_connection = db_connect()
    df = pd.read_sql(f"SELECT * FROM USERS WHERE EMAIL = '{email}'",db_connection)
    user_dict= df.to_dict(orient='records')[0]
    db_connection.close()
    return UserInDB(**user_dict)

def get_all_users():
    db_connection = db_connect()
    df = pd.read_sql("select * from users",db_connection)
    db_connection.close()
    return df.to_dict(orient='records')

def user_register(first_name:str,last_name:str,email:str,sex:str,password):
    hashed_password = get_password_hash(password)
    try:
        db_connection = db_connect()
        query = f"INSERT INTO USERS VALUES ('{str(uuid.uuid4())}','{first_name}','{last_name}','{email}','{sex.title()}','{hashed_password}','0','{str(datetime.now())}',null)"
        db_connection.cursor().execute(query)
        db_connection.commit()
        db_connection.close()
        return "user_added"
    except sqlite3.IntegrityError as e:
        return str(e)
    except Exception as e:
        return "user registration failed"
     
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Güvenlik kontrolü için middleware
async def api_key_middleware(x_api_key: str = Header(...)):
    if x_api_key != sample_api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")