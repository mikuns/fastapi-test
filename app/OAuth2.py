from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose.exceptions import JWTError
from jose import jwt
from app import schemas, database, models
from sqlalchemy.orm import Session
from app.config import MySetting


oauth2_schema = OAuth2PasswordBearer(tokenUrl='/login')

SECRET_KEY = MySetting.api_key
ALGORITHM = MySetting.database_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = MySetting.database_minutes_expires_token


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credential_exception: HTTPException):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Use "algorithms" instead of "[ALGORITHM]"
        user_id = payload.get("user_id")  # Correct the variable name to "user_id"
        if not user_id:
            raise credential_exception
        token_data = schemas.TokenData(id=user_id)  # Correct the token_data assignment
    except JWTError:
        raise credential_exception
    return token_data


def current_user(token: str = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",  # Fix the detail message
        headers={"WWW-Authenticate": "Bearer"},  # Correct the header
    )
    token = verify_access_token(token, credential_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user


def get_current_user(token: str = Depends(oauth2_schema), db: Session = Depends(database.get_db)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = verify_access_token(token, credential_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()  # Use token.user_id
    return user
