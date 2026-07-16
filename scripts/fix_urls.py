import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.infra.database import SessionLocal
from src.infra.repositories import SQLAlchemyCarRepository

async def fix_image_urls():
    db = SessionLocal()
    repo = SQLAlchemyCarRepository(db)
    cars = await repo.get_all()
    
    for car in cars:
        if car.image_urls:
            new_urls = []
            for url in car.image_urls:
                # Substitui espaços por _ no caminho da URL
                new_url = url.replace(' ', '_')
                new_urls.append(new_url)
            car.image_urls = new_urls
            await repo.save(car)
            print(f"Atualizado: {car.name}")
    
    db.close()
    print("✅ Caminhos das imagens corrigidos!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(fix_image_urls())
