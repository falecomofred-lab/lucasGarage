from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from src.core.entities import Car, Manufacturer, Category

class CarRepository(ABC):
    @abstractmethod
    async def save(self, car: Car) -> Car:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Car]:
        pass

    @abstractmethod
    async def get_all(self) -> List[Car]:
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def count(self) -> int:
        pass

    @abstractmethod
    async def count_by_manufacturer(self) -> Dict[str, int]:
        pass

    @abstractmethod
    async def count_by_category(self) -> Dict[str, int]:
        pass

    @abstractmethod
    async def get_recent(self, limit: int = 4) -> List[Car]:
        pass

class ManufacturerRepository(ABC):
    @abstractmethod
    async def save(self, manufacturer: Manufacturer) -> Manufacturer:
        pass

    @abstractmethod
    async def get_all(self) -> List[Manufacturer]:
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Manufacturer]:
        pass

class CategoryRepository(ABC):
    @abstractmethod
    async def save(self, category: Category) -> Category:
        pass

    @abstractmethod
    async def get_all(self) -> List[Category]:
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Category]:
        pass

class AIService(ABC):
    @abstractmethod
    async def identify_car(self, image_bytes: bytes) -> str:
        pass

    @abstractmethod
    async def generate_description(self, car: Car) -> str:
        pass

    @abstractmethod
    async def generate_specs(self, car: Car) -> Dict:
        pass

    @abstractmethod
    async def suggest_category(self, car: Car) -> str:
        pass
