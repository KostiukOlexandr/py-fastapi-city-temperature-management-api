from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional, List
from app import models, schemas
from dateutil import parser

# --- Cities CRUD ---
def create_city(db: Session, city_in: schemas.CityCreate) -> models.City:
    city = models.City(name=city_in.name, additional_info=city_in.additional_info)
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

def get_city_by_id(db: Session, city_id: int) -> Optional[models.City]:
    return db.query(models.City).filter(models.City.id == city_id).first()

def get_city_by_name(db: Session, name: str) -> Optional[models.City]:
    return db.query(models.City).filter(models.City.name == name).first()

def delete_city(db: Session, city_id: int) -> Optional[models.City]:
    city = get_city_by_id(db, city_id)
    if city:
        db.delete(city)
        db.commit()
        return city
    return None

# --- Temperatures CRUD ---
def create_temperature(db: Session, city_id: int, temperature: float, dt: Optional[datetime] = None) -> models.Temperature:
    if dt is None:
        dt = datetime.utcnow()
    temp = models.Temperature(city_id=city_id, temperature=temperature, date_time=dt)
    db.add(temp)
    db.commit()
    db.refresh(temp)
    return temp

def get_temperatures(db: Session) -> List[models.Temperature]:
    return db.query(models.Temperature).all()

def get_temperatures_by_city(db: Session, city_id: int) -> List[models.Temperature]:
    return db.query(models.Temperature).filter(models.Temperature.city_id == city_id).all()

def bulk_create_temperatures(db: Session, items: List[dict]) -> List[models.Temperature]:
    temps = []
    for item in items:
        try:
            # перевірка ключів
            if "city_id" not in item or "temperature" not in item:
                continue

            dt_value = item.get("date_time")
            if isinstance(dt_value, str):
                try:
                    dt_value = parser.parse(dt_value)
                except Exception:
                    # некоректний формат → пропускаємо
                    continue
            elif dt_value is None:
                dt_value = datetime.utcnow()

            temps.append(models.Temperature(
                city_id=item["city_id"],
                temperature=item["temperature"],
                date_time=dt_value
            ))
        except Exception:
            continue

    try:
        db.add_all(temps)
        db.commit()
        for t in temps:
            db.refresh(t)
    except Exception:
        db.rollback()
        raise
    return temps
