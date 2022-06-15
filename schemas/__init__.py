"""
Data IO between client and service
"""
import uuid
from datetime import datetime
from typing import List, Optional

from faker import Faker
from pydantic import BaseModel, Field, StrictBool, condecimal

UUID_EXAMPLE = uuid.uuid4()
fake: Faker = Faker(["zh_CN"])
fake.seed_locale("zh_CN", 0)
Faker.seed(0)


class Root(BaseModel):
    name: str = Field(title="The project name", example="home-assessment")


class TimeWorking(BaseModel):
    is_available: StrictBool = Field(True, description="Flag this day is available for working", example=True)
    time_start_at: str = Field("09:00:00", description="Start working time", example="09:00:00")
    time_end_at: str = Field("17:00:00", description="End working time", example="17:00:00")


class WorkingHours(BaseModel):
    monday: TimeWorking = Field(title="Working time on Monday")
    tuesday: TimeWorking = Field(title="Working time on Tuesday")
    wednesday: TimeWorking = Field(title="Working time on Wednesday")
    thursday: TimeWorking = Field(title="Working time on Thursday")
    friday: TimeWorking = Field(title="Working time on Friday")
    saturday: TimeWorking = Field(title="Working time on Saturday")
    sunday: TimeWorking = Field(title="Working time on Sunday")
    holidays: TimeWorking = Field(title="Working time on Holidays")


class DoctorBase(BaseModel):
    area_id: uuid.UUID = Field(..., description="Area id", example=UUID_EXAMPLE)
    category_ids: List[uuid.UUID] = Field(
        [], description="Related categories that the doctor belongs to", example=[UUID_EXAMPLE]
    )
    price: condecimal(ge=0, le=100000) = Field(..., description="The price", example=100)
    phone_number: str = Field(None, description="The default phone number", example=fake.phone_number())
    name: str = Field(..., description="Doctor's name", max_length=150, example=fake.name())
    working_hours: WorkingHours = Field(description="Working hours")


class Doctor(DoctorBase):
    id: uuid.UUID = Field(..., description="Primary key", example=UUID_EXAMPLE)
    created_at: datetime = Field(..., title="Created at datetime", example="2021-12-27T14:01:01.000000+00:00")
    updated_at: datetime = Field(..., title="Updated at datetime", example="2021-12-27T14:01:01.000000+00:00")

    class Config:
        orm_mode = True


class DoctorCreate(DoctorBase):
    working_hours: Optional[WorkingHours] = Field(None, description="Working hours")


class Doctors(BaseModel):
    items: List[Doctor]


class AreaBase(BaseModel):
    name: str = Field(..., description="Area name", example="Mariana Medical Central", max_length=255)


class Area(AreaBase):
    id: uuid.UUID = Field(..., description="Primary key", example=UUID_EXAMPLE)

    class Config:
        orm_mode = True


class Areas(BaseModel):
    items: List[Area]


class CategoryBase(BaseModel):
    name: str = Field(..., description="Category name", example="General Practitioner", max_length=255)


class Category(AreaBase):
    id: uuid.UUID = Field(..., description="Primary key", example=UUID_EXAMPLE)

    class Config:
        orm_mode = True
