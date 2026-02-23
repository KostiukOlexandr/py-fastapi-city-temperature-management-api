from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import httpx, asyncio

from app import crud, schemas, deps, models


router = APIRouter(prefix="/temperatures", tags=["temperatures"])

async def fetch_temp(client: httpx.AsyncClient, city_name: str) -> float:
    return 5.0

@router.post("/update", response_model=list[schemas.TemperatureRead], status_code=status.HTTP_201_CREATED)
async def update_temperatures(db: Session = Depends(deps.get_db)):
    cities = crud.get_cities(db)
    if not cities:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No cities found")

    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [fetch_temp(client, city.name) for city in cities]
        fetched = await asyncio.gather(*tasks, return_exceptions=True)

    temps = []
    for city, result in zip(cities, fetched):
        if isinstance(result, Exception):
            continue
        temps.append(models.Temperature(
            city_id=city.id,
            temperature=result,
            date_time=datetime.utcnow()
        ))

    db.add_all(temps)
    db.commit()
    for t in temps:
        db.refresh(t)

    return temps


@router.get("/", response_model=list[schemas.TemperatureRead])
def read_temperatures(
    city_id: int | None = Query(default=None),
    db: Session = Depends(deps.get_db)
):
    return crud.get_temperatures(db, city_id=city_id)
