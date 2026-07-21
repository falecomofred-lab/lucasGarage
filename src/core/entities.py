from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class CarClass(str, Enum):
    SPORTS = "sports"
    CLASSIC = "classic"
    SUPERCAR = "supercar"
    MUSCLE = "muscle"
    RACING = "racing"
    LUXURY = "luxury"

class CarStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

@dataclass
class Manufacturer:
    name: str
    id: Optional[int] = None
    country: Optional[str] = None
    founded_year: Optional[int] = None
    logo_url: Optional[str] = None

@dataclass
class Category:
    name: str
    id: Optional[int] = None
    description: Optional[str] = None
    icon: Optional[str] = None

@dataclass
class Car:
    name: str
    manufacturer_id: int
    category_id: int
    year: int
    color: str
    class_: CarClass
    id: Optional[int] = None
    scale: str = "1:32"
    description: Optional[str] = None
    trivia: Optional[str] = None
    image_urls: List[str] = field(default_factory=list)
    status: CarStatus = CarStatus.DRAFT
    velocidade: Optional[int] = None
    potencia: Optional[int] = None
    letra: Optional[str] = None
    super_trunfo: bool = False
    produzidos: Optional[int] = None     # unidades fabricadas
    peso: Optional[int] = None           # kg
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def is_published(self) -> bool:
        return self.status == CarStatus.PUBLISHED

    @property
    def preview_image(self) -> Optional[str]:
        return self.image_urls[0] if self.image_urls else None
