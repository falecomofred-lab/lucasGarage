# 📤 Enviar o Lucas Garage para o GitHub

Guia rápido em PT-BR. Rode os comandos no **PowerShell** (ou Git Bash), dentro da pasta do projeto.

> ⚠️ O push pede seu **usuário do GitHub** e um **token** (senha não funciona mais).
> Só você digita isso — veja a seção "Token" no final.

---

## 1. Criar o repositório vazio
1. Acesse https://github.com/new
2. Nome: **lucas-garage** · Descrição: *Catálogo premium de miniaturas 1:32 (FastAPI)*
3. Público ou Privado (tanto faz) · **NÃO** marque "Add README"
4. Clique **Create repository**

## 2. Configurar o Git (só na primeira vez)
```powershell
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@gmail.com"
```

## 3. Entrar na pasta do projeto
```powershell
cd "G:\Meu Drive\projetos\lucas_garage"
```

## 4. Inicializar e fazer o primeiro commit
```powershell
git init
git add .
git commit -m "Lucas Garage v1.0"
```

> ✅ A `venv/` e o banco `*.db` **não** sobem (estão no `.gitignore`).
> ✅ As **fotos** em `uploads/` **sobem** (o servidor precisa delas).

## 5. Conectar ao GitHub e enviar
Troque `SEU-USUARIO` pela sua conta:
```powershell
git remote add origin https://github.com/SEU-USUARIO/lucas-garage.git
git branch -M main
git push -u origin main
```

---

## 🔐 Token do GitHub (quando pedir "senha")
1. https://github.com/settings/tokens → **Generate new token (classic)**
2. Nome: `lucas-garage` · Marque **repo** · Gere e **copie**
3. No PowerShell, quando pedir a senha, **cole o token** (ele não aparece na tela — é normal)

---

## 🔄 Próximos envios (depois de mudar algo)
```powershell
cd "G:\Meu Drive\projetos\lucas_garage"
git add .
git commit -m "descrição da mudança"
git push
```

---

## 🆘 Erros comuns
- **`not a git repository`** → você não está na pasta certa; rode o passo 3.
- **`Authentication failed`** → use o **token**, não a senha da conta.
- **`remote origin already exists`** →
  ```powershell
  git remote remove origin
  git remote add origin https://github.com/SEU-USUARIO/lucas-garage.git
  ```
- **push muito grande / demorado** → normal na 1ª vez (as fotos têm ~28 MB).

➡️ Depois que estiver no GitHub, siga o **`DEPLOY_PYTHONANYWHERE.md`** para publicar online.
