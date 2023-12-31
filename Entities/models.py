from pydantic import BaseModel
import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    id : str
    first_name: str
    last_name: str
    email: str
    sex: str
    disabled : int
    creation_date : datetime.datetime
    closing_date : datetime.datetime | None = None

class UserInDB(User):
    hashed_password: str

class CreateUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    sex: str
    passrowd : str