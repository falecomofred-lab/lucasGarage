# ⚡ QUICK START - Lucas Garage

**Pronto para rodar em 5 minutos!**

---

## 🚀 Passo 1: Instalar Dependências

```bash
# Abra terminal na pasta do projeto
cd G:\Meu Drive\projetos\lucas_garage

# Instale as dependências
pip install -r requirements.txt
```

**Tempo esperado:** 2-3 minutos  
**Nota:** EasyOCR fará download de modelos (~200MB) na primeira execução.

---

## 📦 Passo 2: Inicializar Banco de Dados

```bash
# Cria tabelas e carrega dados de exemplo
python init_db.py
```

**Resultado esperado:**
```
✅ Database initialized successfully!

📊 Dados carregados:
   • 5 fabricantes (Ferrari, Lamborghini, Porsche, McLaren, Bugatti)
   • 5 categorias (Sports, Supercar, Classic, Luxury, Racing)
   • 5 carros de exemplo
```

---

## 🎯 Passo 3: Iniciar o Servidor

```bash
# Inicie o servidor FastAPI
uvicorn src.main:app --reload
```

**Resultado esperado:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Acesse:**
- 🌐 Dashboard: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs
- 🔍 OpenAPI JSON: http://localhost:8000/openapi.json

---

## 🧪 Passo 4: Testar a API

**Abra outro terminal** e rode:

```bash
python test_api.py
```

**Testa:**
- ✅ Listar carros
- ✅ Criar novo carro
- ✅ Atualizar carro
- ✅ Deletar carro
- ✅ Health check

---

## 🎮 Testando Endpoints (via Swagger)

Abra: **http://localhost:8000/docs**

### Exemplo 1: Listar Carros
```
GET /api/cars
```

### Exemplo 2: Criar Novo Carro
```
POST /api/cars
Content-Type: application/json

{
  "name": "Meu Carro",
  "manufacturer_id": 1,
  "category_id": 1,
  "year": 2024,
  "color": "Red",
  "class_": "sports"
}
```

### Exemplo 3: Upload de Imagem
```
POST /api/cars/1/images
Content-Type: multipart/form-data
file: [escolher arquivo .jpg]
```

### Exemplo 4: OCR - Identificar Carro
```
POST /api/cars/1/identify
Content-Type: multipart/form-data
file: [foto da miniatura]
```

---

## 📁 Estrutura Final

```
lucas_garage/
├── src/
│   ├── api/
│   │   ├── __init__.py          ✅ INTEGRADO
│   │   └── cars_api.py          ✅ NOVO
│   ├── services/
│   │   ├── __init__.py          ✅ NOVO
│   │   ├── ocr_service.py       ✅ NOVO
│   │   └── manufacturer_image_service.py ✅ NOVO
│   ├── core/
│   ├── infra/
│   ├── templates/
│   ├── static/
│   └── main.py                  ✅ ATUALIZADO
├── init_db.py                   ✅ NOVO
├── test_api.py                  ✅ NOVO
├── requirements.txt             ✅ NOVO
├── QUICKSTART.md                ✅ NOVO (este arquivo)
├── ANALISE_PROFUNDA.md          📊 Análise completa
├── SETUP_GUIA.md                📖 Detalhes de setup
└── ROADMAP_VISUAL.md            🗺️  Timeline de implementação
```

---

## ✨ O que Funciona Agora

### ✅ API REST Completa
- `GET /api/cars` - Listar com filtros
- `POST /api/cars` - Criar novo
- `GET /api/cars/{id}` - Detalhe
- `PUT /api/cars/{id}` - Atualizar
- `DELETE /api/cars/{id}` - Deletar

### ✅ Upload e Processamento
- `POST /api/cars/{id}/images` - Upload de imagens
- `POST /api/cars/{id}/identify` - OCR automático

### ✅ Funcionalidades Backend
- OCR com EasyOCR (identifica carros em fotos)
- Busca de imagens públicas (Wikimedia Commons)
- Cache automático de imagens
- API documentada com Swagger

### ✅ Dashboard
- Homepage com grid de carros
- Preview de imagens
- Informações de cada miniatura

---

## 🎓 Como Usar OCR

### 1. Upload Manual + OCR
```bash
# Terminal 1: Servidor rodando
uvicorn src.main:app --reload

# Terminal 2: Teste
curl -X POST "http://localhost:8000/api/cars/1/identify" \
  -F "file=@/caminho/para/imagem.jpg"
```

### 2. Via Python
```python
import asyncio
from src.services.ocr_service import CarOCRService

async def test():
    service = CarOCRService()
    result = await service.identify_car("uploads/exemplo.jpg")
    
    print(f"Modelo: {result.model_name}")
    print(f"Confiança: {result.confidence:.1%}")

asyncio.run(test())
```

### 3. Via Swagger
1. Abra http://localhost:8000/docs
2. Vá para `POST /api/cars/{car_id}/identify`
3. Escolha um car_id (ex: 1)
4. Escolha uma foto
5. Execute

---

## 🐛 Troubleshooting

### Erro: `ModuleNotFoundError: No module named 'easyocr'`
```bash
pip install easyocr
```

### Erro: `Port 8000 already in use`
```bash
# Use outra porta
uvicorn src.main:app --port 8001
```

### Erro: `Database is locked`
```bash
# Feche todas as conexões
# Ou delete o banco e crie novamente
rm data/lucas_garage.db
python init_db.py
```

### OCR muito lento
- Esperado na primeira execução (download de modelos)
- Subsequentes são mais rápidas
- GPU aceleraria mais (requer CUDA)

---

## 📊 Dados de Exemplo

Após rodar `init_db.py`, você tem:

**Fabricantes:**
- Ferrari (1947)
- Lamborghini (1963)
- Porsche (1931)
- McLaren (1985)
- Bugatti (1909)

**Categorias:**
- Sports
- Supercar
- Classic
- Luxury
- Racing

**Carros (5 de exemplo):**
- Ferrari F40 (1987) 🔴
- Lamborghini Countach (1974) 🟡
- Porsche 911 Carrera RS (1973) 🟢
- McLaren F1 (1993) 🟠
- Bugatti Veyron (2005) 🔵

---

## 🔄 Próximos Passos

### Imediato (Agora)
- [x] Instalar dependências
- [x] Inicializar banco
- [x] Rodar servidor
- [x] Testar endpoints

### Curtíssimo Prazo (Hoje)
- [ ] Explorar endpoints via Swagger
- [ ] Fazer upload de uma imagem
- [ ] Testar OCR
- [ ] Adicionar seus próprios carros

### Curto Prazo (Esta semana)
- [ ] Implementar mais validações
- [ ] Adicionar testes unitários
- [ ] Melhorar interface do dashboard
- [ ] Documentar API

### Médio Prazo (Próximas 2-3 semanas)
- [ ] ElasticSearch para busca avançada
- [ ] Sistema de tags automáticas
- [ ] Dashboard com estatísticas
- [ ] Cache com Redis

---

## 📚 Documentação

| Arquivo | Conteúdo |
|---------|----------|
| `QUICKSTART.md` | **Você está aqui** - Setup rápido |
| `SETUP_GUIA.md` | Detalhes completos de setup |
| `ANALISE_PROFUNDA.md` | Análise estratégica do projeto |
| `ROADMAP_VISUAL.md` | Timeline e arquitetura futura |

---

## 💡 Dicas Rápidas

### Para Ver Logs Detalhados
```bash
uvicorn src.main:app --reload --log-level debug
```

### Para Limpar Uploads
```bash
# Windows
rmdir /s uploads\temp
rmdir /s uploads\temp_batch

# Linux/Mac
rm -rf uploads/temp uploads/temp_batch
```

### Para Resetar Banco
```bash
# Delete o banco
rm data/lucas_garage.db

# Recrie
python init_db.py
```

---

## ✅ Checklist de Conclusão

- [x] **Análise Profunda** concluída
- [x] **Serviço OCR** implementado
- [x] **Serviço de Imagens** implementado  
- [x] **API REST** implementada
- [x] **Banco de Dados** integrado
- [x] **Dados de Exemplo** carregados
- [x] **Testes** configurados
- [x] **Documentação** completa

---

## 🎉 Pronto!

Você agora tem um **Catálogo Premium Inteligente** funcionando!

```bash
# Resumindo os 3 passos principais:

1️⃣  pip install -r requirements.txt
2️⃣  python init_db.py
3️⃣  uvicorn src.main:app --reload

# Então abra:
# 🌐 http://localhost:8000
# 📚 http://localhost:8000/docs
```

**Qualquer dúvida, consulte:**
- `ANALISE_PROFUNDA.md` para arquitetura
- `SETUP_GUIA.md` para detalhes
- `ROADMAP_VISUAL.md` para futuro
- Comentários no código (docstrings)

---

**Bem-vindo ao Lucas Garage! 🚗✨**

Agora você tem uma base sólida para continuar melhorando. Basta seguir o roadmap!
