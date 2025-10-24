from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.models import Item
from app.schemas.schemas import ItemCreate, ItemUpdate

class ItemCRUD:
    async def get_item(self, db: AsyncSession, item_id: int) -> Optional[Item]:
        """Obtiene un item por ID (solo activos)"""
        result = await db.execute(
            select(Item).filter(Item.id == item_id, Item.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_items(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Item]:
        """Obtiene lista de items activos"""
        result = await db.execute(
            select(Item)
            .filter(Item.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_items_by_owner(self, db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 100) -> List[Item]:
        """Obtiene items de un propietario específico (solo activos)"""
        result = await db.execute(
            select(Item)
            .filter(Item.owner_id == owner_id, Item.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_item(self, db: AsyncSession, item: ItemCreate, owner_id: int) -> Item:
        """Crea un nuevo item"""
        db_item = Item(
            title=item.title,
            description=item.description,
            price=item.price,
            owner_id=owner_id
        )
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item

    async def update_item(self, db: AsyncSession, item_id: int, item_update: ItemUpdate) -> Optional[Item]:
        """Actualiza un item"""
        db_item = await self.get_item(db, item_id)
        if not db_item:
            return None
        
        update_data = item_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        await db.commit()
        await db.refresh(db_item)
        return db_item

    async def soft_delete_item(self, db: AsyncSession, item_id: int) -> bool:
        """Elimina un item (soft delete)"""
        db_item = await self.get_item(db, item_id)
        if not db_item:
            return False
        
        db_item.soft_delete()
        await db.commit()
        return True

    async def restore_item(self, db: AsyncSession, item_id: int) -> bool:
        """Restaura un item eliminado"""
        result = await db.execute(
            select(Item).filter(Item.id == item_id, Item.is_deleted == True)
        )
        db_item = result.scalar_one_or_none()
        if not db_item:
            return False
        
        db_item.restore()
        await db.commit()
        return True

    async def get_deleted_items(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Item]:
        """Obtiene items eliminados (soft delete)"""
        result = await db.execute(
            select(Item)
            .filter(Item.is_deleted == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

# Instancia global del CRUD
item_crud = ItemCRUD()
