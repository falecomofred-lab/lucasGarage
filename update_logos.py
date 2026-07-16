"""
Script para atualizar logos das montadoras usando URLs diretas que funcionam.
Sem necessidade de fazer download - simples URLs públicas!

Uso:
    python update_logos.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.infra.database import SessionLocal, ManufacturerModel

# URLs DIRETAS que funcionam (Wiki Commons, Wikipedia, etc)
LOGO_URLS = {
    "Ferrari": "https://upload.wikimedia.org/wikipedia/en/5/5d/Ferrari_Logo.png",
    "Lamborghini": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Lamborghini_logo.png/220px-Lamborghini_logo.png",
    "Porsche": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Porsche_logo.svg/220px-Porsche_logo.svg.png",
    "Mercedes-Benz": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Mercedes_Benz_Logo_2020.svg/220px-Mercedes_Benz_Logo_2020.svg.png",
    "BMW": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/BMW.svg/220px-BMW.svg.png",
    "Audi": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Audi_Logo.svg/220px-Audi_Logo.svg.png",
    "Volkswagen": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Volkswagen_logo_2019.svg/220px-Volkswagen_logo_2019.svg.png",
    "Ford": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Ford_Motor_Company_Logo.svg/220px-Ford_Motor_Company_Logo.svg.png",
    "Chevrolet": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Chevrolet_logo.svg/220px-Chevrolet_logo.svg.png",
    "Dodge": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Dodge_logo.svg/220px-Dodge_logo.svg.png",
    "Jaguar": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Jaguar_1x1_logo.png/220px-Jaguar_1x1_logo.png",
    "Rolls-Royce": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Rolls-Royce_logo.svg/220px-Rolls-Royce_logo.svg.png",
    "Bentley": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Bentley_Motors_Logo_-_Black.svg/220px-Bentley_Motors_Logo_-_Black.svg.png",
    "Aston Martin": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Aston_Martin_logo.svg/220px-Aston_Martin_logo.svg.png",
    "Bugatti": "https://upload.wikimedia.org/wikipedia/en/thumb/6/6b/Bugatti_logo.svg/220px-Bugatti_logo.svg.png",
    "Maserati": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Maserati_logo.svg/220px-Maserati_logo.svg.png",
    "Toyota": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Toyota_logo_%282019-present%29.svg/220px-Toyota_logo_%282019-present%29.svg.png",
    "Honda": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Honda_logo.svg/220px-Honda_logo.svg.png",
    "Nissan": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Nissan_logo.svg/220px-Nissan_logo.svg.png",
    "Mazda": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Mazda_Motor_Corporation_Logo.svg/220px-Mazda_Motor_Corporation_Logo.svg.png",
    "Suzuki": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Suzuki_Motor_Corporation_logo.svg/220px-Suzuki_Motor_Corporation_logo.svg.png",
    "Subaru": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Subaru_logo.svg/220px-Subaru_logo.svg.png",
    "Mitsubishi": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Mitsubishi_Motors_Logo.svg/220px-Mitsubishi_Motors_Logo.svg.png",
    "McLaren": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/McLaren_automobiles_logo.png/220px-McLaren_automobiles_logo.png",
    "Hyundai": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Hyundai_Motor_Company_logo.svg/220px-Hyundai_Motor_Company_logo.svg.png",
    "Kia": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Kia_logo_%282023%29.svg/220px-Kia_logo_%282023%29.svg.png",
    "Renault": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Renault_logo.svg/220px-Renault_logo.svg.png",
    "Peugeot": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Peugeot_Logo_2020.svg/220px-Peugeot_Logo_2020.svg.png",
    "Volvo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Volvo_logo.svg/220px-Volvo_logo.svg.png",
    "Alfa Romeo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Alfa_Romeo_logo.svg/220px-Alfa_Romeo_logo.svg.png",
    "Lancia": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Lancia_Logo_2010.svg/220px-Lancia_Logo_2010.svg.png",
    "Citroën": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Citro%C3%ABn_logo.svg/220px-Citro%C3%ABn_logo.svg.png",
    "Saab": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Saab_logo.svg/220px-Saab_logo.svg.png",
    "Lotus": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Lotus_Cars_logo.svg/220px-Lotus_Cars_logo.svg.png",
    "Pagani": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Pagani_logo.svg/220px-Pagani_logo.svg.png",
}


def update_logos():
    """Atualiza logos das montadoras com URLs diretas"""

    print("\n" + "="*60)
    print("🖼️  ATUALIZANDO LOGOS DAS MONTADORAS")
    print("="*60 + "\n")

    db = SessionLocal()

    updated = 0
    skipped = 0

    for manufacturer_name, logo_url in LOGO_URLS.items():
        try:
            print(f"🔗 {manufacturer_name:20} ", end="", flush=True)

            # Buscar no banco
            mfr = db.query(ManufacturerModel).filter_by(name=manufacturer_name).first()

            if mfr:
                mfr.logo_url = logo_url
                db.commit()
                print(f"✅ URL salva")
                updated += 1
            else:
                print(f"⚠️  Não encontrada")
                skipped += 1

        except Exception as e:
            print(f"❌ Erro: {str(e)[:40]}")

    db.close()

    print("\n" + "="*60)
    print(f"📊 RESUMO")
    print("="*60)
    print(f"✅ Atualizadas: {updated} logos")
    print(f"⚠️  Não encontradas: {skipped}")
    print("="*60 + "\n")


if __name__ == "__main__":
    update_logos()
    print("✨ Logos atualizadas! Reinicie o servidor para ver as mudanças.")
