from fastapi import APIRouter

from api.endpoints import doctors


api_router = APIRouter()

# Doctors
api_router.include_router(doctors.router, prefix="/doctors", tags=["Doctors"])
