# 🚀 GUIA: ENVIAR LUCAS GARAGE PARA GITHUB

## ✅ PRÉ-REQUISITOS

1. **Git instalado** no seu PC
   - Teste: `git --version` no PowerShell
   - Se não tiver: https://git-scm.com/download/win

2. **Conta GitHub** (grátis)
   - Acesse: https://github.com/signup

3. **GitHub Desktop** (opcional, mais fácil)
   - Ou use PowerShell/Terminal

---

## 📋 PASSO 1: Criar Repositório no GitHub

1. Acesse: **https://github.com/new**
2. Preencha:
   - **Repository name:** `lucas-garage`
   - **Description:** `Catálogo premium de miniaturas 1:32 com FastAPI`
   - **Public** ou **Private** (sua escolha)
   - ❌ NÃO marque "Add README" (vamos criar)
3. Clique: **"Create repository"**

**Resultado:** Você terá um repositório vazio pronto

---

## 🔧 PASSO 2: Configurar Git Localmente

Abra o **PowerShell** na pasta do projeto:

```powershell
cd "G:\Meu Drive\projetos\lucas_garage"
```

Configure seu nome e email (primeira vez apenas):

```powershell
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@gmail.com"
```

---

## 📝 PASSO 3: Criar .gitignore

Crie arquivo `G:\Meu Drive\projetos\lucas_garage\.gitignore`:

```plaintext
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# SQLite
*.db
*.sqlite
*.sqlite3

# Uploads
uploads/
src/static/logos/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local

# Cache
.cache/
*.cache

# Logs
*.log

# Node (se usar)
node_modules/
package-lock.json

# Misc
.DS_Store
.AppleDouble
.LSOverride
```

---

## 🔌 PASSO 4: Inicializar Repositório Local

```powershell
git init
git add .
git commit -m "🎉 Initial commit: Lucas Garage - Catálogo de miniaturas 1:32"
```

**Esperado:**
```
[main (root-commit) ...] 🎉 Initial commit
 XX files changed, YYYY insertions(+)
```

---

## 🔗 PASSO 5: Conectar ao GitHub

Copie a URL do seu repositório GitHub (exemplo):
```
https://github.com/seu-usuario/lucas-garage.git
```

No PowerShell:

```powershell
git remote add origin https://github.com/seu-usuario/lucas-garage.git
git branch -M main
git push -u origin main
```

**Primeira vez:** Será pedido login do GitHub
- Use seu **nome de usuário** e **token de acesso**
- Se não tiver token: https://github.com/settings/tokens
  - Crie com: `repo`, `workflow`, `user`

---

## ✅ PASSO 6: Verificar no GitHub

1. Acesse seu repositório: `https://github.com/seu-usuario/lucas-garage`
2. Deve aparecer:
   - ✅ Todos os arquivos
   - ✅ `src/`, `TESTE_CORRECOES.md`, etc
   - ✅ Branch `main`

---

## 📝 PASSO 7: Criar README.md

Crie `G:\Meu Drive\projetos\lucas_garage\README.md`:

```markdown
# 🏎️ Lucas Garage

Catálogo digital premium para miniaturas 1:32 com FastAPI, SQLAlchemy e Jinja2.

## ✨ Funcionalidades

- 🚗 Catálogo de 80+ miniaturas premium
- 📝 Edição completa de dados com formulário
- 🖼️ Logos de montadoras (Wikimedia Commons)
- 🏷️ Classificação por classe e categoria
- 📊 Dashboard interativo
- 🔍 Busca e filtros
- ⚡ API REST completa (CRUD)

## 🛠️ Stack Tecnológico

- **Backend:** FastAPI (Python 3.10+)
- **Database:** SQLite + SQLAlchemy ORM
- **Frontend:** Jinja2 Templates + Tailwind CSS
- **Images:** Wikimedia Commons API
- **Styling:** Tailwind CSS

## 🚀 Como Rodar

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/lucas-garage.git
cd lucas-garage
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Instale dependências
```bash
pip install fastapi uvicorn sqlalchemy jinja2 httpx easyocr
```

### 4. Inicie o servidor
```bash
python -m uvicorn src.main:app --reload
```

### 5. Abra no navegador
```
http://localhost:8000
```

## 📂 Estrutura do Projeto

```
lucas-garage/
├── src/
│   ├── core/
│   │   ├── config.py
│   │   ├── entities.py
│   │   └── interfaces.py
│   ├── infra/
│   │   ├── database.py
│   │   └── repositories.py
│   ├── services/
│   │   ├── ocr_service.py
│   │   └── manufacturer_image_service.py
│   ├── api/
│   │   └── cars_api.py
│   ├── static/
│   │   └── logos/
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   └── pages/
│   │       └── edit_car.html
│   └── main.py
├── fetch_manufacturers.py
├── update_logos.py
├── TESTE_CORRECOES.md
├── RESUMO_CORRECOES.txt
└── README.md
```

## 🎯 Próximas Funcionalidades

- [ ] Autenticação de usuários
- [ ] Upload de imagens
- [ ] Exportar catálogo (PDF)
- [ ] Mobile app
- [ ] Integração com APIs de preços

## 📄 Licença

MIT License - Veja LICENSE.md

## 👨‍💻 Autor

**Frederico** - [@frederico.rep](https://github.com/seu-usuario)

---

Made with ❤️ para Lucas Garage 🏎️
```

Salve e faça commit:

```powershell
git add README.md
git commit -m "📚 Add README with project documentation"
git push
```

---

## 🔄 PRÓXIMOS COMMITS (Rotina)

Sempre que fizer mudanças:

```powershell
# Ver o que mudou
git status

# Adicionar arquivos
git add .

# Fazer commit com mensagem descritiva
git commit -m "Descrição breve da mudança"

# Enviar para GitHub
git push
```

### 💡 Boas práticas de commit:

```powershell
# ✅ BOM
git commit -m "✨ Add edit form for car details"
git commit -m "🐛 Fix car save validation errors"
git commit -m "📚 Update README with setup guide"
git commit -m "🚀 Add manufacturer logo support"

# ❌ RUIM
git commit -m "mudancas"
git commit -m "fix"
git commit -m "update"
```

---

## 🔐 PRIVACIDADE & SEGURANÇA

⚠️ **IMPORTANTE:**

1. **Nunca commitar:** `.env`, passwords, tokens
2. Verifique o `.gitignore` cobre tudo sensível
3. Usuários podem ver seu código (público)
4. Para privado: configure repositório como "Private"

---

## 📊 Ver Histórico

```powershell
# Ver commits
git log --oneline

# Ver mudanças em um arquivo
git show <arquivo>

# Ver diferenças
git diff
```

---

## ✅ CHECKLIST FINAL

- [ ] Repositório criado no GitHub
- [ ] `.gitignore` criado locally
- [ ] `git init` executado
- [ ] `git add .` e `git commit` feitos
- [ ] `git remote add origin` configurado
- [ ] `git push` enviou tudo
- [ ] Arquivos aparecem no GitHub.com
- [ ] `README.md` criado
- [ ] Pode ver o repositório público

---

## 🆘 TROUBLESHOOTING

### Erro: "fatal: not a git repository"
```powershell
git init
```

### Erro: "Authentication failed"
1. Gere token: https://github.com/settings/tokens
2. Use token como password

### Erro: "branch 'main' set up to track remote 'origin/main'"
```powershell
git pull origin main
```

### Limpar tudo e recomeçar
```powershell
rm -r .git
git init
git add .
git commit -m "Fresh start"
git remote add origin <URL>
git push -u origin main
```

---

## 🎉 PRONTO!

Seu projeto está no GitHub! 🚀

- Código está versionado
- Histórico de mudanças
- Outros podem colaborar
- Backup automático

**Próximo passo:** Continuar desenvolvendo e fazendo commits regulares!

