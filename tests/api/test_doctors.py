import uuid
from typing import Any, Dict

import pytest
from fastapi import status
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


async def test_list_of_doctor(client: AsyncClient) -> None:
    response = await client.get("/api/doctors/")
    assert response.status_code == status.HTTP_200_OK


async def test_list_of_doctor_with_query_params(client: AsyncClient) -> None:
    params = {"area_id": uuid.uuid4(), "price_min": 0, "price_max": 1000}
    response = await client.get("/api/doctors/", params=params)
    assert response.status_code == status.HTTP_200_OK


async def test_doctor_not_existed(client: AsyncClient) -> None:
    response = await client.get(f"/api/doctors/{uuid.uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_create_doctor_invalid_area(client: AsyncClient, doctor_data: Dict[str, Any]) -> None:
    doctor_data["area_id"] = str(uuid.uuid4())
    response = await client.post(f"/api/doctors/", json=doctor_data)
    data = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Area is not found" in data["detail"]


async def test_create_doctor_invalid_category(client: AsyncClient, doctor_data: Dict[str, Any]) -> None:
    doctor_data["category_ids"] = [str(uuid.uuid4())]
    response = await client.post(f"/api/doctors/", json=doctor_data)
    data = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Category is not found" in data["detail"]
