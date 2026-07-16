import sys
import os
import base64
import json
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import settings
from src.core.entities import Car, CarClass, CarStatus
from src.infra.database import SessionLocal
from src.infra.repositories import SQLAlchemyCarRepository

# ============================================================
# CONFIGURAÇÃO DA IA (OpenAI)
# ============================================================
# Instale: pip install openai
from openai import OpenAI

# Coloque sua chave aqui ou em uma variável de ambiente
OPENAI_API_KEY = "sua-chave-aqui"  # OU use os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Prompt para a IA
PROMPT = """
Você é um especialista em carros antigos e miniaturas. Analise a imagem e extraia as seguintes informações no formato JSON:

{
  "marca": "marca do carro",
  "modelo": "modelo específico",
  "ano": "ano aproximado (ex: 1972)",
  "cor": "cor principal",
  "classe": "uma das seguintes: 'supercar', 'sports', 'classic', 'muscle', 'racing', 'luxury'",
  "escala": "escala da miniatura (ex: 1:32)",
  "potencia": "potência aproximada em cv (opcional, pode ser vazio)",
  "pais": "país de origem (opcional)",
  "tipo": "tipo de carroceria (ex: sedan, perua, cupê)"
}

Retorne APENAS o JSON, sem texto adicional. Se não tiver certeza de algum campo, use null.
"""

# ============================================================
# FUNÇÕES
# ============================================================
def encode_image(image_path):
    """Codifica a imagem para base64."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def identify_car(image_path):
    """Envia a imagem para a IA e retorna o JSON."""
    base64_image = encode_image(image_path)
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # ou "gpt-4o" se tiver acesso
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                    ],
                }
            ],
            max_tokens=500,
            temperature=0.0,
        )
        content = response.choices[0].message.content
        # Limpa o JSON (caso a IA retorne com marcadores)
        if "`json" in content:
            content = content.split("`json")[1].split("`")[0]
        elif "`" in content:
            content = content.split("`")[1].split("`")[0]
        return json.loads(content.strip())
    except Exception as e:
        print(f"❌ Erro ao processar {image_path}: {e}")
        return None

def update_car(car_id, data, db):
    """Atualiza um carro no banco com os dados da IA."""
    repo = SQLAlchemyCarRepository(db)
    car = await repo.get_by_id(car_id)
    if not car:
        print(f"Carro {car_id} não encontrado.")
        return
    # Atualiza campos
    if data.get("marca"):
        # Precisamos do ID do fabricante - vamos buscar ou criar
        mfr_repo = SQLAlchemyManufacturerRepository(db)
        mfr = await mfr_repo.get_by_name(data["marca"])
        if not mfr:
            mfr = await mfr_repo.save(Manufacturer(name=data["marca"]))
        car.manufacturer_id = mfr.id
    if data.get("modelo"):
        car.name = data["modelo"]
    if data.get("ano"):
        car.year = int(data["ano"]) if data["ano"] else car.year
    if data.get("cor"):
        car.color = data["cor"]
    if data.get("classe"):
        # Mapeia string para enum
        class_map = {
            "supercar": CarClass.SUPERCAR,
            "sports": CarClass.SPORTS,
            "classic": CarClass.CLASSIC,
            "muscle": CarClass.MUSCLE,
            "racing": CarClass.RACING,
            "luxury": CarClass.LUXURY,
        }
        car.class_ = class_map.get(data["classe"].lower(), car.class_)
    if data.get("escala"):
        car.scale = data["escala"]
    if data.get("potencia"):
        car.trivia = (car.trivia or "") + f"\nPotência: {data['potencia']}"
    if data.get("pais"):
        car.description = (car.description or "") + f"\nPaís: {data['pais']}"
    if data.get("tipo"):
        car.description = (car.description or "") + f"\nTipo: {data['tipo']}"
    # Salva
    await repo.save(car)
    print(f"✅ Carro {car.id} atualizado: {car.name}")

async def main():
    db = SessionLocal()
    repo = SQLAlchemyCarRepository(db)
    cars = await repo.get_all()

    # Filtra apenas carros que ainda não têm nome definido (opcional)
    # ou processa todos.
    for car in cars:
        # Pula se já tiver um nome decente (ex: não começa com "WhatsApp")
        if car.name and not car.name.startswith("WhatsApp"):
            print(f"⏭️ Pulando {car.name} (já nomeado)")
            continue
        # Pega a primeira imagem
        if not car.image_urls:
            print(f"⏭️ Carro {car.id} sem imagem.")
            continue
        img_url = car.image_urls[0]
        # Converte URL (ex: /uploads/... ) para caminho no disco
        img_path = settings.UPLOAD_DIR / Path(img_url).name
        if not img_path.exists():
            print(f"⏭️ Arquivo não encontrado: {img_path}")
            continue
        print(f"🔍 Processando {img_path.name}...")
        data = identify_car(img_path)
        if data:
            print(f"   → Dados recebidos: {data}")
            await update_car(car.id, data, db)
        else:
            print(f"   ⚠️ Falha na identificação.")
    db.close()
    print("🎉 Atualização concluída!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
