from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from src.core.interfaces import CarRepository, ManufacturerRepository, CategoryRepository
from src.core.entities import Car, Manufacturer, Category, CarClass, CarStatus
from src.infra.database import CarModel, ManufacturerModel, CategoryModel
import json

class SQLAlchemyManufacturerRepository(ManufacturerRepository):
    def __init__(self, session: Session):
        self.session = session

    async def save(self, manufacturer: Manufacturer) -> Manufacturer:
        if manufacturer.id:
            # Update
            model = self.session.query(ManufacturerModel).filter(ManufacturerModel.id == manufacturer.id).first()
            if not model:
                raise ValueError(f"Manufacturer with id {manufacturer.id} not found")
            model.name = manufacturer.name
            model.country = manufacturer.country
            model.founded_year = manufacturer.founded_year
            model.logo_url = manufacturer.logo_url
        else:
            # Create
            model = ManufacturerModel(
                name=manufacturer.name,
                country=manufacturer.country,
                founded_year=manufacturer.founded_year,
                logo_url=manufacturer.logo_url,
            )
            self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    async def get_all(self) -> List[Manufacturer]:
        models = self.session.query(ManufacturerModel).all()
        return [self._to_entity(m) for m in models]

    async def get_by_name(self, name: str) -> Optional[Manufacturer]:
        model = self.session.query(ManufacturerModel).filter(ManufacturerModel.name == name).first()
        return self._to_entity(model) if model else None

    def _to_entity(self, model: ManufacturerModel) -> Manufacturer:
        return Manufacturer(
            name=model.name,
            id=model.id,
            country=model.country,
            founded_year=model.founded_year,
            logo_url=model.logo_url,
        )

class SQLAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, session: Session):
        self.session = session

    async def save(self, category: Category) -> Category:
        if category.id:
            # Update
            model = self.session.query(CategoryModel).filter(CategoryModel.id == category.id).first()
            if not model:
                raise ValueError(f"Category with id {category.id} not found")
            model.name = category.name
            model.description = category.description
            model.icon = category.icon
        else:
            # Create
            model = CategoryModel(
                name=category.name,
                description=category.description,
                icon=category.icon,
            )
            self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    async def get_all(self) -> List[Category]:
        models = self.session.query(CategoryModel).all()
        return [self._to_entity(m) for m in models]

    async def get_by_name(self, name: str) -> Optional[Category]:
        model = self.session.query(CategoryModel).filter(CategoryModel.name == name).first()
        return self._to_entity(model) if model else None

    def _to_entity(self, model: CategoryModel) -> Category:
        return Category(
            name=model.name,
            id=model.id,
            description=model.description,
            icon=model.icon,
        )

class SQLAlchemyCarRepository(CarRepository):
    def __init__(self, session: Session):
        self.session = session

    async def save(self, car: Car) -> Car:
        if car.id:
            # Update
            car_model = self.session.query(CarModel).filter(CarModel.id == car.id).first()
            if not car_model:
                raise ValueError(f"Car with id {car.id} not found")
            car_model.name = car.name
            car_model.manufacturer_id = car.manufacturer_id
            car_model.category_id = car.category_id
            car_model.year = car.year
            car_model.color = car.color
            car_model.scale = car.scale
            car_model.class_ = car.class_
            car_model.description = car.description
            car_model.trivia = car.trivia
            car_model.image_urls = json.dumps(car.image_urls)
            car_model.status = car.status
            car_model.velocidade = car.velocidade
            car_model.potencia = car.potencia
            car_model.letra = car.letra
            car_model.super_trunfo = car.super_trunfo
            car_model.produzidos = car.produzidos
            car_model.peso = car.peso
        else:
            # Create
            car_model = CarModel(
                name=car.name,
                manufacturer_id=car.manufacturer_id,
                category_id=car.category_id,
                year=car.year,
                color=car.color,
                scale=car.scale,
                class_=car.class_,
                description=car.description,
                trivia=car.trivia,
                image_urls=json.dumps(car.image_urls),
                status=car.status,
                velocidade=car.velocidade,
                potencia=car.potencia,
                letra=car.letra,
                super_trunfo=car.super_trunfo,
                produzidos=car.produzidos,
                peso=car.peso,
            )
            self.session.add(car_model)
        self.session.commit()
        self.session.refresh(car_model)
        return self._to_entity(car_model)

    async def get_by_id(self, id: int) -> Optional[Car]:
        car_model = self.session.query(CarModel).filter(CarModel.id == id).first()
        return self._to_entity(car_model) if car_model else None

    async def get_all(self) -> List[Car]:
        car_models = self.session.query(CarModel).all()
        return [self._to_entity(c) for c in car_models]

    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        manufacturer: Optional[str] = None,
        category: Optional[str] = None,
        year: Optional[int] = None,
        class_: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Car]:
        query = self.session.query(CarModel)
        if manufacturer:
            query = query.join(CarModel.manufacturer).filter(ManufacturerModel.name == manufacturer)
        if category:
            query = query.join(CarModel.category).filter(CategoryModel.name == category)
        if year:
            query = query.filter(CarModel.year == year)
        if class_:
            query = query.filter(CarModel.class_ == class_)
        if search:
            query = query.filter(or_(CarModel.name.ilike(f"%{search}%"), CarModel.description.ilike(f"%{search}%")))
        car_models = query.offset(skip).limit(limit).all()
        return [self._to_entity(c) for c in car_models]

    async def count(self) -> int:
        return self.session.query(CarModel).count()

    async def count_by_manufacturer(self) -> Dict[str, int]:
        result = self.session.query(ManufacturerModel.name, func.count(CarModel.id))\
            .join(CarModel.manufacturer).group_by(ManufacturerModel.name).all()
        return {r[0]: r[1] for r in result}

    async def count_by_category(self) -> Dict[str, int]:
        result = self.session.query(CategoryModel.name, func.count(CarModel.id))\
            .join(CarModel.category).group_by(CategoryModel.name).all()
        return {r[0]: r[1] for r in result}

    async def get_recent(self, limit: int = 4) -> List[Car]:
        car_models = self.session.query(CarModel).order_by(CarModel.created_at.desc()).limit(limit).all()
        return [self._to_entity(c) for c in car_models]

    async def delete(self, id: int) -> bool:
        car_model = self.session.query(CarModel).filter(CarModel.id == id).first()
        if not car_model:
            return False
        self.session.delete(car_model)
        self.session.commit()
        return True

    def _to_entity(self, model: CarModel) -> Car:
        return Car(
            name=model.name,
            manufacturer_id=model.manufacturer_id,
            category_id=model.category_id,
            year=model.year,
            color=model.color,
            class_=model.class_,
            id=model.id,
            scale=model.scale,
            description=model.description,
            trivia=model.trivia,
            image_urls=json.loads(model.image_urls) if model.image_urls else [],
            status=model.status,
            velocidade=getattr(model, "velocidade", None),
            potencia=getattr(model, "potencia", None),
            letra=getattr(model, "letra", None),
            super_trunfo=bool(getattr(model, "super_trunfo", False)),
            produzidos=getattr(model, "produzidos", None),
            peso=getattr(model, "peso", None),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
