# pylint: disable=E402
import asyncio
import random
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

from faker import Faker


file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

from models import Area, AreaTranslation, Category, CategoryTranslation, Doctor, DoctorTranslation

from core.config import Language
from core.context import request_context
from core.db.base import async_session


# Cache the initial areas and categories id so we can use when seed the doctor data
cached_data = {"area": [], "category": []}

languages = [Language.English, Language.Chinese]

fakers = [Faker(Language.English.value), Faker(Language.Chinese.value)]

related_data = {
    "areas": [
        {
            Language.English: "Mariana Medical Central, Room 2005",
            Language.Chinese: "马里亚纳医疗中心，2005 室",
        },
        {
            Language.English: "TH Medical Centre, Shop 2, GF, Treasure Garden",
            Language.Chinese: "TH 医疗中心, 2 号店, 宝园",
        },
    ],
    "categories": [
        {
            Language.English: "General practitioner",
            Language.Chinese: "全科医生",
        },
        {
            Language.English: "Yoga trainer",
            Language.Chinese: "瑜伽教练",
        },
    ],
}

doctor_basic = {
    "area_id": None,
    "category_ids": [],
    "price": 100,
    "phone_number": "180660487",
    "working_hours": {
        "monday": {"is_available": True, "time_start_at": "09:00:00", "time_end_at": "17:00:00"},
        "tuesday": {"is_available": True, "time_start_at": "09:00:00", "time_end_at": "17:00:00"},
        "wednesday": {"is_available": True, "time_start_at": "09:00:00", "time_end_at": "17:00:00"},
        "thursday": {"is_available": True, "time_start_at": "09:00:00", "time_end_at": "17:00:00"},
        "friday": {"is_available": True, "time_start_at": "09:00:00", "time_end_at": "17:00:00"},
        "saturday": {"is_available": False, "time_start_at": "09:00:00", "time_end_at": "17:00:00"},
        "sunday": {"is_available": False, "time_start_at": "09:00:00", "time_end_at": "17:00:00"},
        "holidays": {"is_available": False, "time_start_at": "09:00:00", "time_end_at": "17:00:00"},
    },
}


async def create_doctor_data(language: Language = Language.English) -> Dict[str, Any]:
    data = deepcopy(doctor_basic)
    if cached_data["area"]:
        data["area_id"] = random.choice(cached_data["area"])
    if cached_data["category"]:
        data["category_ids"] = [random.choice(cached_data["category"])]
    data["price"] = random.uniform(1.5, 2.5) * 1000
    data["phone_number"] = f'{data["phone_number"]}{random.randint(100, 999)}'
    data["name"] = fakers[0].name() if language == Language.English else fakers[1].name()
    return data


async def seed_related_data(items, model, model_translation):  # type: ignore
    def _get_original_id(_instance) -> str:
        return getattr(_instance, f"{model.__name__.lower()}_id")

    for item in items:
        query = await model_translation.filter({"name": item[Language.English]})
        instance = query.first()
        if instance:
            original_id = _get_original_id(instance)
            print(model.__name__, original_id, "skipped")
            continue

        obj_in = dict(
            name=item[Language.English],
        )
        instance = await model.create(obj_in=obj_in, language=Language.English)
        fk = model.__translation__.fk
        obj_in = dict(language_code=Language.Chinese, name=item[Language.Chinese])
        obj_in[fk] = instance.id
        await model_translation(**obj_in).save()
        print(model.__name__, instance.id, "created")


async def seed_cache_data() -> None:
    for instance in await Area.all():
        cached_data["area"].append(instance.id)
    for instance in await Category.all():
        cached_data["category"].append(instance.id)


async def seed_doctor_data() -> None:
    print("Initialing doctor data...")
    doctors = await Doctor.all()
    if len(doctors):
        # Data has been created
        return

    for index in range(0, 10):
        language_index = random.choice([0, 1])
        other_language = random.choice([0, 1, 2])
        language = languages[language_index]
        obj_in = await create_doctor_data(language=language)
        instance = await Doctor.create(obj_in=obj_in, language=language)
        if other_language == 0:
            # 1/3 of record will available in other language
            if language_index == 1:
                faker = fakers[0]
                language = languages[0]
            else:
                faker = fakers[1]
                language = languages[1]
            instance_trans = DoctorTranslation(doctor_id=instance.id, language_code=language, name=faker.name())
            await instance_trans.save()
        print("Doctor", instance.id, "created")


async def seed_data() -> None:
    print("Initialing categories and areas data...")
    await seed_related_data(related_data["areas"], Area, AreaTranslation)
    await seed_related_data(related_data["categories"], Category, CategoryTranslation)
    await seed_cache_data()
    await seed_doctor_data()


async def main() -> None:
    try:
        token = request_context.init()
        db = async_session()
        request_context.set("db", db)
        await seed_data()
    finally:
        await db.close()
        request_context.reset(token)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
