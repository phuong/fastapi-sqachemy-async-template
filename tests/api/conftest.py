import random

import models
import pytest
from faker import Faker


fake: Faker = Faker(["zh_CN"])
fake.seed_locale("zh_CN", 0)
Faker.seed(0)


@pytest.fixture
async def random_area(db_context) -> models.Area:
    """
    Return random area that existing in db
    """
    areas = await models.Area.all()
    return random.choice(areas)


@pytest.fixture
async def doctor_data(random_area) -> models.Doctor:
    return {
        "area_id": str(random_area.id),
        "category_ids": [],
        "price": 100,
        "phone_number": "18066048764",
        "name": fake.name(),
        "working_hours": {
            "monday": {"is_available": True, "time_start_at": "09:00:00", "time_end_at": "17:00:00"},
            "tuesday": {"is_available": True, "time_start_at": "09:00:00", "time_end_at": "17:00:00"},
            "wednesday": {"is_available": True, "time_start_at": "09:00:00", "time_end_at": "17:00:00"},
            "thursday": {"is_available": True, "time_start_at": "09:00:00", "time_end_at": "17:00:00"},
            "friday": {"is_available": True, "time_start_at": "09:00:00", "time_end_at": "17:00:00"},
            "saturday": {"is_available": True, "time_start_at": "09:00:00", "time_end_at": "17:00:00"},
            "sunday": {"is_available": True, "time_start_at": "09:00:00", "time_end_at": "17:00:00"},
            "holidays": {"is_available": True, "time_start_at": "09:00:00", "time_end_at": "17:00:00"},
        },
    }
