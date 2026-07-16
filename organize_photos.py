"""
ORGANIZADOR DE FOTOS - Lucas Garage

O que faz:
1. Lê todas as fotos do WhatsApp na pasta uploads/
2. Ordena por data/hora (ordem em que foram tiradas)
3. Agrupa de 3 em 3: principal, frente, traseira
4. Renomeia para: car01_main.jpeg, car01_front.jpeg, car01_rear.jpeg...
5. Vincula ao carro correspondente no banco de dados

Uso:
    python organize_photos.py           (simula, não altera nada)
    python organize_photos.py --run     (executa de verdade)
"""

import re
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.infra.database import SessionLocal, CarModel

UPLOADS = Path("uploads")
FOTOS_POR_CARRO = 3  # principal, frente, traseira
SLOTS = ["main", "front", "rear"]

DRY_RUN = "--run" not in sys.argv


def sort_key(path: Path):
    """Extrai (data, hora, índice) do nome WhatsApp para ordenar cronologicamente."""
    name = path.name.replace("_", " ")
    # WhatsApp Image 2026-07-15 at 14.06.04 (1).jpeg
    m = re.search(r"(\d{4}-\d{2}-\d{2}) at (\d{2}\.\d{2}\.\d{2})(?:\s*\((\d+)\))?", name)
    if m:
        date, time, idx = m.group(1), m.group(2), int(m.group(3) or 0)
        return (date, time, idx)
    return ("9999", name, 0)


def main():
    print("\n" + "=" * 64)
    print("📷 ORGANIZADOR DE FOTOS - LUCAS GARAGE")
    if DRY_RUN:
        print("   MODO SIMULAÇÃO (nada será alterado)")
        print("   Para executar de verdade: python organize_photos.py --run")
    print("=" * 64 + "\n")

    # 1. Coletar fotos do WhatsApp
    photos = sorted(
        [p for p in UPLOADS.glob("*.jp*g") if "whatsapp" in p.name.lower()],
        key=sort_key
    )
    print(f"📁 Fotos do WhatsApp encontradas: {len(photos)}")

    if not photos:
        print("❌ Nenhuma foto encontrada em uploads/")
        return

    # 2. Carros do banco (ordenados por ID)
    db = SessionLocal()
    cars = db.query(CarModel).order_by(CarModel.id).all()
    print(f"🚗 Carros no banco: {len(cars)}")

    grupos = len(photos) // FOTOS_POR_CARRO
    print(f"📦 Grupos de {FOTOS_POR_CARRO} fotos: {grupos}")
    sobra = len(photos) % FOTOS_POR_CARRO
    if sobra:
        print(f"⚠️  Sobram {sobra} foto(s) no final (ficam sem vínculo)")
    print()

    # 3. Atribuir
    vinculados = 0
    for i, car in enumerate(cars):
        start = i * FOTOS_POR_CARRO
        group = photos[start:start + FOTOS_POR_CARRO]
        if not group:
            break

        urls = []
        for j, photo in enumerate(group):
            slot = SLOTS[j]
            new_name = f"car{car.id:02d}_{slot}{photo.suffix.lower()}"
            new_path = UPLOADS / new_name
            urls.append(f"/uploads/{new_name}")

            print(f"  🚗 Carro #{car.id:02d} [{slot:5}] ← {photo.name[:50]}")

            if not DRY_RUN:
                if new_path.exists():
                    new_path.unlink()
                photo.rename(new_path)

        if not DRY_RUN:
            car.image_urls = json.dumps(urls)
            vinculados += 1

    if not DRY_RUN:
        db.commit()
    db.close()

    print("\n" + "=" * 64)
    if DRY_RUN:
        print("✅ SIMULAÇÃO OK! Se a ordem acima estiver correta, execute:")
        print("   python organize_photos.py --run")
    else:
        print(f"✅ CONCLUÍDO! {vinculados} carros com fotos vinculadas.")
        print("   Reinicie o servidor e veja o dashboard!")
    print("=" * 64 + "\n")


if __name__ == "__main__":
    main()
