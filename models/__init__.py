from typing import Any, Dict, List, Optional

import sqlalchemy as sa
from sqlalchemy.orm import column_property

from core.config import Language
from core.db.models import TimestampMixin, TranslationConfig, UUIDBaseModel
from core.db.types import UUID


class AreaTranslation(TimestampMixin, UUIDBaseModel):
    __tablename__ = "areas_translation"
    __table_args__ = (sa.UniqueConstraint("area_id", "language_code", name="uq_area_id_language_code"),)

    area_id = sa.Column(UUID(), sa.ForeignKey("areas.id"), nullable=False)
    language_code = sa.Column(sa.String(5), nullable=False, index=True)
    name = sa.Column(sa.String(255))


class Area(TimestampMixin, UUIDBaseModel):
    """
    In the limited of this project, I assuming that an area will contains full data of an "Address" object
    """

    __tablename__ = "areas"
    __translation__ = TranslationConfig(fields=["name"], model=AreaTranslation)

    name = column_property(AreaTranslation.name)
    # distinct_id, # country_code and so on


class CategoryTranslation(TimestampMixin, UUIDBaseModel):
    __tablename__ = "categories_translation"
    __table_args__ = (sa.UniqueConstraint("category_id", "language_code", name="uq_category_id_language_code"),)

    category_id = sa.Column(UUID(), sa.ForeignKey("categories.id"), nullable=False)
    language_code = sa.Column(sa.String(5), nullable=False, index=True)
    name = sa.Column(sa.String(255))


class Category(TimestampMixin, UUIDBaseModel):
    __tablename__ = "categories"
    __translation__ = TranslationConfig(fields=["name"], model=CategoryTranslation)

    name = column_property(CategoryTranslation.name)

    doctors = sa.orm.relationship("DoctorCategory", back_populates="category")


class DoctorTranslation(TimestampMixin, UUIDBaseModel):
    __tablename__ = "doctors_translation"
    __table_args__ = (sa.UniqueConstraint("doctor_id", "language_code", name="uq_doctor_id_language_code"),)

    doctor_id = sa.Column(UUID(), sa.ForeignKey("doctors.id"), nullable=False)
    language_code = sa.Column(sa.String(5), nullable=False, index=True)
    name = sa.Column(sa.String(150))


class Doctor(TimestampMixin, UUIDBaseModel):
    """
    Doctor class with none-translation fields
    """

    __tablename__ = "doctors"
    __translation__ = TranslationConfig(fields=["name"], model=DoctorTranslation)

    area_id = sa.Column(UUID(), sa.ForeignKey("areas.id"), nullable=False)
    price = sa.Column(sa.DECIMAL(precision=13, scale=2), nullable=True)
    phone_number = sa.Column(sa.String(13), nullable=True)
    working_hours = sa.Column(sa.JSON())
    name = column_property(DoctorTranslation.name)

    categories = sa.orm.relationship("DoctorCategory", back_populates="doctor")

    @classmethod
    async def filter(
        cls: "Doctor",
        filters: Dict[str, Any],
        *,
        language: Language,
        sorting: Optional[Dict[str, str]] = None,
    ) -> List["Doctor"]:
        db = cls._get_db()
        query = await cls._get_joined_query(language)
        if filters:
            category_ids = filters.pop("category_id__in", [])
            query = query.where(sa.and_(True, *cls._build_filters(filters)))
            if category_ids:
                query = query.join(Doctor.categories).where(DoctorCategory.category_id.in_(category_ids))
        db_execute = await db.execute(query)
        return db_execute.scalars().all()

    @classmethod
    async def create(cls, obj_in: Dict[str, Any], language: Language) -> "Doctor":
        category_ids = obj_in.pop("category_ids", [])
        instance = await super().create(obj_in=obj_in, language=language)
        for category_id in category_ids:
            item = DoctorCategory(doctor_id=instance.id, category_id=category_id)
            await item.save()
        return instance


class DoctorCategory(UUIDBaseModel):
    """
    M2M relationship between doctor and category
    """

    __tablename__ = "doctors_categories"
    __table_args__ = (sa.UniqueConstraint("doctor_id", "category_id", name="uq_doctor_id_category_id"),)

    doctor_id = sa.Column(UUID(), sa.ForeignKey("doctors.id"), nullable=False)
    category_id = sa.Column(UUID(), sa.ForeignKey("categories.id"), nullable=False)

    doctor = sa.orm.relationship("Doctor", back_populates="categories")
    category = sa.orm.relationship("Category", back_populates="doctors")
