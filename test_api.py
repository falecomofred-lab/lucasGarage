"""
Script para testar os endpoints da API.

Testa:
1. GET /api/cars - Listar carros
2. GET /api/cars/{id} - Detalhe do carro
3. POST /api/cars - Criar novo carro
4. PUT /api/cars/{id} - Atualizar carro
5. DELETE /api/cars/{id} - Deletar carro

Uso:
    # 1. Inicie o servidor
    uvicorn src.main:app --reload

    # 2. Em outro terminal, rode o teste
    python test_api.py
"""

import httpx
import asyncio
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"


async def test_api():
    """Testa todos os endpoints"""

    async with httpx.AsyncClient() as client:
        print("\n" + "="*60)
        print("🧪 TESTANDO LUCAS GARAGE API")
        print("="*60)

        # 1. GET /api/cars - Listar carros
        print("\n1️⃣  GET /api/cars - Listar carros")
        print("-" * 60)
        response = await client.get(f"{BASE_URL}/api/cars")
        print(f"Status: {response.status_code}")
        cars = response.json()
        print(f"Carros encontrados: {len(cars)}")
        if cars:
            print(f"\nPrimeiro carro:")
            print(json.dumps(cars[0], indent=2, default=str))

        # 2. GET /api/cars/{id} - Se houver carros
        if cars:
            car_id = cars[0]['id']
            print(f"\n2️⃣  GET /api/cars/{car_id} - Detalhe")
            print("-" * 60)
            response = await client.get(f"{BASE_URL}/api/cars/{car_id}")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                car = response.json()
                print(json.dumps(car, indent=2, default=str))

            # 3. PUT /api/cars/{id} - Atualizar
            print(f"\n3️⃣  PUT /api/cars/{car_id} - Atualizar")
            print("-" * 60)
            update_data = {
                "description": "Atualizado via teste de API - " + "Ferrari legend"
            }
            response = await client.put(
                f"{BASE_URL}/api/cars/{car_id}",
                json=update_data
            )
            print(f"Status: {response.status_code}")
            print(json.dumps(response.json(), indent=2, default=str))

        # 4. POST /api/cars - Criar novo
        print(f"\n4️⃣  POST /api/cars - Criar novo carro")
        print("-" * 60)
        new_car = {
            "name": "Test Car via API",
            "manufacturer_id": 1,
            "category_id": 1,
            "year": 2024,
            "color": "Test Red",
            "class_": "sports",
            "description": "Criado via teste de API"
        }
        response = await client.post(
            f"{BASE_URL}/api/cars",
            json=new_car
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            new_car_data = response.json()
            new_car_id = new_car_data['id']
            print(json.dumps(new_car_data, indent=2, default=str))

            # 5. DELETE /api/cars/{id} - Deletar o carro que acabamos de criar
            print(f"\n5️⃣  DELETE /api/cars/{new_car_id} - Deletar carro de teste")
            print("-" * 60)
            response = await client.delete(f"{BASE_URL}/api/cars/{new_car_id}")
            print(f"Status: {response.status_code}")
            if response.status_code == 204:
                print("✅ Carro deletado com sucesso")

        # 6. GET /health - Health check
        print(f"\n6️⃣  GET /health - Health check")
        print("-" * 60)
        response = await client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))

        print("\n" + "="*60)
        print("✅ TESTES CONCLUÍDOS!")
        print("="*60)
        print("\n📚 Endpoints disponíveis:")
        print("  • GET    /api/cars              - Listar carros")
        print("  • POST   /api/cars              - Criar carro")
        print("  • GET    /api/cars/{id}         - Detalhe")
        print("  • PUT    /api/cars/{id}         - Atualizar")
        print("  • DELETE /api/cars/{id}         - Deletar")
        print("  • POST   /api/cars/{id}/images  - Upload de imagens")
        print("  • POST   /api/cars/{id}/identify - OCR")
        print("  • GET    /docs                  - API Swagger")
        print("  • GET    /                      - Dashboard")


if __name__ == "__main__":
    print("\n🚀 Iniciando testes da API...")
    print("Certifique-se de que o servidor está rodando:")
    print("  uvicorn src.main:app --reload\n")

    try:
        asyncio.run(test_api())
    except Exception as e:
        print(f"\n❌ Erro ao testar API: {e}")
        print("\nVerfique se o servidor está rodando em http://localhost:8000")
