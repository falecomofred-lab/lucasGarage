"""
CHECAGEM DE ENDPOINTS - Lucas Garage
Testa todos os endpoints antes da entrega.

Uso:
    1. Deixe o servidor rodando: python -m uvicorn src.main:app --reload
    2. Em OUTRO terminal: python check_endpoints.py
"""

import httpx

BASE = "http://localhost:8000"

# (método, rota, status esperados, descrição)
TESTS = [
    ("GET",  "/health",              [200],      "Health check"),
    ("GET",  "/",                    [200],      "Dashboard (coleção)"),
    ("GET",  "/edit/1",              [200],      "Formulário de edição (carro 1)"),
    ("GET",  "/edit/999",            [200],      "Edição de carro inexistente (form vazio)"),
    ("GET",  "/api/cars",            [200],      "API: listar carros"),
    ("GET",  "/api/cars/1",          [200],      "API: detalhe do carro 1"),
    ("GET",  "/api/cars/99999",      [404],      "API: carro inexistente (404 correto)"),
    ("GET",  "/api/cars?limit=5",    [200],      "API: paginação"),
    ("GET",  "/static/logos",        [200, 301, 307, 404], "Pasta static acessível"),
    ("POST", "/api/identify-photo",  [200, 422], "API: identificação por IA (sem foto = 422)"),
]


def check():
    print("\n" + "=" * 70)
    print("🔍 CHECAGEM DE ENDPOINTS - LUCAS GARAGE")
    print("=" * 70 + "\n")

    ok, fail = 0, 0

    with httpx.Client(timeout=15, follow_redirects=False) as client:
        # Verificar servidor
        try:
            client.get(f"{BASE}/health")
        except httpx.ConnectError:
            print("❌ SERVIDOR NÃO ESTÁ RODANDO!")
            print("   Execute primeiro: python -m uvicorn src.main:app --reload\n")
            return

        for method, route, expected, desc in TESTS:
            try:
                resp = client.request(method, f"{BASE}{route}")
                status = resp.status_code
                passed = status in expected
                icon = "✅" if passed else "❌"
                print(f"{icon} {method:5} {route:28} → {status}  {desc}")
                if passed:
                    ok += 1
                else:
                    fail += 1
                    print(f"      Esperado: {expected}, recebido: {status}")
                    print(f"      Resposta: {resp.text[:150]}")
            except Exception as e:
                fail += 1
                print(f"❌ {method:5} {route:28} → ERRO: {str(e)[:60]}")

        # Teste de salvamento (POST /edit/1)
        print()
        try:
            resp = client.get(f"{BASE}/api/cars/1")
            if resp.status_code == 200:
                car = resp.json()
                form_data = {
                    "name": car.get("name") or "Teste",
                    "manufacturer_id": str(car.get("manufacturer_id") or 1),
                    "category_id": str(car.get("category_id") or 1),
                    "year": str(car.get("year") or 2000),
                    "color": car.get("color") or "Vermelho",
                    "class_": "sports",
                    "scale": "1:32",
                    "status": "draft",
                }
                resp2 = client.post(f"{BASE}/edit/1", data=form_data)
                if resp2.status_code in (303, 200):
                    print(f"✅ POST  /edit/1 (salvar dados)       → {resp2.status_code}  Salvamento funciona!")
                    ok += 1
                else:
                    print(f"❌ POST  /edit/1                      → {resp2.status_code}  Falha ao salvar")
                    fail += 1
        except Exception as e:
            fail += 1
            print(f"❌ POST  /edit/1 → ERRO: {str(e)[:60]}")

    print("\n" + "=" * 70)
    print(f"📊 RESULTADO: {ok} OK · {fail} FALHAS")
    if fail == 0:
        print("🎉 TODOS OS ENDPOINTS FUNCIONANDO — PRONTO PARA ENTREGA!")
    else:
        print("⚠️  Corrija as falhas acima antes de entregar.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    check()
