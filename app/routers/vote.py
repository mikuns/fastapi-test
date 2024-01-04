from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from app import models, schemas, OAuth2
from app.database import get_db

router = APIRouter()

@router.post("/votes", status_code=status.HTTP_201_CREATED)
def up_votes(vote: schemas.Vote, db: Session = Depends(get_db), current_user: int = Depends(OAuth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.user_id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {vote.post_id} not found")
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id,
                                              models.Vote.user_id == current_user.id)
    voted = vote_query.first()
    if vote.dir == 1:
        if voted:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User {current_user.id} has already voted on post {vote.post_id}")
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        print(new_vote)
        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)
        return {"vote":"successfully"}
    else:
        if not voted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vote does not exist")
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Successfully un_voted"}


@router.post("/comment_post", status_code=status.HTTP_201_CREATED)
async def create_comment(comment: schemas.Comment, db: Session = Depends(get_db), current_user: int = Depends(
    OAuth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == comment.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {comment.post_id} not found")

    new_comment = models.Comment(**comment.dict())

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.post("/comment", status_code=status.HTTP_201_CREATED, response_model=schemas.Comment)
async def create_comment(
    comment: schemas.CommentBase,
    db: Session = Depends(get_db),
    current_user:int = Depends(OAuth2.get_current_user)
):
    post = db.query(models.Post).filter(models.Post.id == comment.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {comment.post_id} not found")

    new_comment = models.Comment(**comment.dict(), user_id=current_user.id)

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.post("/comments", status_code=status.HTTP_201_CREATED, response_model=schemas.Comment)
async def create_comment(
    comment: schemas.CommentBase,  # Use CommentBase here
    db: Session = Depends(get_db),
    current_user: models.User = Depends(OAuth2.get_current_user)
):
    post = db.query(models.Post).filter(models.Post.id == comment.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {comment.post_id} not found")

    new_comment = models.Comment(**comment.dict(), user_id=current_user.id)

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

