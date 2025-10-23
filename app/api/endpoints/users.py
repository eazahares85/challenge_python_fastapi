from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_superuser
from app.schemas.schemas import User, UserCreate, UserUpdate, UserWithPosts
from app.crud.crud_user import user_crud
from app.models.models import User as UserModel

router = APIRouter()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser)
):
    """Crear un nuevo usuario (solo superusuarios)"""
    # Verificar si el usuario ya existe
    existing_user = await user_crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    existing_email = await user_crud.get_user_by_email(db, user.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return await user_crud.create_user(db=db, user=user)

@router.get("/", response_model=List[User])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Obtener lista de usuarios (requiere autenticación)"""
    users = await user_crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/with-posts", response_model=List[UserWithPosts])
async def read_users_with_posts(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Obtener usuarios con sus posts (requiere autenticación)"""
    users = await user_crud.get_users_with_posts(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Obtener un usuario específico (requiere autenticación)"""
    db_user = await user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Actualizar un usuario (solo el propio usuario o superusuarios)"""
    # Solo permitir que el usuario actualice su propio perfil o que sea superusuario
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_user = await user_crud.update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser)
):
    """Eliminar un usuario (soft delete, solo superusuarios)"""
    success = await user_crud.soft_delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

@router.post("/{user_id}/restore", response_model=dict)
async def restore_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser)
):
    """Restaurar un usuario eliminado (solo superusuarios)"""
    success = await user_crud.restore_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User restored successfully"}

@router.get("/deleted/list", response_model=List[User])
async def read_deleted_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser)
):
    """Obtener usuarios eliminados (solo superusuarios)"""
    users = await user_crud.get_deleted_users(db, skip=skip, limit=limit)
    return users