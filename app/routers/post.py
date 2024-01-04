from fastapi import Response, status, HTTPException, Depends, APIRouter, Query, Request
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from app import models, schemas, OAuth2
from app.database import get_db
from sqlalchemy import func
from fastapi.responses import HTMLResponse

templates = Jinja2Templates(directory="templates")
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")





@router.get("/post", response_model=List[schemas.Post], status_code=status.HTTP_200_OK)
def search_posts(
        request: Request,
        query: str = Query(None),
        db: Session = Depends(get_db)
):
    if query:
        result = (
            db.query(models.Post, models.User.email, func.count(models.Vote.post_id).label("votes"))
            .outerjoin(models.Vote, models.Vote.post_id == models.Post.id)
            .join(models.User, models.User.id == models.Post.user_id)
            .filter(
                models.Post.title.ilike(f"%{query}%") | models.Post.content.ilike(f"%{query}%")
            )
            .group_by(models.Post.id, models.User.email)
            .all()
        )
    else:
        result = (
            db.query(models.Post, models.User.email, func.count(models.Vote.post_id).label("votes"))
            .outerjoin(models.Vote, models.Vote.post_id == models.Post.id)
            .join(models.User, models.User.id == models.Post.user_id)
            .group_by(models.Post.id, models.User.email)
            .all()
        )

    # Prepare the data to pass to the template
    posts_with_votes = [{"post": post, "user_email": email, "votes": votes} for post, email, votes in result]

    # Render the HTML template and pass the data
    return templates.TemplateResponse("post.html", {"request": request, "posts_with_votes": posts_with_votes})

#
#
# @router.get("/all", response_class=HTMLResponse)
# async def posts(request: Request, db: Session = Depends(get_db)):
#
#     result = (
#         db.query(models.Post, models.User.email, func.count(models.Vote.post_id).label("votes"))
#         .outerjoin(models.Vote, models.Vote.post_id == models.Post.id)
#         .join(models.User, models.User.id == models.Post.user_id)
#         .group_by(models.Post.id, models.User.email)
#         .all()
#     )
#
#     # Prepare the data to pass to the template
#     posts_with_votes = [{"post": post, "user_email": email, "votes": votes} for post, email, votes in result]
#
#     # Render the HTML template and pass the data
#     return templates.TemplateResponse("post.html", {"request": request, "posts_with_votes": posts_with_votes})
#
#
# @router.get("/lall", response_class=HTMLResponse)
# async def posts(request: Request, db: Session = Depends(get_db)):
#     result = (
#         db.query(models.User, models.Post, func.count(models.Vote.post_id).label("votes"))
#         .outerjoin(models.Vote, models.Vote.post_id == models.Post.id)
#         .group_by(models.Post.id)
#         .all()
#     )
#
#     # Prepare the data to pass to the template
#     posts_with_votes = [{"post": post, "votes": votes} for post, votes in result]
#
#     # Render the HTML template and pass the data
#     return templates.TemplateResponse("post.html", {"request": request, "posts_with_votes": posts_with_votes})



@router.get("/post/{id}", response_model=schemas.Post)
async def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(OAuth2.current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    return post

@router.delete("/post/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(OAuth2.current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    print(current_user.id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to make such action")
    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/post/{id}", response_model=schemas.Post)
async def update_post(
    id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(OAuth2.current_user)
):
    post_in_db = db.query(models.Post).filter(models.Post.id == id).first()
    if not post_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    if post_in_db.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to make such action")

    # Update post_in_db using the data from post
    post_data = post.dict(exclude_unset=True)  # Extracts data from post, excluding unset values
    for field, value in post_data.items():
        setattr(post_in_db, field, value)

    db.commit()
    db.refresh(post_in_db)
    return post_in_db



@router.get("/createpost", status_code=status.HTTP_200_OK)
async def create_post_page(request: Request):
    return templates.TemplateResponse("create_post.html", {"request": request})


@router.post('/create_post_endpoint', status_code=status.HTTP_201_CREATED)
async def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    curr_user: models.User = Depends(OAuth2.get_current_user)
):
    if curr_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed or user details not found")

    try:
        post_model = models.Post(user_id=curr_user.id, **post.dict())
        db.add(post_model)
        db.commit()
        db.refresh(post_model)
        return post_model
    except Exception as e:
        print("error",e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create post")

@router.get('/user_post', status_code=status.HTTP_200_OK)
async def get_user_posts(request: Request, db: Session = Depends(get_db),
             curr_user: models.User = Depends(OAuth2.get_current_user)):
    user_posts = db.query(models.Post).filter(models.Post.user_id == curr_user.id).all()
    if not user_posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='You don\'t have any posts yet')
    return templates.TemplateResponse("user_post.html", {"request": request, "user_posts": user_posts})


