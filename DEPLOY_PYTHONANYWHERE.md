# 🚀 Deploy do Lucas Garage no PythonAnywhere

> O Lucas Garage é **FastAPI (ASGI)**. O PythonAnywhere hoje roda ASGI pelo
> **suporte nativo (beta) com uvicorn** — o antigo truque do `a2wsgi` **não funciona**.
> Docs oficiais: https://help.pythonanywhere.com/pages/ASGICommandLine/

---

## Pré-requisito
O código já deve estar no **GitHub** (veja `ENVIAR_GITHUB.txt`), incluindo a pasta
`uploads/` com as fotos (já liberada no `.gitignore`).

---

## Passo a passo

### 1. Console Bash no PythonAnywhere
No painel, abra **Consoles → Bash**.

### 2. Clonar o projeto
```bash
git clone https://github.com/SEU-USUARIO/lucas-garage.git
cd lucas-garage
```

### 3. Criar o ambiente virtual e instalar
```bash
mkvirtualenv --python=/usr/bin/python3.10 lucas
pip install -r requirements.txt
```
(Se `python3.10` não existir, use a versão mais nova que aparecer no painel.)

### 4. Popular o banco com os 83 carros + fotos
```bash
python seed_from_photos.py
```

### 5. Criar o site ASGI (comando único)
Troque **SEU-USUARIO** nos dois lugares:
```bash
pa website create \
  --domain SEU-USUARIO.pythonanywhere.com \
  --command '/home/SEU-USUARIO/.virtualenvs/lucas/bin/uvicorn --app-dir /home/SEU-USUARIO/lucas-garage --uds ${DOMAIN_SOCKET} src.main:app'
```

### 6. Recarregar quando mudar algo
```bash
pa website reload --domain SEU-USUARIO.pythonanywhere.com
```

Pronto: acesse **https://SEU-USUARIO.pythonanywhere.com** 🏎️

---

## Observações importantes

- **Fotos e /static:** o próprio app serve (via StaticFiles), então funcionam mesmo
  sem o mapeamento de estáticos do PythonAnywhere.
- **Banco de dados:** o SQLite fica **no servidor**. A partir do deploy, edite os
  carros **direto no site publicado** (essa passa a ser a versão "de verdade").
  Não rode `seed_from_photos.py` de novo, senão recria tudo como rascunho.
- **Quer levar os carros que você já editou aqui no PC?** Em vez do passo 4, suba o
  arquivo `data/lucas_garage.db` pela aba **Files** do PythonAnywhere (mesma pasta `data/`).
- **Atualizar o código depois:** no console → `cd lucas-garage && git pull` → passo 6 (reload).
