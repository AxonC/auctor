import os

from fastapi import status, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import timedelta, datetime

from models import User 
from queries import get_user_by_username, create_user

from pydantic import ValidationError

from config import SECRET_KEY_AUTH

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str) -> User:
    try: 
        user = User(**get_user_by_username(username=username))
    except ValidationError:
        return None
    
    return user if verify_password(password, user.password) else None

def create_access_token(username: str, token_lifespan = 30):
    expire = datetime.utcnow() + timedelta(minutes=token_lifespan)
    claims = {"exp": expire, "uid": username}
    encoded_jwt = jwt.encode(claims, SECRET_KEY_AUTH, ALGORITHM)
    return encoded_jwt

def create_new_user(username: str, plain_password: str, name: str):
    hashed_password = pwd_context.hash(plain_password)
    return create_user(user=User(username=username, password=hashed_password, name=name))

def verify_jwt_token(token: str = Depends(oauth2_scheme)) -> User:
    """ Verify the given JWT token, returning the corresponding user if
        considered to be valid, else will throw an unauthorized HTTP error.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY_AUTH, algorithms=[ALGORITHM])
        username: str = payload.get("uid")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return User(**get_user_by_username(username=username))
