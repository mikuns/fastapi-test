from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from pydantic.types import conint

# Example usage:
class PostBase(BaseModel):
    title: Optional[str] = None
    content: str



class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Post(PostBase):
    id: int
    created_at: datetime
    user_id: int
    user_profile: UserOut
    class Config:
        from_attributes = True

class PostOut(PostBase):
    Post: Post
    votes: int


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None

class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    created_at: str
    user_id: int
    votes: int

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str
    post_id: int

class Comment(CommentBase):
    id: int
    created_at: datetime
    user_id: int
    post_id: int

    class Config:
        from_attributes = True

class BasicInfo(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    age: int
    gender: str


class LocationInfo(BaseModel):
    phone_number: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    hobbies: Optional[str] = None


class UserProfileIn(BaseModel):
    basic_info: BasicInfo
    user_info: UserOut
    location_info: LocationInfo
    created_at: datetime

    class Config:
        from_attributes = True
class UserProfile(BaseModel):
    id: int
    profile_image: Optional[bytes] = None
    user_email: EmailStr
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    hobbies: Optional[str] = None
    country: Optional[str] = None
    age: int
    phone_number: Optional[str] = None
    posts: Optional[int] = None
