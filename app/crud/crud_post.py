from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.models import Post, Tag
from app.schemas.schemas import PostCreate, PostUpdate

class PostCRUD:
    async def get_post(self, db: AsyncSession, post_id: int) -> Optional[Post]:
        """Obtiene un post por ID (solo activos)"""
        result = await db.execute(
            select(Post).filter(Post.id == post_id, Post.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_post_with_relations(self, db: AsyncSession, post_id: int) -> Optional[Post]:
        """Obtiene un post con todas sus relaciones (solo activos)"""
        result = await db.execute(
            select(Post)
            .options(
                selectinload(Post.author),
                selectinload(Post.comments),
                selectinload(Post.tags)
            )
            .filter(Post.id == post_id, Post.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_posts(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Post]:
        """Obtiene lista de posts activos"""
        result = await db.execute(
            select(Post)
            .filter(Post.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_posts_with_relations(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Post]:
        """Obtiene posts con relaciones (solo activos)"""
        result = await db.execute(
            select(Post)
            .options(
                selectinload(Post.author),
                selectinload(Post.comments),
                selectinload(Post.tags)
            )
            .filter(Post.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_posts_by_author(self, db: AsyncSession, author_id: int, skip: int = 0, limit: int = 100) -> List[Post]:
        """Obtiene posts de un autor específico (solo activos)"""
        result = await db.execute(
            select(Post)
            .filter(Post.author_id == author_id, Post.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_post(self, db: AsyncSession, post: PostCreate, author_id: int) -> Post:
        """Crea un nuevo post"""
        db_post = Post(
            title=post.title,
            content=post.content,
            author_id=author_id
        )
        
        # Agregar tags si se proporcionan
        if post.tag_ids:
            result = await db.execute(
                select(Tag).filter(Tag.id.in_(post.tag_ids), Tag.is_deleted == False)
            )
            tags = result.scalars().all()
            db_post.tags = tags
        
        db.add(db_post)
        await db.commit()
        await db.refresh(db_post)
        return db_post

    async def update_post(self, db: AsyncSession, post_id: int, post_update: PostUpdate) -> Optional[Post]:
        """Actualiza un post"""
        db_post = await self.get_post(db, post_id)
        if not db_post:
            return None
        
        update_data = post_update.model_dump(exclude_unset=True)
        
        # Manejar tags por separado
        tag_ids = update_data.pop("tag_ids", None)
        if tag_ids is not None:
            result = await db.execute(
                select(Tag).filter(Tag.id.in_(tag_ids), Tag.is_deleted == False)
            )
            tags = result.scalars().all()
            db_post.tags = tags
        
        # Actualizar otros campos
        for field, value in update_data.items():
            setattr(db_post, field, value)
        
        await db.commit()
        await db.refresh(db_post)
        return db_post

    async def soft_delete_post(self, db: AsyncSession, post_id: int) -> bool:
        """Elimina un post (soft delete)"""
        db_post = await self.get_post(db, post_id)
        if not db_post:
            return False
        
        db_post.soft_delete()
        await db.commit()
        return True

    async def restore_post(self, db: AsyncSession, post_id: int) -> bool:
        """Restaura un post eliminado"""
        result = await db.execute(
            select(Post).filter(Post.id == post_id, Post.is_deleted == True)
        )
        db_post = result.scalar_one_or_none()
        if not db_post:
            return False
        
        db_post.restore()
        await db.commit()
        return True

    async def get_deleted_posts(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Post]:
        """Obtiene posts eliminados (soft delete)"""
        result = await db.execute(
            select(Post)
            .filter(Post.is_deleted == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

# Instancia global del CRUD
post_crud = PostCRUD()
