import json
import random
from typing import Any, Dict

import models
import pytest
import schemas
from scripts.initial import create_doctor_data


@pytest.fixture
async def random_area(db_context) -> models.Area:
    """
    Return random area that existing in db
    """
    areas = await models.Area.all()
    return random.choice(areas)


@pytest.fixture
async def random_category(db_context) -> models.Category:
    """
    Return random category that existing in db
    """
    areas = await models.Area.all()
    return random.choice(areas)


@pytest.fixture
async def doctor_data(random_area, random_category) -> Dict[str, Any]:
    """
    Create random client payload for doctor
    """
    data = await create_doctor_data()
    data["area_id"] = random_area.id
    data["categories_id"] = [random_category.id]
    return json.loads(schemas.DoctorBase(**data).json())
