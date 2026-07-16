import sys
import os

# Adiciona a raiz do projeto ao sys.path (caminho absoluto)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.entities import Manufacturer, Category
from src.infra.database import SessionLocal
from src.infra.repositories import SQLAlchemyManufacturerRepository, SQLAlchemyCategoryRepository

async def init_data():
    db = SessionLocal()
    mfr_repo = SQLAlchemyManufacturerRepository(db)
    cat_repo = SQLAlchemyCategoryRepository(db)

    manufacturers = ['Ferrari', 'Porsche', 'Lamborghini', 'Ford', 'Chevrolet', 'Bugatti', 'McLaren', 'Mercedes-Benz', 'BMW', 'Audi', 'Jaguar', 'Maserati', 'Aston Martin', 'Koenigsegg', 'Pagani']
    for name in manufacturers:
        await mfr_repo.save(Manufacturer(name=name))

    categories = ['Supercar', 'Sports', 'Classic', 'Muscle', 'Racing', 'Luxury']
    for name in categories:
        await cat_repo.save(Category(name=name))

    db.close()
    print("✅ Fabricantes e categorias criados!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_data())
