from fastapi import Header

from core.config import Language
from core.context import request_context


async def check_language_code(
    X_Language_Code: Language = Header(
        Language.English,
        description="Activated language code for current request.",
        example=Language.English,
    )
) -> Language:
    request_context.set("language", X_Language_Code)
