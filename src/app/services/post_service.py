#DB 객체 의존성 주입 변경
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.app.database import get_db
from src.app.models.post import Post
from src.app.schemas.post import PostCreate, PostUpdate


class PostService:
    #초기화 시 DB 주입
    def __init__(self, db: Session):
        self.db = db

    def create_post(self, post: PostCreate):
        created_post = Post(**post.model_dump())
        self.db.add(created_post)
        self.db.commit()
        self.db.refresh(created_post)
        return created_post

    def get_posts(self):
        query = (
            select(Post)
            .order_by(Post.created_at.desc())
            .limit(10)
        )
        posts = self.db.execute(query).scalars().all()

        return posts

    def get_post(self, post_id: int):
        query = (
            select(Post)
            .where(Post.id == post_id)
        )
        post = self.db.execute(query).scalar_one_or_none()

        return post

    def update_post(self, post_id: int, post: PostUpdate):
        query = (
            select(Post)
            .where(Post.id == post_id)
        )
        existing_post = self.db.execute(query).scalar_one_or_none()

        existing_post.title = post.title
        existing_post.content = post.content

        self.db.commit()
        self.db.refresh(existing_post)

        return existing_post

    def delete_post(self, post_id: int):
        query = (
            select(Post)
            .where(Post.id == post_id)
        )
        existing_post = self.db.execute(query).scalar_one_or_none()

        self.db.delete(existing_post)
        self.db.commit()

        return {"message": "게시글이 성공적으로 삭제되었습니다."}

"""
Depends 클래스 사용 의존성 주입 -> 의존성 주입을 받은 채로 라우터 단으로 넘겨줌
FASTAPI가 의존성 생명주기 자동 관리 + DB가 서비스안으로 들어감. 라우터단에선 한 단계 더 추상화 되어서 들어가 확장성 측면에서 유리하다.
"""
def get_post_service(db: Session = Depends(get_db)):
    return PostService(db)