from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.core.security import authenticate_user, create_access_token
from app.schemas.schemas import Token
from app.crud.crud_user import user_crud

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Endpoint para obtener token de acceso OAuth2"""
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=dict)
async def register_user(
    username: str,
    email: str,
    password: str,
    name: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Endpoint para registrar un nuevo usuario"""
    # Verificar si el usuario ya existe
    existing_user = await user_crud.get_user_by_username(db, username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    existing_email = await user_crud.get_user_by_email(db, email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Crear nuevo usuario
    from app.schemas.schemas import UserCreate
    user_data = UserCreate(
        username=username,
        email=email,
        password=password,
        name=name
    )
    
    user = await user_crud.create_user(db, user_data)
    return {"message": "User created successfully", "user_id": user.id}
