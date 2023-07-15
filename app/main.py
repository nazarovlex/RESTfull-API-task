import uvicorn
import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordRequestForm
from storage.storage import Base, engine, pwd_context, SessionLocal, database, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from models.models import User, UserCreate, UserResponse, PostCreate, Post, Like, LikeCreate, Token, PostUpdateResponse

app = FastAPI()


# create tables in DB
async def create_tables() -> None:
    # create tables if not exist
    Base.metadata.create_all(bind=engine)


# create DB connection
@app.on_event("startup")
async def startup() -> None:
    await database.connect()
    await create_tables()


# close DB connection
@app.on_event("shutdown")
async def shutdown() -> None:
    await database.disconnect()


# Function to authenticate user
async def authenticate_user(username: str, password: str) -> User or bool:
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


# Function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Function to get user from database by username
def get_user(username: str) -> User:
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    return user


# Function to create JWT token
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


# Function to decode and verify token
def decode_token(authorization: str = Header(...)) -> User:
    token = authorization.split(" ")[1]  # Extract token from "Authorization: Bearer {token}" header
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = get_user(username)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Route for registering a new user
@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate) -> User:
    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed_password = pwd_context.hash(user.password)
    new_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return new_user


# Route for user authentication and creating JWT token
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


# Route for creating a post
@app.post("/posts")
async def create_post(post: PostCreate, current_user: User = Depends(decode_token)):
    db = SessionLocal()
    new_post = Post(title=post.title, content=post.content, author_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    db.close()
    return new_post


# Route for getting all posts
@app.get("/posts")
async def get_posts(current_user: User = Depends(decode_token)):
    db = SessionLocal()
    posts = db.query(Post).all()
    db.close()
    return posts


# Route for getting a post by its ID
@app.get("/posts/{post_id}")
async def get_post(post_id: int, current_user: User = Depends(decode_token)):
    db = SessionLocal()
    post = db.query(Post).filter(Post.id == post_id).first()
    db.close()
    return post


# Route for updating a post
@app.put("/posts/{post_id}", response_model=PostUpdateResponse)
async def update_post(post_id: int, post: PostCreate, current_user: User = Depends(decode_token)):
    db = SessionLocal()
    existing_post = db.query(Post).filter(Post.id == post_id).first()
    if not existing_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if existing_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not the author of this post")
    existing_post.title = post.title
    existing_post.content = post.content
    changed_post = PostUpdateResponse(id=existing_post.id, title=existing_post.title, content=existing_post.content)
    db.commit()
    db.close()
    return changed_post


# Route for deleting a post
@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, current_user: User = Depends(decode_token)) -> dict:
    db = SessionLocal()
    existing_post = db.query(Post).filter(Post.id == post_id).first()
    if not existing_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if existing_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not the author of this post")
    db.delete(existing_post)
    db.commit()
    db.close()
    return {"message": "Post deleted successfully"}


# Route for liking/disliking a post
@app.post("/posts/{post_id}/like")
async def like_post(post_id: int, like: LikeCreate, current_user: User = Depends(decode_token)) -> dict:
    db = SessionLocal()
    existing_post = db.query(Post).filter(Post.id == post_id).first()
    if not existing_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if existing_post.author_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot like your own post")
    existing_like = db.query(Like).filter(Like.user_id == current_user.id, Like.post_id == post_id).first()
    if existing_like:
        existing_like.is_like = like.is_like
    else:
        new_like = Like(user_id=current_user.id, post_id=post_id, is_like=like.is_like)
        db.add(new_like)
    db.commit()
    db.close()
    message_like = "Like added successfully" if like.is_like else "Like removed successfully"
    return {"message": message_like}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
