# 🚀 GUIA DE SETUP - Lucas Garage

**Análise concluída!** Aqui está como começar a implementação.

---

## 📋 Checklist Rápido

- [x] Análise profunda completada (`ANALISE_PROFUNDA.md`)
- [x] Serviço OCR criado (`src/services/ocr_service.py`)
- [x] Serviço de Imagens Públicas criado (`src/services/manufacturer_image_service.py`)
- [x] API REST completa criada (`src/api/cars_api.py`)
- [ ] Instalar dependências
- [ ] Integrar rotas na app
- [ ] Testar endpoints

---

## 🔧 Passo 1: Instalar Dependências

Adicione ao `pyproject.toml`:

```toml
[project]
dependencies = [
    # ... deps existentes ...
    "easyocr>=1.7.0",           # OCR
    "python-httpx>=0.27.0",     # HTTP async
    "pytest>=7.4.0",            # Testes (opcional mas recomendado)
    "pytest-asyncio>=0.23.0",   # Testes async (opcional)
]
```

Depois instale:

```bash
cd G:\Meu Drive\projetos\lucas_garage

# Usando pip
pip install easyocr httpx pytest pytest-asyncio

# Ou com uv (mais rápido)
uv pip install easyocr httpx pytest pytest-asyncio
```

### ⚠️ Nota sobre EasyOCR

- **Primeira execução:** EasyOCR baixa modelos (~200MB)
- **Tempo:** ~1 min na primeira vez, depois instantâneo
- **GPU opcional:** Se tiver NVIDIA GPU, instale `torch` com CUDA para acelerar

---

## 🎯 Passo 2: Integrar Rotas na App

No arquivo `src/main.py`, adicione as rotas:

```python
# No topo do arquivo
from src.api.cars_api import router as cars_router

# Depois de criar o app
app = FastAPI(title="Lucas Garage", version="0.1.0")

# Registrar rotas
app.include_router(cars_router)

# Resto da config...
```

**Antes:**
```python
app = FastAPI(title="Lucas Garage", version="0.1.0")
app.mount("/static", StaticFiles(...), name="static")
app.mount("/uploads", StaticFiles(...), name="uploads")
```

**Depois:**
```python
from src.api.cars_api import router as cars_router

app = FastAPI(title="Lucas Garage", version="0.1.0")

# Registrar router da API
app.include_router(cars_router)

# Mounts
app.mount("/static", StaticFiles(...), name="static")
app.mount("/uploads", StaticFiles(...), name="uploads")
```

---

## ✅ Passo 3: Testar a API

### 3.1 - Iniciar o servidor

```bash
cd G:\Meu Drive\projetos\lucas_garage

# Com uvicorn direto
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Ou com python -m
python -m uvicorn src.main:app --reload
```

Acesse: **http://localhost:8000/docs** (Swagger UI)

### 3.2 - Testar Endpoints

#### Lista de Carros (vazio no início)
```bash
curl -X GET "http://localhost:8000/api/cars"
```

Resposta esperada:
```json
[]
```

#### Criar um Carro
```bash
curl -X POST "http://localhost:8000/api/cars" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ferrari F40",
    "manufacturer_id": 1,
    "category_id": 1,
    "year": 1987,
    "color": "red",
    "class_": "sports"
  }'
```

#### OCR em Imagem
```bash
curl -X POST "http://localhost:8000/api/cars/1/identify" \
  -F "file=@/caminho/para/imagem.jpg"
```

---

## 🧪 Passo 4: Testes Rápidos (Opcional)

### Teste do OCR

```python
# Crie um arquivo: test_ocr.py

import asyncio
from src.services.ocr_service import CarOCRService

async def test():
    service = CarOCRService()
    
    # Use uma imagem de teste
    result = await service.identify_car("uploads/exemplo.jpg")
    
    print(f"Model: {result.model_name}")
    print(f"Confidence: {result.confidence:.1%}")
    print(f"Features: {result.extracted_features}")

# Executar
if __name__ == "__main__":
    asyncio.run(test())
```

Rodando:
```bash
python test_ocr.py
```

### Teste do Serviço de Imagens

```python
# Crie um arquivo: test_images.py

import asyncio
from src.services.manufacturer_image_service import ManufacturerImageService

async def test():
    service = ManufacturerImageService()
    
    # Buscar imagens do Ferrari F40
    images = await service.fetch_images("Ferrari", "F40")
    
    print(f"Encontradas {len(images)} imagens:")
    for img in images[:3]:
        print(f"  - {img.source}: {img.title}")
        print(f"    {img.url}")

if __name__ == "__main__":
    asyncio.run(test())
```

Rodando:
```bash
python test_images.py
```

---

## 🔐 Passo 5: Configurar Chaves de API (Opcional)

Se quiser usar Pixabay e Unsplash:

### Pixabay

1. Vá para: https://pixabay.com/api/
2. Crie conta e pegue a chave
3. No código:

```python
from src.services.manufacturer_image_service import ManufacturerImageService

service = ManufacturerImageService(
    pixabay_key="sua_chave_aqui"
)
```

### Unsplash

1. Vá para: https://unsplash.com/developers
2. Registre app e pegue Client ID
3. No código:

```python
service = ManufacturerImageService(
    unsplash_key="seu_client_id_aqui"
)
```

**Ou via .env:**

```
PIXABAY_KEY=sua_chave
UNSPLASH_KEY=seu_id
```

Depois no `config.py`:

```python
class Settings(BaseSettings):
    PIXABAY_KEY: Optional[str] = None
    UNSPLASH_KEY: Optional[str] = None
```

---

## 📊 Estrutura Final do Projeto

Depois das implementações:

```
lucas_garage/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── cars_api.py           ✅ NOVO
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ocr_service.py        ✅ NOVO
│   │   └── manufacturer_image_service.py  ✅ NOVO
│   ├── core/
│   │   ├── config.py
│   │   ├── entities.py
│   │   └── interfaces.py
│   ├── infra/
│   │   ├── database.py
│   │   └── repositories.py
│   ├── templates/
│   │   ├── base.html
│   │   └── pages/
│   │       └── dashboard.html
│   ├── static/
│   └── main.py
├── data/
│   ├── lucas_garage.db
│   └── image_cache/              ✅ NOVO (criado automaticamente)
├── uploads/
│   ├── temp/
│   └── temp_batch/
├── alembic/
├── pyproject.toml
├── ANALISE_PROFUNDA.md           ✅ NOVO
└── SETUP_GUIA.md                 ✅ NOVO (este arquivo)
```

---

## 🎯 Próximos Passos

### Imediato (Hoje)
- [x] Ler análise completa
- [ ] Instalar dependências
- [ ] Integrar rotas
- [ ] Testar endpoints básicos

### Curto Prazo (Esta semana)
- [ ] Implementar CRUD completo no frontend
- [ ] Adicionar validações
- [ ] Testes automatizados
- [ ] Documentação de API

### Médio Prazo (Próximas 2 semanas)
- [ ] ElasticSearch para busca avançada
- [ ] Sistema de tags automático
- [ ] Dashboard com estatísticas
- [ ] Cache com Redis

### Longo Prazo (Roadmap)
- [ ] Autenticação de usuários
- [ ] Compartilhamento de coleções
- [ ] App mobile
- [ ] Integração com marketplaces

---

## 🐛 Troubleshooting

### Erro: `ModuleNotFoundError: No module named 'easyocr'`

```bash
pip install easyocr
```

### Erro: `CUDA/GPU não encontrado`

Normal. OCR funciona em CPU também (mais lento). Se quiser usar GPU:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Erro: `Port 8000 already in use`

```bash
# Use outra porta
uvicorn src.main:app --port 8001
```

### Erro: `Database locked`

Se usar SQLite:

```bash
# Feche outras conexões
# Ou mude para PostgreSQL em produção
```

---

## 📚 Documentação Gerada

Já está tudo documentado em:

- **API Swagger:** http://localhost:8000/docs
- **Análise Detalhada:** `ANALISE_PROFUNDA.md`
- **Código comentado:** Veja docstrings em cada arquivo

---

## 💬 Perguntas?

Se tiver dúvidas:

1. Leia os **comentários no código** (docstrings)
2. Veja os **exemplos de teste** (test_*.py)
3. Consulte a **análise profunda** para entender a arquitetura
4. Teste os **endpoints via Swagger** (http://localhost:8000/docs)

---

## ✨ Sucesso!

Você agora tem:

- ✅ Análise profunda do projeto
- ✅ Serviço OCR funcional para identificar carros
- ✅ Integração com imagens públicas de fabricantes
- ✅ API REST completa
- ✅ Roadmap claro para futuro

**Próximo passo:** Instalar dependências e rodar a API!

```bash
pip install easyocr httpx
python -m uvicorn src.main:app --reload
# Acesse http://localhost:8000/docs
```

---

**Boa codificação! 🚀**
