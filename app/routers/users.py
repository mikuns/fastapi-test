from fastapi import status, HTTPException, Depends, APIRouter, Query, Request
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, utils, OAuth2
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")



@router.get("/users")
def all_users(
        limit: int = Query(10, le=100),
        skip: int = Query(0, ge=0),
        search: Optional[str] = Query(None, description="Search for user containing this text"),
        db: Session = Depends(get_db)
):
    query = db.query(models.User)

    if search:
        # Searching across related tables using JOINs
        query = query.join(models.BasicUserInfo).filter(
            (models.BasicUserInfo.first_name.ilike(f"%{search}%")) |
            (models.BasicUserInfo.last_name.ilike(f"%{search}%"))
        ).join(models.User).filter(
            models.User.user_name.ilike(f"%{search}%")
        ).join(models.LocationInfo).filter(
            models.LocationInfo.phone_number.ilike(f"%{search}%")
        ).filter(
            (models.User.email.ilike(f"%{search}%"))

        )

    query = query.offset(skip).limit(limit)

    result = query.all()

    return result

@router.get('/login', status_code=status.HTTP_200_OK)
async def get_login(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post('/login_endpoint', response_model=schemas.Token)
async def login(user_credential: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(get_db)):
    try:
        user = db.query(models.User).filter(models.User.email == user_credential.username).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if not utils.verify(user_credential.password, user.password):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
        token_type = "bearer"
        access_token = OAuth2.create_access_token(data={'user_id': user.id})
        print(access_token)
        return JSONResponse(content={"access_token": access_token}, status_code=200)
        #access_token = OAuth2.create_access_token(data={'user_id': user.id})
        #return {"access_token": access_token, "token_type": token_type}
    except Exception as e:
        print(f"Error {e}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")




@router.get('/basic_info', status_code=status.HTTP_200_OK)
async def create_user(request: Request):
    return templates.TemplateResponse("basic_info.html", {"request": request})


@router.post("/submit_basic_info", status_code=status.HTTP_201_CREATED)
async def create_user_basic_info(user: schemas.BasicInfo, db: Session = Depends(get_db)):
    try:
        user_inf = models.BasicUserInfo(**user.dict())
        db.add(user_inf)
        db.commit()
        db.refresh(user_inf)
        #return RedirectResponse(url='/location_info')
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="an error occurred during creation")



@router.get('/signup', status_code=status.HTTP_200_OK)
async def create_user(request: Request):
    return templates.TemplateResponse("user_form.html", {"request": request})



@router.post('/signup_info', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Hash the password
    hash_pwd = pwd_context.hash(user.password)
    user_dict = user.dict()
    user_dict["password"] = hash_pwd

    new_user = models.User(**user_dict)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user



@router.get('/location_info')
async def create_user(request: Request):
    return templates.TemplateResponse("location_form.html", {"request": request})

@router.post("/submit_location_info", status_code=status.HTTP_201_CREATED)
async def create_user_location(location: schemas.LocationInfo, db: Session = Depends(get_db)):
    try:
        
        loc_info = models.LocationInfo(**location.dict())
        db.add(loc_info)
        db.commit()
        db.refresh(loc_info)
    except Exception as e:
        db.rollback()
        print(f"error occurred {e}")

        raise HTTPException(status_code=500, detail="An error occurred during user creation")


@router.get("/profile", status_code=status.HTTP_200_OK)
async def get_support(request: Request, db: Session = Depends(get_db), current_user: models.User = Depends(OAuth2.current_user)):
    user_profile = (
        db.query(models.User)
        .filter(models.User.id == current_user.id)
        .outerjoin(models.BasicUserInfo)
        .join(models.LocationInfo)
        .first()
    )

    if user_profile:
        return templates.TemplateResponse("profile.html.html", {"request": request, "user_profile": user_profile})
    else:
        return {"message": "User profile not found"}

