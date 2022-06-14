# pylint: disable=E402
import asyncio
import sys
from pathlib import Path


file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

from models import Area, AreaTranslation, Category, CategoryTranslation, Doctor, DoctorTranslation

from core.config import Language
from core.context import request_context
from core.db.base import async_session


data = {
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


async def init_related_data(items, model, model_translation):  # type: ignore
    def _get_original_id(_instance) -> str:
        return getattr(_instance, f"{model.__name__.lower()}_id")

    for item in items:
        query = await model_translation.filter({"name": item[Language.English]})
        instance = query.first()
        if instance:
            print(model.__name__, _get_original_id(instance), "skipped")
            continue

        obj_in = dict(
            name=item[Language.English],
        )
        instance = await model.create(obj_in=obj_in, language=Language.English)
        print(instance, type(instance))
        fk = model.__translation__.fk
        obj_in = dict(language_code=Language.Chinese, name=item[Language.Chinese])
        obj_in[fk] = instance.id
        await model_translation(**obj_in).save()
        print(model.__name__, instance.id, "created")


async def init_data() -> None:
    print("Initialing data...")
    await init_related_data(data["areas"], Area, AreaTranslation)
    await init_related_data(data["categories"], Category, CategoryTranslation)


async def main() -> None:
    try:
        token = request_context.init()
        db = async_session()
        request_context.set("db", db)
        await init_data()
    finally:
        await db.close()
        request_context.reset(token)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
