# 🏎️ Lucas Garage

> Catálogo digital premium para miniaturas 1:32 escala com FastAPI, SQLAlchemy e Jinja2

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![FastAPI](https://img.shields.io/badge/fastapi-0.100+-green)

---

## ✨ Funcionalidades

- 🚗 **Catálogo Completo** - 80+ miniaturas premium com dados verídicos
- 📝 **Edição Intuitiva** - Formulário web para atualizar dados de cada carro
- 🖼️ **Logos de Montadoras** - Integração com Wikimedia Commons
- 🏷️ **Classificação** - Por classe (Sports, Classic, Supercar, etc) e categoria
- 📊 **Dashboard** - Visualização de toda a coleção
- 🔍 **Busca & Filtros** - Filtrar por montadora, ano, classe
- ⚡ **API REST** - Endpoints completos para integração (CRUD)
- 🎨 **Interface Moderna** - Tailwind CSS + Design responsivo

---

## 🛠️ Stack Tecnológico

| Componente | Tecnologia |
|-----------|-----------|
| **Backend** | FastAPI (Python 3.10+) |
| **ORM** | SQLAlchemy |
| **Database** | SQLite |
| **Template** | Jinja2 |
| **Frontend** | Tailwind CSS |
| **HTTP Client** | httpx |
| **Images API** | Wikimedia Commons |

---

## 🚀 Como Rodar Localmente

### Pré-requisitos
- Python 3.10+
- Git
- PowerShell ou Terminal

### Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/lucas-garage.git
cd lucas-garage
```

2. **Crie ambiente virtual:**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Instale dependências:**
```bash
pip install -r requirements.txt
```

4. **Inicie o servidor:**
```bash
python -m uvicorn src.main:app --reload
```

5. **Abra no navegador:**
```
http://localhost:8000
```

---

## 📂 Estrutura do Projeto

```
lucas-garage/
│
├── src/
│   ├── core/                          # Regras de negócio
│   │   ├── config.py                 # Configurações
│   │   ├── entities.py               # Modelos (Car, Manufacturer)
│   │   └── interfaces.py             # Interfaces abstrata
│   │
│   ├── infra/                        # Infraestrutura
│   │   ├── database.py              # SQLAlchemy models
│   │   └── repositories.py          # Data access layer
│   │
│   ├── services/                     # Serviços
│   │   ├── ocr_service.py           # OCR (EasyOCR)
│   │   └── manufacturer_image_service.py  # Busca de logos
│   │
│   ├── api/                          # API REST
│   │   └── cars_api.py              # Endpoints CRUD
│   │
│   ├── static/                       # Arquivos estáticos
│   │   └── logos/                   # Logos das montadoras
│   │
│   ├── templates/                    # Templates Jinja2
│   │   ├── base.html                # Layout base
│   │   ├── dashboard.html           # Página principal
│   │   └── pages/
│   │       └── edit_car.html        # Formulário de edição
│   │
│   └── main.py                      # Aplicação principal
│
├── .gitignore                        # Git ignore rules
├── .env.example                      # Exemplo de variáveis
├── requirements.txt                  # Dependências Python
├── README.md                         # Este arquivo
├── GITHUB_SETUP.md                   # Guia GitHub
├── TESTE_CORRECOES.md               # Guia de testes
└── LICENSE                          # Licença MIT
```

---

## 📖 Documentação

### Guias Disponíveis

- **[GITHUB_SETUP.md](./GITHUB_SETUP.md)** - Como enviar para GitHub
- **[TESTE_CORRECOES.md](./TESTE_CORRECOES.md)** - Teste das correções
- **[RESUMO_CORRECOES.txt](./RESUMO_CORRECOES.txt)** - Auditoria e fixes

---

## 🔌 API Endpoints

### Carros (Cars)

```bash
# Listar todos os carros
GET /api/cars

# Obter carro específico
GET /api/cars/{id}

# Criar novo carro
POST /api/cars
Content-Type: application/json
{
  "name": "Ferrari F40",
  "manufacturer_id": 1,
  "category_id": 1,
  "year": 1987,
  "color": "Vermelho",
  "class_": "supercar",
  "scale": "1:32"
}

# Atualizar carro
PUT /api/cars/{id}

# Deletar carro
DELETE /api/cars/{id}
```

### Montadoras (Manufacturers)

```bash
# Listar montadoras
GET /api/manufacturers

# Buscar montadora por nome
GET /api/manufacturers?name=Ferrari
```

### Categorias (Categories)

```bash
# Listar categorias
GET /api/categories
```

---

## 🎯 Funcionalidades em Desenvolvimento

- [x] Catálogo básico
- [x] Formulário de edição
- [x] Logos de montadoras
- [x] API REST (CRUD)
- [x] Validações de dados
- [ ] Autenticação de usuários
- [ ] Upload de imagens
- [ ] Exportar em PDF
- [ ] Relatórios estatísticos
- [ ] Mobile app
- [ ] Integração com APIs de preços

---

## 🐛 Correções Recentes

**v0.2.0** (15/07/2026)
- ✅ Corrigido erro ao salvar carros
- ✅ Validações de formulário
- ✅ Tratamento de erros robusto
- ✅ Logos do Wikimedia Commons

**v0.1.0** (Inicial)
- ✅ Projeto criado
- ✅ API REST funcional
- ✅ Dashboard inicial

---

## 🔐 Segurança

### Boas Práticas

- ✅ Validação de entrada
- ✅ SQL Injection protection (via ORM)
- ✅ Type hints para segurança
- ✅ Error handling robusto

### Variáveis Sensíveis

Use `.env` para variáveis sensíveis (não comitar):

```env
DATABASE_URL=sqlite:///lucas.db
SECRET_KEY=your-secret-key
DEBUG=False
```

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m '✨ Add AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT - veja [LICENSE](./LICENSE) para detalhes.

---

## 👨‍💻 Autor

**Frederico**  
📧 frederico.rep@gmail.com  
🐙 GitHub: [@seu-usuario](https://github.com/seu-usuario)

---

## 🙏 Agradecimentos

- **Wikimedia Commons** - Logos de montadoras
- **FastAPI** - Framework incrível
- **Tailwind CSS** - Styling
- **SQLAlchemy** - ORM poderosa

---

## 📞 Suporte

Encontrou um bug? Tem uma sugestão?

1. Abra uma [Issue](https://github.com/seu-usuario/lucas-garage/issues)
2. Descreva o problema
3. Inclua prints se possível

---

## 🎉 Roadmap

```
2026-Q3: v1.0 (MVP)
- Autenticação
- Upload de imagens
- Exportar PDF

2026-Q4: v1.5
- Mobile app
- Relatórios
- Análise de coleção

2027-Q1: v2.0
- Integração de preços
- Comunidade de colecionadores
- API pública
```

---

<div align="center">

Made with ❤️ para **Lucas Garage** 🏎️

[⬆ Voltar ao topo](#-lucas-garage)

</div>
