# 🔍 AUDITORIA DO CÓDIGO - LUCAS GARAGE

## ❌ ERROS ENCONTRADOS

### 1. **MAIN.PY - Linha 81 (CRÍTICO)**
**Problema:** `car=car or {}`  
Quando o carro não existe, passa um dicionário vazio em vez de um objeto Car.

**Efeito:** Template tenta acessar `car.name`, `car.manufacturer_id`, etc. → **TypeError**

**Solução:** Renderizar um car vazio corretamente ou criar uma classe vazia

---

### 2. **ENTITIES.PY - Linha 46 (AVISO)**
**Problema:** `image_urls: List[str] = None`  
Usar None como padrão para lista é anti-pattern Python.

**Solução:** Usar `field(default_factory=list)` ou deixar o `__post_init__` lidar

---

### 3. **MAIN.PY - Linhas 102-111 (LÓGICA)**
**Problema:** Conversão de Enum pode falhar se form.get retornar None

**Solução:** Adicionar validações e defaults

---

### 4. **TEMPLATE EDIT_CAR.HTML - Linha 58 (LÓGICA)**
**Problema:** Comparação `if car.manufacturer_id == mfr.id` quando car pode não ter atributo

**Solução:** Usar `car.get('manufacturer_id')` ou verificar se car existe

---

### 5. **MAIN.PY - Linha 128 (LÓGICA)**
**Problema:** `await repo.save(car)` espera que car.id já exista para UPDATE

**Solução:** Repositório deve decidir se é INSERT ou UPDATE baseado em car.id

---

## ✅ RECOMENDAÇÕES

1. Validar todos os form.get() antes de usar
2. Tratar Enum corretamente (value vs enum)
3. Usar padrões type-safe no template
4. Adicionar try/except para erros de conversão
5. Logs de debug para salvar dados

