import sys
import os

# Adiciona a raiz do projeto ao sys.path (caminho absoluto)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import cv2
import numpy as np
from pathlib import Path
import pytesseract
from src.core.config import settings
from src.core.entities import Car, CarClass, CarStatus
from src.infra.database import SessionLocal
from src.infra.repositories import SQLAlchemyCarRepository

# Configuração do Tesseract (ajuste o caminho se necessário)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

MANUFACTURERS = {
    'ferrari': 'Ferrari',
    'porsche': 'Porsche',
    'lamborghini': 'Lamborghini',
    'mustang': 'Ford',
    'camaro': 'Chevrolet',
    'corvette': 'Chevrolet',
    'bugatti': 'Bugatti',
    'mclaren': 'McLaren',
    'mercedes': 'Mercedes-Benz',
    'bmw': 'BMW',
    'audi': 'Audi',
    'jaguar': 'Jaguar',
    'maserati': 'Maserati',
    'aston': 'Aston Martin',
    'koenigsegg': 'Koenigsegg',
    'pagani': 'Pagani',
}

CLASS_MAP = {
    'supercar': CarClass.SUPERCAR,
    'sports': CarClass.SPORTS,
    'classic': CarClass.CLASSIC,
    'muscle': CarClass.MUSCLE,
    'racing': CarClass.RACING,
    'luxury': CarClass.LUXURY,
}

def get_dominant_color(image_path):
    img = cv2.imread(str(image_path))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pixels = img.reshape(-1, 3)
    mask = (pixels > [30, 30, 30]).all(axis=1)
    if np.any(mask):
        pixels = pixels[mask]
    if len(pixels) == 0:
        return "Desconhecida"
    avg = np.mean(pixels, axis=0)
    r, g, b = avg
    if r > g and r > b:
        return "Vermelho"
    elif g > r and g > b:
        return "Verde"
    elif b > r and b > g:
        return "Azul"
    elif r > 150 and g > 150 and b > 150:
        return "Branco"
    elif r < 80 and g < 80 and b < 80:
        return "Preto"
    elif abs(r - g) < 20 and abs(g - b) < 20:
        if r > 150:
            return "Cinza"
        else:
            return "Prata"
    else:
        return "Outra"

def extract_text(image_path):
    # OCR desativado - retorna string vazia
    return ""

def parse_car_info(text, filename, image_path):
    info = {
        'name': None,
        'manufacturer': None,
        'year': None,
        'scale': '1:32',
        'color': None,
        'class_': None,
        'image_url': f"/uploads/{filename}",
    }

    year_match = re.search(r'\b(19[0-9]{2}|20[0-9]{2})\b', text)
    if year_match:
        info['year'] = int(year_match.group())

    scale_match = re.search(r'1[:：]\d{2}', text)
    if scale_match:
        info['scale'] = scale_match.group().replace('：', ':')

    combined = (text + ' ' + filename).lower()
    for key, mfr in MANUFACTURERS.items():
        if key in combined:
            info['manufacturer'] = mfr
            break

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        for line in lines:
            if not re.match(r'^[\d:]+$', line) and len(line) > 3:
                info['name'] = line
                break
    if not info['name']:
        info['name'] = Path(filename).stem.replace('_', ' ').replace('-', ' ')

    info['color'] = get_dominant_color(image_path)

    class_text = text.lower()
    for key, cls in CLASS_MAP.items():
        if key in class_text:
            info['class_'] = cls
            break
    if not info['class_']:
        if info['manufacturer'] in ['Ferrari', 'Lamborghini', 'Bugatti']:
            info['class_'] = CarClass.SUPERCAR
        elif info['manufacturer'] in ['Porsche', 'McLaren']:
            info['class_'] = CarClass.SPORTS
        else:
            info['class_'] = CarClass.CLASSIC

    return info

async def import_images():
    db = SessionLocal()
    repo = SQLAlchemyCarRepository(db)
    upload_dir = settings.UPLOAD_DIR

    extensions = ('.jpg', '.jpeg', '.png', '.webp')
    image_files = [f for f in upload_dir.glob('*') if f.suffix.lower() in extensions]

    print(f"📸 Encontradas {len(image_files)} imagens para processar...")

    for img_path in image_files:
        filename = img_path.name
        print(f"🔍 Processando: {filename}")

        text = extract_text(img_path)
        print(f"   Texto extraído: {text[:100]}...")

        info = parse_car_info(text, filename, img_path)
        print(f"   → Nome: {info['name']}")
        print(f"   → Fabricante: {info['manufacturer']}")
        print(f"   → Ano: {info['year']}")
        print(f"   → Cor: {info['color']}")
        print(f"   → Classe: {info['class_']}")

        car = Car(
            name=info['name'],
            manufacturer_id=1,
            category_id=1,
            year=info['year'] or 2000,
            color=info['color'],
            scale=info['scale'],
            class_=info['class_'],
            description=f"Importado automaticamente da imagem {filename}.",
            image_urls=[info['image_url']],
            status=CarStatus.DRAFT,
        )
        saved = await repo.save(car)
        print(f"✅ Carro #{saved.id} cadastrado: {saved.name}")

    db.close()
    print("🎉 Importação concluída!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(import_images())
