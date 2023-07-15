from pydantic import BaseModel
from storage.storage import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


# request models
# Model for user authentication request
class Token(BaseModel):
    access_token: str
    token_type: str


# Model for creating a post
class PostCreate(BaseModel):
    title: str
    content: str


# Model for creating a user
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


# Model for liking/disliking a post
class LikeCreate(BaseModel):
    is_like: bool


# response models
# Model for post update response
class PostUpdateResponse(BaseModel):
    id: int
    title: str
    content: str


# Model for user registration response
class UserResponse(BaseModel):
    id: int
    username: str
    email: str


# postgres models
# Model for the users table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    posts = relationship("Post", back_populates="author")


# Model for the posts table
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    likes = relationship("Like", back_populates="post")


# Model for the likes table
class Like(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    post = relationship("Post", back_populates="likes")
    is_like = Column(Boolean)
