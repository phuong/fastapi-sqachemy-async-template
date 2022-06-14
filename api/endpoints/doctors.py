from typing import Any, List, Optional
from uuid import UUID

import models
import schemas
from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import condecimal

from core.config import Language
from core.context import request_context
from core.db.models import BaseModel


router = APIRouter()


async def _get_or_404(model: BaseModel, id: UUID, language: Optional[Language] = None) -> BaseModel:
    instance = await model.get(id=id, language=language)
    if not instance:
        raise HTTPException(status_code=404, detail=f"{model.__name__} is not found {id}")
    return instance


async def _validate_input_data(data: schemas.DoctorCreate):
    await _get_or_404(models.Area, data.area_id)
    for category_id in data.category_ids:
        await _get_or_404(models.Category, category_id)


async def _process_instance(instance: models.Doctor) -> models.Doctor:
    """
    Append addition data field for the Doctor
    """
    categories = await models.DoctorCategory.filter({"doctor_id": instance.id})
    instance.category_ids = [item.id for item in categories]
    return instance


@router.post("/", response_model=schemas.Doctor)
async def create_doctor(
    data: schemas.DoctorCreate,
) -> Any:
    # Basic validate
    await _validate_input_data(data)

    obj_in = data.dict()
    category_ids = obj_in.pop("category_ids")

    instance: models.Doctor = await models.Doctor.create(obj_in, language=request_context.language)
    for category_id in category_ids:
        item = models.DoctorCategory(doctor_id=instance.id, category_id=category_id)
        await item.save()
    return instance


@router.get("/{doctor_id}", response_model=schemas.Doctor)
async def retrieve_doctor(
    doctor_id: UUID = Path(..., description="The doctor id", example=schemas.UUID_EXAMPLE)
) -> Any:
    instance = await _get_or_404(models.Doctor, doctor_id, language=request_context.language)
    if instance:
        instance = await _process_instance(instance)
    return instance


@router.get("/", response_model=schemas.Doctors)
async def list_doctors(
    area_id: Optional[UUID] = Query(None, description="The area ID", example=schemas.UUID_EXAMPLE),
    category_ids: Optional[List[UUID]] = Query([], description="The list of category", example=[schemas.UUID_EXAMPLE]),
    price_min: condecimal(ge=0, le=100000) = Query(0, description="The min of price range", example=0),
    price_max: condecimal(ge=0, le=100000) = Query(0, description="The max of price range", example=1000.0),
) -> Any:
    language = request_context.language

    # Prepare the filter conditions
    filters = dict()
    if area_id:
        filters["area_id"] = area_id
    if category_ids:
        filters["category_id__in"] = category_ids
    if price_min or price_max:
        filters["price__between"] = (min(price_min, price_max), max(price_min, price_max))

    items = []
    for instance in await models.Doctor.filter(filters, language=language):
        items.append(await _process_instance(instance))
    return {"items": items}
