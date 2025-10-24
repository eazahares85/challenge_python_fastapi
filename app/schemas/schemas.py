from pydantic import BaseModel, EmailStr, ConfigDict, Field, validator
from typing import Optional, List
from datetime import datetime
import re

# User Schemas
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Email válido del usuario")
    username: str = Field(..., min_length=3, max_length=50, description="Username entre 3 y 50 caracteres")
    name: Optional[str] = Field(None, max_length=100, description="Nombre completo del usuario")
    is_active: bool = Field(True, description="Estado activo del usuario")
    is_superuser: bool = Field(False, description="Privilegios de superusuario")

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username solo puede contener letras, números, guiones y guiones bajos')
        return v.lower()

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100, description="Contraseña entre 8 y 100 caracteres")

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="Email válido del usuario")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username entre 3 y 50 caracteres")
    name: Optional[str] = Field(None, max_length=100, description="Nombre completo del usuario")
    password: Optional[str] = Field(None, min_length=8, max_length=100, description="Contraseña entre 8 y 100 caracteres")
    is_active: Optional[bool] = Field(None, description="Estado activo del usuario")

    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9_-]+$', v):
                raise ValueError('Username solo puede contener letras, números, guiones y guiones bajos')
            return v.lower()
        return v

    @validator('password')
    def validate_password(cls, v):
        if v is not None:
            if len(v) < 8:
                raise ValueError('La contraseña debe tener al menos 8 caracteres')
            if not re.search(r'[A-Z]', v):
                raise ValueError('La contraseña debe contener al menos una letra mayúscula')
            if not re.search(r'[a-z]', v):
                raise ValueError('La contraseña debe contener al menos una letra minúscula')
            if not re.search(r'\d', v):
                raise ValueError('La contraseña debe contener al menos un número')
        return v

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
    items: List["Item"] = []

# Tag Schemas
class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Nombre del tag entre 1 y 50 caracteres")
    description: Optional[str] = Field(None, max_length=200, description="Descripción del tag hasta 200 caracteres")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        # Convertir a lowercase y reemplazar espacios con guiones
        return re.sub(r'\s+', '-', v.strip().lower())

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Nombre del tag entre 1 y 50 caracteres")
    description: Optional[str] = Field(None, max_length=200, description="Descripción del tag hasta 200 caracteres")

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('El nombre no puede estar vacío')
            # Convertir a lowercase y reemplazar espacios con guiones
            return re.sub(r'\s+', '-', v.strip().lower())
        return v

class Tag(TagBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Post Schemas
class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Título del post entre 1 y 200 caracteres")
    content: str = Field(..., min_length=10, max_length=5000, description="Contenido del post entre 10 y 5000 caracteres")

    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip()

    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('El contenido no puede estar vacío')
        return v.strip()

class PostCreate(PostBase):
    tag_ids: Optional[List[int]] = Field(default=[], description="IDs de tags asociados al post")

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Título del post entre 1 y 200 caracteres")
    content: Optional[str] = Field(None, min_length=10, max_length=5000, description="Contenido del post entre 10 y 5000 caracteres")
    tag_ids: Optional[List[int]] = Field(None, description="IDs de tags asociados al post")

    @validator('title')
    def validate_title(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('El título no puede estar vacío')
            return v.strip()
        return v

    @validator('content')
    def validate_content(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('El contenido no puede estar vacío')
            return v.strip()
        return v

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
    content: str = Field(..., min_length=1, max_length=1000, description="Contenido del comentario entre 1 y 1000 caracteres")

    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('El contenido no puede estar vacío')
        return v.strip()

class CommentCreate(CommentBase):
    post_id: int = Field(..., description="ID del post al que pertenece el comentario")

class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=1000, description="Contenido del comentario entre 1 y 1000 caracteres")

    @validator('content')
    def validate_content(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('El contenido no puede estar vacío')
            return v.strip()
        return v

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

# Item Schemas
class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Título del item entre 1 y 100 caracteres")
    description: Optional[str] = Field(None, max_length=500, description="Descripción del item hasta 500 caracteres")
    price: float = Field(..., gt=0, description="Precio del item mayor a 0")

    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip()

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="Título del item entre 1 y 100 caracteres")
    description: Optional[str] = Field(None, max_length=500, description="Descripción del item hasta 500 caracteres")
    price: Optional[float] = Field(None, gt=0, description="Precio del item mayor a 0")

    @validator('title')
    def validate_title(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('El título no puede estar vacío')
            return v.strip()
        return v

class Item(ItemBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class ItemWithRelations(Item):
    owner: User

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
ItemWithRelations.model_rebuild()