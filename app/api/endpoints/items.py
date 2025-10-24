from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.schemas import Item, ItemCreate, ItemUpdate
from app.crud.crud_item import item_crud
from app.models.models import User as UserModel

router = APIRouter()

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Crear un nuevo item (requiere autenticación)"""
    return await item_crud.create_item(db=db, item=item, owner_id=current_user.id)

@router.get("/", response_model=List[Item])
async def read_items(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Obtener lista de items (requiere autenticación)"""
    items = await item_crud.get_items(db, skip=skip, limit=limit)
    return items

@router.get("/my-items", response_model=List[Item])
async def read_my_items(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Obtener items del usuario actual (requiere autenticación)"""
    items = await item_crud.get_items_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    return items

@router.get("/{item_id}", response_model=Item)
async def read_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Obtener un item específico (requiere autenticación)"""
    db_item = await item_crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.put("/{item_id}", response_model=Item)
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Actualizar un item (solo el propietario o superusuarios)"""
    db_item = await item_crud.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if db_item.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this item"
        )
    
    updated_item = await item_crud.update_item(db, item_id=item_id, item_update=item_update)
    return updated_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Eliminar un item (soft delete, solo el propietario o superusuarios)"""
    db_item = await item_crud.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if db_item.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this item"
        )
    
    success = await item_crud.soft_delete_item(db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found during soft delete")

@router.post("/{item_id}/restore", response_model=dict)
async def restore_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Restaurar un item eliminado (requiere autenticación)"""
    success = await item_crud.restore_item(db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found or not deleted")
    return {"message": "Item restored successfully"}
