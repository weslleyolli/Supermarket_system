"""
Repositório de categorias
"""

from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infrastructure.database.models.product import Category
from app.presentation.schemas.product import CategoryCreate, CategoryUpdate


class CategoryRepository:
    """Repositório para operações com categorias"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, category_id: int) -> Optional[Category]:
        """Busca categoria por ID"""
        return self.db.query(Category).filter(Category.id == category_id).first()

    def get_by_name(self, name: str) -> Optional[Category]:
        """Busca categoria por nome"""
        return self.db.query(Category).filter(Category.name.ilike(f"%{name}%")).first()

    def get_all(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[Category]:
        """Lista todas as categorias"""
        query = self.db.query(Category)

        if active_only:
            query = query.filter(Category.is_active == True)

        return query.offset(skip).limit(limit).all()

    def create(self, category_data: CategoryCreate) -> Category:
        """Cria nova categoria"""
        # Verificar se nome já existe
        existing = self.get_by_name(category_data.name)
        if existing:
            raise ValueError("Nome da categoria já existe")

        db_category = Category(**category_data.model_dump())

        try:
            self.db.add(db_category)
            self.db.commit()
            self.db.refresh(db_category)
            return db_category
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Erro ao criar categoria")

    def update(
        self, category_id: int, category_data: CategoryUpdate
    ) -> Optional[Category]:
        """Atualiza categoria"""
        db_category = self.get_by_id(category_id)
        if not db_category:
            return None

        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_category)
            return db_category
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Erro ao atualizar categoria")

    def delete(self, category_id: int) -> bool:
        """Remove categoria (soft delete)"""
        db_category = self.get_by_id(category_id)
        if not db_category:
            return False

        # Verificar se tem produtos associados
        from app.infrastructure.database.models.product import Product

        products_count = (
            self.db.query(Product).filter(Product.category_id == category_id).count()
        )

        if products_count > 0:
            raise ValueError("Não é possível remover categoria com produtos associados")

        db_category.is_active = False
        self.db.commit()
        return True

    def get_products_count(self, category_id: int) -> int:
        """Conta produtos da categoria"""
        from app.infrastructure.database.models.product import Product

        return (
            self.db.query(Product)
            .filter(and_(Product.category_id == category_id, Product.is_active == True))
            .count()
        )
