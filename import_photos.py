"""
📷 IMPORTAÇÃO DE FOTOS - Lucas Garage

Vincula as fotos da pasta ./uploads aos carros já cadastrados no banco.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMO NOMEAR AS FOTOS (padrão simples):

    <id_do_carro>_<numero>.jpg

Exemplos:
    1_1.jpg   → 1ª foto (principal) do carro de ID 1
    1_2.jpg   → 2ª foto (frente)    do carro de ID 1
    1_3.jpg   → 3ª foto (traseira)  do carro de ID 1
    12_1.png  → 1ª foto do carro de ID 12

Extensões aceitas: .jpg .jpeg .png .webp
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMO USAR:
    1. Coloque as fotos renomeadas dentro da pasta ./uploads
    2. Rode:  python import_photos.py
    3. Recarregue o site — as fotos aparecem nos cards

Rodar de novo é seguro: ele apenas re-vincula o que estiver na pasta.
"""

import sys
import os
import re
import json
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.infra.database import engine, SessionLocal, Base, CarModel

UPLOAD_DIR = Path("uploads")
VALID_EXT = (".jpg", ".jpeg", ".png", ".webp")
# Captura: <id>_<numero>.<ext>
PATTERN = re.compile(r"^(\d+)_(\d+)\.(jpg|jpeg|png|webp)$", re.IGNORECASE)


def import_photos():
    Base.metadata.create_all(bind=engine)

    if not UPLOAD_DIR.exists():
        print(f"❌ Pasta '{UPLOAD_DIR}' não encontrada.")
        return

    # 1. Agrupa arquivos por car_id
    grupos = defaultdict(list)  # car_id -> [(numero, filename), ...]
    ignorados = []
    for f in UPLOAD_DIR.iterdir():
        if not f.is_file():
            continue
        m = PATTERN.match(f.name)
        if m:
            car_id = int(m.group(1))
            numero = int(m.group(2))
            grupos[car_id].append((numero, f.name))
        elif f.suffix.lower() in VALID_EXT:
            ignorados.append(f.name)

    if not grupos:
        print("⚠️  Nenhuma foto no padrão <id>_<numero>.jpg foi encontrada em ./uploads")
        if ignorados:
            print(f"   ({len(ignorados)} arquivo(s) de imagem ignorado(s) por não seguir o padrão)")
        return

    # 2. Atualiza cada carro
    db = SessionLocal()
    try:
        atualizados = 0
        nao_encontrados = []
        for car_id, arquivos in sorted(grupos.items()):
            car = db.query(CarModel).filter(CarModel.id == car_id).first()
            if not car:
                nao_encontrados.append(car_id)
                continue

            arquivos.sort(key=lambda x: x[0])  # ordena pelo número
            urls = [f"/uploads/{nome}" for _, nome in arquivos]
            car.image_urls = json.dumps(urls)
            atualizados += 1
            print(f"✅ Carro #{car_id}: {len(urls)} foto(s) vinculada(s)")

        db.commit()

        print(f"\n🎉 Concluído! {atualizados} carro(s) atualizado(s).")
        if nao_encontrados:
            print(f"⚠️  IDs sem carro no banco (fotos ignoradas): {nao_encontrados}")
        if ignorados:
            print(f"ℹ️  Arquivos fora do padrão (ignorados): {len(ignorados)}")

    finally:
        db.close()


if __name__ == "__main__":
    import_photos()
