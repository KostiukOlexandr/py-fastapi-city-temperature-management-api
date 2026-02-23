from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional, List
from app import models, schemas
from dateutil import parser


def create_temperature(
    db: Session,
    city_id: int,
    temperature: float,
    dt: Optional[datetime] = None
) -> models.Temperature:
    if dt is None:
        dt = datetime.utcnow()
    temperature_obj = models.Temperature(
        city_id=city_id,
        temperature=temperature,
        date_time=dt
    )
    db.add(temperature_obj)
    db.commit()
    db.refresh(temperature_obj)
    return temperature_obj


def bulk_create_temperatures(db: Session, items: List[dict]) -> List[models.Temperature]:
    temps = []
    for item in items:
        dt_value = item.get("date_time")
        if isinstance(dt_value, str):
            dt_value = parser.parse(dt_value)
        elif dt_value is None:
            dt_value = datetime.utcnow()

        temps.append(models.Temperature(
            city_id=item["city_id"],
            temperature=item["temperature"],
            date_time=dt_value
        ))

    db.add_all(temps)
    db.commit()
    for t in temps:
        db.refresh(t)
    return temps
