"""
Script para baixar logos das montadoras do Wikimedia Commons
e salvar localmente no projeto.

Uso:
    python download_logos.py
"""

import httpx
import asyncio
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from src.infra.database import SessionLocal
from src.infra.repositories import SQLAlchemyManufacturerRepository

# Diretório para logos
LOGOS_DIR = Path("src/static/logos")
LOGOS_DIR.mkdir(parents=True, exist_ok=True)

# Mapeamento de montadoras para URLs de logos no Wikimedia
LOGO_URLS = {
    "Ferrari": "https://upload.wikimedia.org/wikipedia/en/5/5d/Ferrari_Logo.png",
    "Lamborghini": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Lamborghini_logo.png",
    "Porsche": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Porsche_logo.svg",
    "Mercedes-Benz": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Mercedes_Benz_Logo_2020.svg",
    "BMW": "https://upload.wikimedia.org/wikipedia/commons/4/44/BMW.svg",
    "Audi": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Audi_Logo.svg",
    "Volkswagen": "https://upload.wikimedia.org/wikipedia/commons/6/6d/Volkswagen_logo_2019.svg",
    "Ford": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Ford_Motor_Company_Logo.svg/1024px-Ford_Motor_Company_Logo.svg.png",
    "Chevrolet": "https://upload.wikimedia.org/wikipedia/commons/b/b2/Chevrolet_logo.svg",
    "Dodge": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Dodge_logo.svg",
    "Jaguar": "https://upload.wikimedia.org/wikipedia/commons/a/ab/Jaguar_1x1_logo.png",
    "Rolls-Royce": "https://upload.wikimedia.org/wikipedia/commons/4/48/Rolls-Royce_logo.svg",
    "Bentley": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Bentley_Motors_Logo_-_Black.svg/1024px-Bentley_Motors_Logo_-_Black.svg.png",
    "Aston Martin": "https://upload.wikimedia.org/wikipedia/commons/7/71/Aston_Martin_logo.svg",
    "Bugatti": "https://upload.wikimedia.org/wikipedia/en/thumb/6/6b/Bugatti_logo.svg/1200px-Bugatti_logo.svg.png",
    "Maserati": "https://upload.wikimedia.org/wikipedia/commons/e/e8/Maserati_logo.svg",
    "Toyota": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Toyota_logo_%282019-present%29.svg",
    "Honda": "https://upload.wikimedia.org/wikipedia/commons/7/7a/Honda_logo.svg",
    "Nissan": "https://upload.wikimedia.org/wikipedia/commons/8/8a/Nissan_logo.svg",
    "Mazda": "https://upload.wikimedia.org/wikipedia/commons/b/b5/Mazda_Motor_Corporation_Logo.svg",
    "Suzuki": "https://upload.wikimedia.org/wikipedia/commons/2/24/Suzuki_Motor_Corporation_logo.svg",
    "Subaru": "https://upload.wikimedia.org/wikipedia/commons/9/94/Subaru_logo.svg",
    "Mitsubishi": "https://upload.wikimedia.org/wikipedia/commons/5/50/Mitsubishi_Motors_Logo.svg",
    "McLaren": "https://upload.wikimedia.org/wikipedia/commons/1/18/McLaren_automobiles_logo.png",
    "Hyundai": "https://upload.wikimedia.org/wikipedia/commons/0/0d/Hyundai_Motor_Company_logo.svg",
    "Kia": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Kia_logo_%282023%29.svg",
    "Renault": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Renault_logo.svg",
    "Peugeot": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Peugeot_Logo_2020.svg",
    "Volvo": "https://upload.wikimedia.org/wikipedia/commons/5/50/Volvo_logo.svg",
    "Alfa Romeo": "https://upload.wikimedia.org/wikipedia/commons/2/2e/Alfa_Romeo_logo.svg",
    "Lancia": "https://upload.wikimedia.org/wikipedia/commons/a/a1/Lancia_Logo_2010.svg",
    "Citroën": "https://upload.wikimedia.org/wikipedia/commons/1/1c/Citro%C3%ABn_logo.svg",
    "Saab": "https://upload.wikimedia.org/wikipedia/commons/9/98/Saab_logo.svg",
    "Lotus": "https://upload.wikimedia.org/wikipedia/commons/7/78/Lotus_Cars_logo.svg",
    "Pagani": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Pagani_logo.svg",
}


async def download_logos():
    """Baixa logos e atualiza banco de dados"""

    print("\n" + "="*60)
    print("🖼️  BAIXANDO LOGOS DAS MONTADORAS")
    print("="*60 + "\n")

    db = SessionLocal()
    repo = SQLAlchemyManufacturerRepository(db)

    downloaded = 0
    failed = 0
    skipped = 0

    async with httpx.AsyncClient(timeout=10) as client:
        for manufacturer_name, logo_url in LOGO_URLS.items():
            try:
                print(f"⬇️  {manufacturer_name:20} ", end="", flush=True)

                # Baixar logo
                response = await client.get(logo_url, follow_redirects=True)
                response.raise_for_status()

                # Salvar localmente
                ext = Path(logo_url).suffix or ".png"
                filename = f"{manufacturer_name.lower().replace(' ', '_')}{ext}"
                filepath = LOGOS_DIR / filename
                filepath.write_bytes(response.content)

                # Atualizar banco com URL local
                mfr = await repo.get_by_name(manufacturer_name)
                if mfr:
                    mfr.logo_url = f"/static/logos/{filename}"
                    await repo.save(mfr)
                    print(f"✅ Salvo ({len(response.content)} bytes)")
                    downloaded += 1
                else:
                    print(f"⚠️  Não encontrada no banco")
                    skipped += 1

            except Exception as e:
                print(f"❌ Erro: {str(e)[:40]}")
                failed += 1

    db.close()

    print("\n" + "="*60)
    print(f"📊 RESUMO")
    print("="*60)
    print(f"✅ Baixadas: {downloaded} logos")
    print(f"❌ Falhadas: {failed}")
    print(f"⏭️  Puladas: {skipped} (não no banco)")
    print(f"📁 Diretório: {LOGOS_DIR}")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(download_logos())
    print("✨ Logos baixadas! Reinicie o servidor para ver as mudanças.")
