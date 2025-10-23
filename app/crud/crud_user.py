from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.models import User
from app.schemas.schemas import UserCreate, UserUpdate
from app.core.security import get_password_hash

class UserCRUD:
    async def get_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Obtiene un usuario por ID (solo activos)"""
        result = await db.execute(
            select(User).filter(User.id == user_id, User.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Obtiene un usuario por email (solo activos)"""
        result = await db.execute(
            select(User).filter(User.email == email, User.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_user_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Obtiene un usuario por username (solo activos)"""
        result = await db.execute(
            select(User).filter(User.username == username, User.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_users(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtiene lista de usuarios activos"""
        result = await db.execute(
            select(User)
            .filter(User.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_users_with_posts(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtiene usuarios con sus posts (solo activos)"""
        result = await db.execute(
            select(User)
            .options(selectinload(User.posts), selectinload(User.comments))
            .filter(User.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_user(self, db: AsyncSession, user: UserCreate) -> User:
        """Crea un nuevo usuario"""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            name=user.name,
            hashed_password=hashed_password,
            is_active=user.is_active,
            is_superuser=user.is_superuser
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def update_user(self, db: AsyncSession, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Actualiza un usuario"""
        db_user = await self.get_user(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def soft_delete_user(self, db: AsyncSession, user_id: int) -> bool:
        """Elimina un usuario (soft delete)"""
        db_user = await self.get_user(db, user_id)
        if not db_user:
            return False
        
        db_user.soft_delete()
        await db.commit()
        return True

    async def restore_user(self, db: AsyncSession, user_id: int) -> bool:
        """Restaura un usuario eliminado"""
        result = await db.execute(
            select(User).filter(User.id == user_id, User.is_deleted == True)
        )
        db_user = result.scalar_one_or_none()
        if not db_user:
            return False
        
        db_user.restore()
        await db.commit()
        return True

    async def get_deleted_users(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtiene usuarios eliminados (soft delete)"""
        result = await db.execute(
            select(User)
            .filter(User.is_deleted == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

# Instancia global del CRUD
user_crud = UserCRUD()