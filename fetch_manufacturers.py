"""
Script para buscar TODAS as montadoras e suas logos/imagens públicas.

Uso:
    python fetch_manufacturers.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.infra.database import SessionLocal
from src.infra.repositories import (
    SQLAlchemyManufacturerRepository,
)
from src.core.entities import Manufacturer
from src.services.manufacturer_image_service import ManufacturerImageService


# Lista completa de montadoras mundiais
MANUFACTURERS = [
    # Italianas
    ("Ferrari", "Italy", 1947),
    ("Lamborghini", "Italy", 1963),
    ("Maserati", "Italy", 1914),
    ("Alfa Romeo", "Italy", 1910),
    ("Lancia", "Italy", 1906),
    ("Pagani", "Italy", 1992),

    # Alemãs
    ("Porsche", "Germany", 1931),
    ("BMW", "Germany", 1916),
    ("Mercedes-Benz", "Germany", 1926),
    ("Audi", "Germany", 1910),
    ("Volkswagen", "Germany", 1937),
    ("Opel", "Germany", 1862),
    ("Maybach", "Germany", 1909),
    ("Gullwing", "Germany", 1992),

    # Britânicas
    ("McLaren", "United Kingdom", 1985),
    ("Jaguar", "United Kingdom", 1922),
    ("Rolls-Royce", "United Kingdom", 1906),
    ("Bentley", "United Kingdom", 1919),
    ("Aston Martin", "United Kingdom", 1913),
    ("Lotus", "United Kingdom", 1948),
    ("MG", "United Kingdom", 1924),
    ("Austin", "United Kingdom", 1905),

    # Francesas
    ("Bugatti", "France", 1909),
    ("Renault", "France", 1898),
    ("Peugeot", "France", 1882),
    ("Citroën", "France", 1919),
    ("Alpine", "France", 1955),

    # Americanas
    ("Ford", "United States", 1903),
    ("Chevrolet", "United States", 1911),
    ("Dodge", "United States", 1900),
    ("Plymouth", "United States", 1928),
    ("Pontiac", "United States", 1926),
    ("Oldsmobile", "United States", 1897),
    ("Cadillac", "United States", 1902),
    ("Corvette", "United States", 1953),
    ("Muscle Cars", "United States", 1960),
    ("Shelby", "United States", 1962),
    ("Hummer", "United States", 1992),

    # Suecas
    ("Volvo", "Sweden", 1927),
    ("Saab", "Sweden", 1947),
    ("Koenigsegg", "Sweden", 1994),

    # Suíça
    ("Bugatti", "Switzerland", 1909),

    # Japonesas
    ("Toyota", "Japan", 1937),
    ("Nissan", "Japan", 1933),
    ("Honda", "Japan", 1949),
    ("Mazda", "Japan", 1920),
    ("Suzuki", "Japan", 1909),
    ("Mitsubishi", "Japan", 1970),
    ("Subaru", "Japan", 1953),
    ("Daihatsu", "Japan", 1907),
    ("Isuzu", "Japan", 1937),
    ("Lexus", "Japan", 1989),
    ("Acura", "Japan", 1986),
    ("Infiniti", "Japan", 1989),

    # Coreanas
    ("Hyundai", "South Korea", 1967),
    ("Kia", "South Korea", 1944),
    ("Daewoo", "South Korea", 1982),
    ("Samsung", "South Korea", 1938),

    # Espanholas
    ("Seat", "Spain", 1950),
    ("Caterham", "Spain", 1973),

    # Australiana
    ("Holden", "Australia", 1856),
    ("FPV", "Australia", 1998),

    # Indianas
    ("Tata", "India", 1945),
    ("Mahindra", "India", 1945),

    # Tailandesa
    ("Isuzu", "Thailand", 1937),
]


async def fetch_all_manufacturers():
    """Busca todas as montadoras e suas imagens"""

    db = SessionLocal()
    repo = SQLAlchemyManufacturerRepository(db)
    image_service = ManufacturerImageService()

    print("\n" + "="*60)
    print("🌍 BUSCANDO MONTADORAS E LOGOS")
    print("="*60 + "\n")

    # Verificar quais já existem
    existing = await repo.get_all()
    existing_names = {m.name.lower() for m in existing}

    added = 0
    skipped = 0

    for name, country, year in MANUFACTURERS:
        try:
            # Verificar se já existe
            if name.lower() in existing_names:
                print(f"⏭️  {name:25} (já existe)")
                skipped += 1
                continue

            # Buscar imagens/logos
            print(f"🔍 {name:25} ", end="", flush=True)
            images = await image_service.fetch_images(name, "logo", year)

            logo_url = images[0].url if images else None

            # Adicionar ao banco
            mfr = Manufacturer(
                name=name,
                country=country,
                founded_year=year,
                logo_url=logo_url
            )

            await repo.save(mfr)

            status = "✅" if logo_url else "⚠️"
            print(f"{status} Logo encontrado" if logo_url else f"{status} Sem logo")
            added += 1

        except Exception as e:
            print(f"❌ Erro: {str(e)[:40]}")

    db.close()

    print("\n" + "="*60)
    print(f"📊 RESUMO")
    print("="*60)
    print(f"✅ Adicionadas: {added} montadoras")
    print(f"⏭️  Puladas: {skipped} (já existiam)")
    print(f"📈 Total no banco: {added + skipped}")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("⏳ Isso pode levar alguns minutos (busca de logos)...\n")
    asyncio.run(fetch_all_manufacturers())
    print("✨ Pronto! Montadoras adicionadas ao banco de dados.")
