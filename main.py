from typing import Any

from fastapi import Depends, FastAPI
from schemas import Root

from api.deps import check_language_code
from api.middlewares import ContextMiddleware
from api.routers import api_router
from core import exceptions
from core.config import settings
from core.db.deps import init_db
from core.db.exceptions import DatabaseValidationError


dependencies = [Depends(check_language_code), Depends(init_db)]

app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG, version=settings.VERSION, dependencies=dependencies)
app.include_router(api_router, prefix="/api")
app.add_exception_handler(DatabaseValidationError, exceptions.database_validation_exception_handler)
app.add_middleware(ContextMiddleware)


@app.get("/", response_model=Root, include_in_schema=False)
def root() -> Any:
    """
    Root path, for health check or ALB check, dont need to include this in the api schema
    """
    return {"name": settings.PROJECT_NAME}
