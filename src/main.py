from http.client import responses
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import engine, Base, get_db
from app.models.post import Post
from app.schemas.post import PostResponse, PostCreate, PostUpdate
from app.services.post_service import get_post_service, PostService


app = FastAPI(
    title="FastAPI_Redis_JWT",
    description="test",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": 'ok'}

@app.get("/ping")
async def ping_db():
    try:
        # 연결 되었을 경우 
        with engine.connect() as conn:
            return {"status": "connected"}
        
    # 연결되지 않았을 경우
    except Exception:
        return {"status": "error", "message": str(Exception)}
    
@app.on_event("startup")
def init_db():
    Base.metadata.create_all(bind=engine)

# 게시글 생성
@app.post("/posts",
          response_model=PostResponse,
          summary ="새 게시글 생성",
          description="새 게시글을 생성합니다.")
def create_post(post: PostCreate, post_service: PostService = Depends(get_post_service)):
    created_post = post_service.create_post(post)
    return created_post

@app.get("/posts", response_model=List[PostResponse],
         summary="게시글 목록 조회",
         description="게시글 목록을 조회합니다.",
         responses={
             404: {
                "description": "게시글을 찾을 수 없습니다.",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Post not found"}
                     }
                 }
                }
         })
def get_posts(post_service: PostService = Depends(get_post_service)):
    posts = post_service.get_posts()

    if posts is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return posts

#게시글 하나하나 조회
@app.get("/posts/{post_id}", response_model=PostResponse,
         summary= "게시글 상세 조회",
         description= "게시글 목록 1개 보기",
         responses={
             404: {
                "description": "게시글을 찾을 수 없습니다.",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Post not found"}
                     }
                 }
                }
})
def get_post(post_id: int, post_service: PostService = Depends(get_post_service)):
    post = post_service.get_post(post_id)
    return post

# 게시글 수정
@app.put("/posts/{post_id}", response_model=PostResponse,
          summary="게시글 수정",
          description="게시글 수정합니다.",
          responses={
              404: {
                "description": "게시글을 찾을 수 없습니다.",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Post not found"}
                     }
                 }
                }
          })
def update_post(post_id: int, post: PostUpdate, post_service: PostService = Depends(get_post_service)):
    update_post = post_service.update_post(post_id, post)
    return update_post


#게시글 삭제
@app.delete("/posts/{post_id}",
          summary="게시글 삭제",
          description="게시글 삭제합니다.",
          responses={
              200: {
                "description": "게시글이 성공적으로 삭제되었습니다.",
                 "content": {
                     "application/json": {
                         "example": {"message": "게시글이 성공적으로 삭제되었습니다."}
                     }
                 }
                },

              404: {
                "description": "게시글을 찾을 수 없습니다.",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Post not found"}
                     }
                 }
                }
          })
def delete_post(post_id: int, post_service: PostService = Depends(get_post_service)):
    delete_post = post_service.delete_post(post_id)
    return delete_post
