"""
Script para inicializar o banco com dados de exemplo.

Executa:
1. Cria tabelas (Alembic)
2. Insere fabricantes
3. Insere categorias
4. Insere carros de exemplo

Uso:
    python init_db.py
"""

import asyncio
import sys
from pathlib import Path

# Adiciona raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.infra.database import Base, engine, SessionLocal
from src.infra.repositories import (
    SQLAlchemyManufacturerRepository,
    SQLAlchemyCategoryRepository,
    SQLAlchemyCarRepository,
)
from src.core.entities import Manufacturer, Category, Car, CarClass, CarStatus


async def init_database():
    """Inicializa banco com dados de exemplo"""

    # 1. Criar tabelas
    print("📦 Criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")

    # 2. Inicializar repositórios
    db = SessionLocal()

    mfr_repo = SQLAlchemyManufacturerRepository(db)
    cat_repo = SQLAlchemyCategoryRepository(db)
    car_repo = SQLAlchemyCarRepository(db)

    try:
        # 3. Verificar se já tem dados
        manufacturers = await mfr_repo.get_all()
        if manufacturers:
            print("⚠️  Banco já tem dados. Pulando inicialização.")
            return

        # 4. Inserir fabricantes
        print("\n🏭 Adicionando fabricantes...")
        manufacturers_data = [
            Manufacturer(
                name="Ferrari",
                country="Italy",
                founded_year=1947,
                logo_url="https://upload.wikimedia.org/wikipedia/en/5/5d/Ferrari_Logo.png"
            ),
            Manufacturer(
                name="Lamborghini",
                country="Italy",
                founded_year=1963,
                logo_url="https://upload.wikimedia.org/wikipedia/commons/f/f7/Lamborghini_logo.png"
            ),
            Manufacturer(
                name="Porsche",
                country="Germany",
                founded_year=1931,
                logo_url="https://upload.wikimedia.org/wikipedia/commons/5/5e/Porsche_logo.svg"
            ),
            Manufacturer(
                name="McLaren",
                country="United Kingdom",
                founded_year=1985,
                logo_url="https://upload.wikimedia.org/wikipedia/en/1/18/McLaren_automobiles_logo.png"
            ),
            Manufacturer(
                name="Bugatti",
                country="France",
                founded_year=1909,
                logo_url="https://upload.wikimedia.org/wikipedia/en/thumb/6/6b/Bugatti_logo.svg/1200px-Bugatti_logo.svg.png"
            ),
        ]

        saved_mfrs = {}
        for mfr_data in manufacturers_data:
            saved = await mfr_repo.save(mfr_data)
            saved_mfrs[mfr_data.name] = saved.id
            print(f"  ✅ {mfr_data.name}")

        # 5. Inserir categorias
        print("\n🏷️  Adicionando categorias...")
        categories_data = [
            Category(
                name="Sports",
                description="High-performance sports cars",
                icon="🏎️"
            ),
            Category(
                name="Supercar",
                description="Extreme performance supercars",
                icon="⚡"
            ),
            Category(
                name="Classic",
                description="Classic and vintage cars",
                icon="👴"
            ),
            Category(
                name="Luxury",
                description="Luxury and grand touring cars",
                icon="👑"
            ),
            Category(
                name="Racing",
                description="Racing and competition cars",
                icon="🏁"
            ),
        ]

        saved_cats = {}
        for cat_data in categories_data:
            saved = await cat_repo.save(cat_data)
            saved_cats[cat_data.name] = saved.id
            print(f"  ✅ {cat_data.name}")

        # 6. Inserir carros de exemplo
        print("\n🚗 Adicionando carros de exemplo...")
        cars_data = [
            Car(
                name="Ferrari F40",
                manufacturer_id=saved_mfrs["Ferrari"],
                category_id=saved_cats["Supercar"],
                year=1987,
                color="Red",
                class_=CarClass.SUPERCAR,
                scale="1:32",
                description="Iconic supercar from the 1980s with V12 engine",
                trivia="The last Ferrari personally approved by Enzo Ferrari"
            ),
            Car(
                name="Lamborghini Countach",
                manufacturer_id=saved_mfrs["Lamborghini"],
                category_id=saved_cats["Supercar"],
                year=1974,
                color="Yellow",
                class_=CarClass.SUPERCAR,
                scale="1:32",
                description="Revolutionary wedge-shaped supercar",
                trivia="Featured in the movie Footloose"
            ),
            Car(
                name="Porsche 911 Carrera RS",
                manufacturer_id=saved_mfrs["Porsche"],
                category_id=saved_cats["Racing"],
                year=1973,
                color="Green",
                class_=CarClass.RACING,
                scale="1:32",
                description="Lightweight high-performance racing version",
                trivia="One of the most sought-after 911 variants"
            ),
            Car(
                name="McLaren F1",
                manufacturer_id=saved_mfrs["McLaren"],
                category_id=saved_cats["Supercar"],
                year=1993,
                color="Orange",
                class_=CarClass.SUPERCAR,
                scale="1:32",
                description="Legendary hypercar with V12 engine and center driver seat",
                trivia="Held the fastest production car record for 16 years"
            ),
            Car(
                name="Bugatti Veyron",
                manufacturer_id=saved_mfrs["Bugatti"],
                category_id=saved_cats["Supercar"],
                year=2005,
                color="Blue",
                class_=CarClass.SUPERCAR,
                scale="1:32",
                description="Modern hypercar with 1001 horsepower",
                trivia="First production car to break 400 km/h"
            ),
        ]

        for car_data in cars_data:
            saved = await car_repo.save(car_data)
            saved.status = CarStatus.PUBLISHED
            await car_repo.save(saved)
            print(f"  ✅ {car_data.name} ({car_data.year})")

        print("\n" + "="*50)
        print("✅ Database initialized successfully!")
        print("="*50)
        print(f"\n📊 Dados carregados:")
        print(f"   • {len(saved_mfrs)} fabricantes")
        print(f"   • {len(saved_cats)} categorias")
        print(f"   • {len(cars_data)} carros de exemplo")
        print(f"\n🚀 Acesse http://localhost:8000/docs para testar a API")

    except Exception as e:
        print(f"\n❌ Erro ao inicializar: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🔧 Inicializando Lucas Garage Database...\n")
    asyncio.run(init_database())
