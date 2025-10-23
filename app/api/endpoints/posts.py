from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.schemas import Post, PostCreate, PostUpdate, PostWithRelations
from app.crud.crud_post import post_crud
from app.models.models import User

router = APIRouter()

@router.post("/", response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear un nuevo post (requiere autenticación)"""
    return await post_crud.create_post(db=db, post=post, author_id=current_user.id)

@router.get("/", response_model=List[Post])
async def read_posts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener lista de posts (requiere autenticación)"""
    posts = await post_crud.get_posts(db, skip=skip, limit=limit)
    return posts

@router.get("/with-relations", response_model=List[PostWithRelations])
async def read_posts_with_relations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener posts con relaciones (requiere autenticación)"""
    posts = await post_crud.get_posts_with_relations(db, skip=skip, limit=limit)
    return posts

@router.get("/my-posts", response_model=List[Post])
async def read_my_posts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener posts del usuario actual (requiere autenticación)"""
    posts = await post_crud.get_posts_by_author(db, current_user.id, skip=skip, limit=limit)
    return posts

@router.get("/author/{author_id}", response_model=List[Post])
async def read_posts_by_author(
    author_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener posts de un autor específico (requiere autenticación)"""
    posts = await post_crud.get_posts_by_author(db, author_id, skip=skip, limit=limit)
    return posts

@router.get("/{post_id}", response_model=Post)
async def read_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener un post específico (requiere autenticación)"""
    db_post = await post_crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

@router.get("/{post_id}/with-relations", response_model=PostWithRelations)
async def read_post_with_relations(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener un post con todas sus relaciones (requiere autenticación)"""
    db_post = await post_crud.get_post_with_relations(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

@router.put("/{post_id}", response_model=Post)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar un post (solo el autor o superusuarios)"""
    # Verificar que el post existe y obtener información del autor
    db_post = await post_crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Solo permitir que el autor actualice su propio post o que sea superusuario
    if db_post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated_post = await post_crud.update_post(db, post_id=post_id, post_update=post_update)
    return updated_post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Eliminar un post (soft delete, solo el autor o superusuarios)"""
    # Verificar que el post existe y obtener información del autor
    db_post = await post_crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Solo permitir que el autor elimine su propio post o que sea superusuario
    if db_post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = await post_crud.soft_delete_post(db, post_id=post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")

@router.post("/{post_id}/restore", response_model=dict)
async def restore_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Restaurar un post eliminado (requiere autenticación)"""
    success = await post_crud.restore_post(db, post_id=post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post restored successfully"}
