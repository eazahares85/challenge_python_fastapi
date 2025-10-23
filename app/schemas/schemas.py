from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserWithPosts(User):
    posts: List["Post"] = []
    comments: List["Comment"] = []

# Tag Schemas
class TagBase(BaseModel):
    name: str
    description: Optional[str] = None

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class Tag(TagBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Post Schemas
class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    tag_ids: Optional[List[int]] = []

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tag_ids: Optional[List[int]] = None

class Post(PostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class PostWithRelations(Post):
    author: User
    comments: List["Comment"] = []
    tags: List[Tag] = []

# Comment Schemas
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    post_id: int

class CommentUpdate(BaseModel):
    content: Optional[str] = None

class Comment(CommentBase):
    id: int
    author_id: int
    post_id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class CommentWithRelations(Comment):
    author: User
    post: Post

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Actualizar las referencias forward
UserWithPosts.model_rebuild()
PostWithRelations.model_rebuild()
CommentWithRelations.model_rebuild()