from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_superuser
from app.schemas.schemas import Tag, TagCreate, TagUpdate
from app.crud.crud_tag import tag_crud
from app.models.models import User

router = APIRouter()

@router.post("/", response_model=Tag, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag: TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Crear un nuevo tag (solo superusuarios)"""
    # Verificar si el tag ya existe
    existing_tag = await tag_crud.get_tag_by_name(db, tag.name)
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag name already exists"
        )
    
    return await tag_crud.create_tag(db=db, tag=tag)

@router.get("/", response_model=List[Tag])
async def read_tags(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener lista de tags (requiere autenticación)"""
    tags = await tag_crud.get_tags(db, skip=skip, limit=limit)
    return tags

@router.get("/with-posts", response_model=List[Tag])
async def read_tags_with_posts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener tags con posts (requiere autenticación)"""
    tags = await tag_crud.get_tags_with_posts(db, skip=skip, limit=limit)
    return tags

@router.get("/{tag_id}", response_model=Tag)
async def read_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener un tag específico (requiere autenticación)"""
    db_tag = await tag_crud.get_tag(db, tag_id=tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag

@router.get("/{tag_id}/with-posts", response_model=Tag)
async def read_tag_with_posts(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener un tag con sus posts (requiere autenticación)"""
    db_tag = await tag_crud.get_tag_with_posts(db, tag_id=tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag

@router.put("/{tag_id}", response_model=Tag)
async def update_tag(
    tag_id: int,
    tag_update: TagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Actualizar un tag (solo superusuarios)"""
    db_tag = await tag_crud.update_tag(db, tag_id=tag_id, tag_update=tag_update)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Eliminar un tag (soft delete, solo superusuarios)"""
    success = await tag_crud.soft_delete_tag(db, tag_id=tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")

@router.post("/{tag_id}/restore", response_model=dict)
async def restore_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Restaurar un tag eliminado (solo superusuarios)"""
    success = await tag_crud.restore_tag(db, tag_id=tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"message": "Tag restored successfully"}

@router.get("/deleted/list", response_model=List[Tag])
async def read_deleted_tags(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Obtener tags eliminados (solo superusuarios)"""
    tags = await tag_crud.get_deleted_tags(db, skip=skip, limit=limit)
    return tags
