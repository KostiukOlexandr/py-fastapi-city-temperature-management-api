from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional, List
from app import models, schemas


def create_city(db: Session, city_in: schemas.CityCreate) -> models.City:
    city = models.City(
        name=city_in.name,
        additional_info=city_in.additional_info
    )
    db.add(city)
    try:
        db.commit()
        db.refresh(city)
    except IntegrityError:
        db.rollback()
        raise
    return city


def get_cities(db: Session) -> List[models.City]:
    return db.query(models.City).all()


def get_city(db: Session, city_id: int) -> Optional[models.City]:
    return db.query(models.City).filter(models.City.id == city_id).first()


def get_city_by_name(db: Session, name: str) -> Optional[models.City]:
    return db.query(models.City).filter(models.City.name == name).first()


def delete_city(db: Session, city_id: int) -> Optional[models.City]:
    city = get_city(db, city_id)
    if city:
        db.delete(city)
        db.commit()
        return city
    return None


def create_temperature(
    db: Session,
    city_id: int,
    temp: float,
    dt: Optional[datetime] = None
) -> models.Temperature:
    if dt is None:
        dt = datetime.utcnow()
    temperature = models.Temperature(
        city_id=city_id,
        temperature=temp,
        date_time=dt
    )
    db.add(temperature)
    db.commit()
    db.refresh(temperature)
    return temperature

def get_temperatures(db: Session, city_id: Optional[int] = None) -> List[models.Temperature]:
    query = db.query(models.Temperature)
    if city_id is not None:   # явна перевірка, щоб уникнути проблем із 0
        query = query.filter(models.Temperature.city_id == city_id)
    return query.all()

def bulk_create_temperatures(db: Session, items: List[dict]) -> List[models.Temperature]:
    temps = [
        models.Temperature(
            city_id=item["city_id"],
            temperature=item["temp"],
            date_time=item.get("date_time", datetime.utcnow())
        )
        for item in items
    ]
    db.add_all(temps)
    db.commit()
    for t in temps:
        db.refresh(t)
    return temps

