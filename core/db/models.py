import datetime
import logging
import re
import uuid
from typing import Any, Dict, List, NoReturn, Optional, Tuple, Type, TypedDict, TypeVar

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import InstrumentedAttribute

from core.config import Language
from core.db.base import Base
from core.db.deps import get_db
from core.db.exceptions import DatabaseValidationError
from core.db.types import UUID, default_uuid
from core.db.utils import operators_map


logger = logging.getLogger(__name__)

TBase = TypeVar("TBase", bound="BaseModel")


class TranslationConfig:
    model: TBase
    fields: List[str]

    def __init__(self, fields: List[str], model: TBase) -> NoReturn:
        self.fields = fields
        self.model = model

    @property
    def fk(self) -> str:
        return "%s_id" % self.model.__name__.lower().replace("translation", "")

    def get_translation_fields(self) -> List[InstrumentedAttribute]:
        _fields = []
        for field in self.fields:
            _fields.append(getattr(self.model, field))
        return _fields

    def get_fk_field(self) -> InstrumentedAttribute:
        return getattr(self.model, self.fk)


def utcnow() -> datetime.datetime:
    """Generates timezone-aware UTC datetime."""
    return datetime.datetime.now(datetime.timezone.utc)


class TimestampMixin:
    created_at = sa.Column(sa.DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = sa.Column(sa.DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class BaseModel(Base):
    __abstract__ = True

    def __str__(self):
        return f"<{type(self).__name__}({self.id=})>"

    @classmethod
    def _raise_validation_exception(cls, e: IntegrityError) -> NoReturn:
        info = e.orig.args[0] if e.orig.args else ""
        if (match := re.findall(r"Key \((.*)\)=\(.*\) already exists|$", info)) and match[0]:
            raise DatabaseValidationError(f"Unique constraint violated for {cls.__name__}", match[0]) from e
        if (match := re.findall(r"Key \((.*)\)=\(.*\) conflicts with existing key|$", info)) and match[0]:
            field_name = match[0].split(",", 1)[0]
            raise DatabaseValidationError(f"Range overlapped for {cls.__name__}", field_name) from e
        if (match := re.findall(r"Key \((.*)\)=\(.*\) is not present in table|$", info)) and match[0]:
            raise DatabaseValidationError(f"Foreign key constraint violated for {cls.__name__}", match[0]) from e
        logger.error("Integrity error for %s: %s", cls.__name__, e)
        raise e

    @classmethod
    def _get_query(cls, prefetch: Optional[Tuple[str, ...]] = None, options: Optional[List[Any]] = None) -> Any:
        query = sa.select(cls)
        if prefetch:
            if not options:
                options = []
            options.extend(selectinload(getattr(cls, x)) for x in prefetch)
            query = query.options(*options).execution_options(populate_existing=True)
        return query

    @classmethod
    async def _get_joined_query(cls: Type[TBase], language) -> sa.orm.Query:
        translation: TranslationConfig = cls.__translation__
        TranslationModel: TBase = translation.model  # noqa
        query = (
            sa.select(cls, *translation.get_translation_fields())
            .join(TranslationModel, translation.get_fk_field() == cls.id)
            .where(TranslationModel.language_code == language)
        )
        return query

    @classmethod
    def _get_db(cls) -> AsyncSession:
        return get_db()

    @classmethod
    async def all(cls: Type[TBase], prefetch: Optional[Tuple[str, ...]] = None) -> List[TBase]:
        query = cls._get_query(prefetch)
        db = get_db()
        db_execute = await db.execute(query)
        return db_execute.scalars().all()

    @classmethod
    async def get(
        cls: Type[TBase],
        id: uuid.UUID,
        language: Optional[Language] = None,
    ) -> Optional[TBase]:
        db = get_db()
        if language:
            translation: TranslationConfig = cls.__translation__
            TranslationModel: TBase = translation.model  # noqa
            query = (
                sa.select(cls, *translation.get_translation_fields())
                .join(TranslationModel, translation.get_fk_field() == cls.id)
                .where(cls.id == id)
                .where(TranslationModel.language_code == language)
            )
            db_execute = await db.execute(query)
            instance = db_execute.first()
            if not instance:
                return None
            return instance[0]
        query = sa.select(cls).where(cls.id == id)
        db_execute = await db.execute(query)
        return db_execute.first()

    @classmethod
    async def filter(
        cls: Type[TBase],
        filters: Dict[str, Any],
        sorting: Optional[Dict[str, str]] = None,
        prefetch: Optional[Tuple[str, ...]] = None,
    ) -> List[TBase]:
        query = cls._get_query(prefetch)
        db = get_db()
        if sorting is not None:
            query = query.order_by(*cls._build_sorting(sorting))
        db_execute = await db.execute(query.where(sa.and_(True, *cls._build_filters(filters))))
        return db_execute.scalars()

    @classmethod
    async def join_filter(cls: Type[TBase], language=Language.English):
        db = get_db()
        translation: TranslationConfig = cls.__translation__
        TranslationModel: TBase = translation.model  # noqa
        query = (
            sa.select(cls, *translation.get_translation_fields())
            .join(TranslationModel, translation.get_fk_field() == cls.id)
            .where(TranslationModel.language_code == language)
        )
        db_execute = await db.execute(query)
        return db_execute.scalars().all()

    @classmethod
    def _build_sorting(cls, sorting: Dict[str, str]) -> List[Any]:
        """Build list of ORDER_BY clauses"""
        result = []
        for field_name, direction in sorting.items():
            field = getattr(cls, field_name)
            result.append(getattr(field, direction)())
        return result

    @classmethod
    def _build_filters(cls, filters: Dict[str, Any]) -> List[Any]:
        """Build list of WHERE conditions"""
        result = []
        for expression, value in filters.items():
            parts = expression.split("__")
            op_name = parts[1] if len(parts) > 1 else "exact"
            if op_name not in operators_map:
                raise KeyError(f"Expression {expression} has incorrect operator {op_name}")
            operator = operators_map[op_name]
            column = getattr(cls, parts[0])
            result.append(operator(column, value))
        return result

    async def save(self, commit: bool = True) -> None:
        db: AsyncSession = get_db()
        db.add(self)
        try:
            if commit:
                await db.commit()
            else:
                await db.flush()
        except IntegrityError as e:
            self._raise_validation_exception(e)

    async def update_attrs(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    async def create(cls, obj_in: Dict[str, Any], language: Language) -> TBase:
        """
        Create model with multiple language supported
        """
        translation: TranslationConfig = cls.__translation__
        obj_trans = dict()
        for field in translation.fields:
            if field in obj_in:
                obj_trans[field] = obj_in.pop(field)

        instance = cls(**obj_in)
        await instance.save()

        obj_trans["language_code"] = language.value
        obj_trans[translation.fk] = instance.id
        instance_trans = translation.model(**obj_trans)
        await instance_trans.save()

        return await cls.get(id=instance.id, language=language)


class UUIDBaseModel(BaseModel):
    __abstract__ = True

    id = sa.Column(UUID(), default=default_uuid, primary_key=True)
