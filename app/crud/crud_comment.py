from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.models import Comment
from app.schemas.schemas import CommentCreate, CommentUpdate

class CommentCRUD:
    async def get_comment(self, db: AsyncSession, comment_id: int) -> Optional[Comment]:
        """Obtiene un comentario por ID (solo activos)"""
        result = await db.execute(
            select(Comment).filter(Comment.id == comment_id, Comment.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_comment_with_relations(self, db: AsyncSession, comment_id: int) -> Optional[Comment]:
        """Obtiene un comentario con relaciones (solo activos)"""
        result = await db.execute(
            select(Comment)
            .options(
                selectinload(Comment.author),
                selectinload(Comment.post)
            )
            .filter(Comment.id == comment_id, Comment.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_comments(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Obtiene lista de comentarios activos"""
        result = await db.execute(
            select(Comment)
            .filter(Comment.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_comments_by_post(self, db: AsyncSession, post_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Obtiene comentarios de un post específico (solo activos)"""
        result = await db.execute(
            select(Comment)
            .filter(Comment.post_id == post_id, Comment.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_comments_by_author(self, db: AsyncSession, author_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Obtiene comentarios de un autor específico (solo activos)"""
        result = await db.execute(
            select(Comment)
            .filter(Comment.author_id == author_id, Comment.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_comment(self, db: AsyncSession, comment: CommentCreate, author_id: int) -> Comment:
        """Crea un nuevo comentario"""
        db_comment = Comment(
            content=comment.content,
            post_id=comment.post_id,
            author_id=author_id
        )
        db.add(db_comment)
        await db.commit()
        await db.refresh(db_comment)
        return db_comment

    async def update_comment(self, db: AsyncSession, comment_id: int, comment_update: CommentUpdate) -> Optional[Comment]:
        """Actualiza un comentario"""
        db_comment = await self.get_comment(db, comment_id)
        if not db_comment:
            return None
        
        update_data = comment_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_comment, field, value)
        
        await db.commit()
        await db.refresh(db_comment)
        return db_comment

    async def soft_delete_comment(self, db: AsyncSession, comment_id: int) -> bool:
        """Elimina un comentario (soft delete)"""
        db_comment = await self.get_comment(db, comment_id)
        if not db_comment:
            return False
        
        db_comment.soft_delete()
        await db.commit()
        return True

    async def restore_comment(self, db: AsyncSession, comment_id: int) -> bool:
        """Restaura un comentario eliminado"""
        result = await db.execute(
            select(Comment).filter(Comment.id == comment_id, Comment.is_deleted == True)
        )
        db_comment = result.scalar_one_or_none()
        if not db_comment:
            return False
        
        db_comment.restore()
        await db.commit()
        return True

    async def get_deleted_comments(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Obtiene comentarios eliminados (soft delete)"""
        result = await db.execute(
            select(Comment)
            .filter(Comment.is_deleted == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

# Instancia global del CRUD
comment_crud = CommentCRUD()
