from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.models import Tag
from app.schemas.schemas import TagCreate, TagUpdate

class TagCRUD:
    async def get_tag(self, db: AsyncSession, tag_id: int) -> Optional[Tag]:
        """Obtiene un tag por ID (solo activos)"""
        result = await db.execute(
            select(Tag).filter(Tag.id == tag_id, Tag.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_tag_by_name(self, db: AsyncSession, name: str) -> Optional[Tag]:
        """Obtiene un tag por nombre (solo activos)"""
        result = await db.execute(
            select(Tag).filter(Tag.name == name, Tag.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_tag_with_posts(self, db: AsyncSession, tag_id: int) -> Optional[Tag]:
        """Obtiene un tag con sus posts (solo activos)"""
        result = await db.execute(
            select(Tag)
            .options(selectinload(Tag.posts))
            .filter(Tag.id == tag_id, Tag.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_tags(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Tag]:
        """Obtiene lista de tags activos"""
        result = await db.execute(
            select(Tag)
            .filter(Tag.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_tags_with_posts(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Tag]:
        """Obtiene tags con posts (solo activos)"""
        result = await db.execute(
            select(Tag)
            .options(selectinload(Tag.posts))
            .filter(Tag.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_tag(self, db: AsyncSession, tag: TagCreate) -> Tag:
        """Crea un nuevo tag"""
        db_tag = Tag(
            name=tag.name,
            description=tag.description
        )
        db.add(db_tag)
        await db.commit()
        await db.refresh(db_tag)
        return db_tag

    async def update_tag(self, db: AsyncSession, tag_id: int, tag_update: TagUpdate) -> Optional[Tag]:
        """Actualiza un tag"""
        db_tag = await self.get_tag(db, tag_id)
        if not db_tag:
            return None
        
        update_data = tag_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_tag, field, value)
        
        await db.commit()
        await db.refresh(db_tag)
        return db_tag

    async def soft_delete_tag(self, db: AsyncSession, tag_id: int) -> bool:
        """Elimina un tag (soft delete)"""
        db_tag = await self.get_tag(db, tag_id)
        if not db_tag:
            return False
        
        db_tag.soft_delete()
        await db.commit()
        return True

    async def restore_tag(self, db: AsyncSession, tag_id: int) -> bool:
        """Restaura un tag eliminado"""
        result = await db.execute(
            select(Tag).filter(Tag.id == tag_id, Tag.is_deleted == True)
        )
        db_tag = result.scalar_one_or_none()
        if not db_tag:
            return False
        
        db_tag.restore()
        await db.commit()
        return True

    async def get_deleted_tags(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Tag]:
        """Obtiene tags eliminados (soft delete)"""
        result = await db.execute(
            select(Tag)
            .filter(Tag.is_deleted == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

# Instancia global del CRUD
tag_crud = TagCRUD()
