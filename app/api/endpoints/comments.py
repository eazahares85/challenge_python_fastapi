from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.schemas import Comment, CommentCreate, CommentUpdate, CommentWithRelations
from app.crud.crud_comment import comment_crud
from app.models.models import User

router = APIRouter()

@router.post("/", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear un nuevo comentario (requiere autenticación)"""
    return await comment_crud.create_comment(db=db, comment=comment, author_id=current_user.id)

@router.get("/", response_model=List[Comment])
async def read_comments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener lista de comentarios (requiere autenticación)"""
    comments = await comment_crud.get_comments(db, skip=skip, limit=limit)
    return comments

@router.get("/post/{post_id}", response_model=List[Comment])
async def read_comments_by_post(
    post_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener comentarios de un post específico (requiere autenticación)"""
    comments = await comment_crud.get_comments_by_post(db, post_id, skip=skip, limit=limit)
    return comments

@router.get("/my-comments", response_model=List[Comment])
async def read_my_comments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener comentarios del usuario actual (requiere autenticación)"""
    comments = await comment_crud.get_comments_by_author(db, current_user.id, skip=skip, limit=limit)
    return comments

@router.get("/{comment_id}", response_model=Comment)
async def read_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener un comentario específico (requiere autenticación)"""
    db_comment = await comment_crud.get_comment(db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment

@router.get("/{comment_id}/with-relations", response_model=CommentWithRelations)
async def read_comment_with_relations(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener un comentario con relaciones (requiere autenticación)"""
    db_comment = await comment_crud.get_comment_with_relations(db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment

@router.put("/{comment_id}", response_model=Comment)
async def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar un comentario (solo el autor o superusuarios)"""
    # Verificar que el comentario existe y obtener información del autor
    db_comment = await comment_crud.get_comment(db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Solo permitir que el autor actualice su propio comentario o que sea superusuario
    if db_comment.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated_comment = await comment_crud.update_comment(db, comment_id=comment_id, comment_update=comment_update)
    return updated_comment

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Eliminar un comentario (soft delete, solo el autor o superusuarios)"""
    # Verificar que el comentario existe y obtener información del autor
    db_comment = await comment_crud.get_comment(db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Solo permitir que el autor elimine su propio comentario o que sea superusuario
    if db_comment.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = await comment_crud.soft_delete_comment(db, comment_id=comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")

@router.post("/{comment_id}/restore", response_model=dict)
async def restore_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Restaurar un comentario eliminado (requiere autenticación)"""
    success = await comment_crud.restore_comment(db, comment_id=comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"message": "Comment restored successfully"}
