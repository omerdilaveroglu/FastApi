from datetime import timedelta
from typing import Annotated
from Entities.models import Token
from Entities.models import User
from Entities.models import CreateUser
from fastapi import Depends, FastAPI, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from functions import get_current_active_user
from functions import authenticate_user
from functions import create_access_token
from functions import get_all_users
from functions import user_register
from typing import List
from functions import ACCESS_TOKEN_EXPIRE_MINUTES
import uvicorn
from functions import api_key_middleware

app = FastAPI(title="FastApi")

@app.post("/token", response_model=Token,tags=["Login"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User,tags=["UserOperations"])
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user

@app.get("/users/me/items/",tags=["UserOperations"])
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.email}]

# GET metodu ile datatable dönen endpoint
@app.get("/users/me/GetAllUsers",response_model=List[User],tags=["UserOperations"])
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return get_all_users()

@app.post("/users/create_user",dependencies=[Depends(api_key_middleware)],tags=['Login'])
def user_added(createUser:CreateUser):
    return user_register(createUser.first_name,createUser.last_name,createUser.email,createUser.sex,createUser.passrowd)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)