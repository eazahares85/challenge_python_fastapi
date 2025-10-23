from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional


class SoftDeleteMixin:
    """
    Mixin que añade funcionalidad de soft delete a los modelos.
    Los registros no se eliminan físicamente, sino que se marcan como eliminados.
    """
    
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def soft_delete(self) -> None:
        """Marca el registro como eliminado (soft delete)"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restaura un registro eliminado"""
        self.is_deleted = False
        self.deleted_at = None
    
    @classmethod
    def filter_active(cls, query):
        """Filtra solo los registros que no están eliminados"""
        return query.filter(cls.is_deleted == False)
    
    @classmethod
    def filter_deleted(cls, query):
        """Filtra solo los registros que están eliminados"""
        return query.filter(cls.is_deleted == True)
    
    @classmethod
    def filter_all(cls, query):
        """Incluye todos los registros (activos y eliminados)"""
        return query
