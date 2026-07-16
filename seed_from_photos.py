"""
🌱 CADASTRO AUTOMÁTICO A PARTIR DAS FOTOS - Lucas Garage

O que este script faz (rodar UMA vez):
1. Garante montadoras e categorias no banco
2. APAGA os carros existentes (limpa qualquer teste antigo)
3. Lê a pasta ./uploads, agrupa as fotos por carro
4. Cria 1 carro por grupo, já com as fotos vinculadas:
     - Nome: provisório ("Carro #N")  → Lucas renomeia depois vendo a foto
     - Montadora: adivinhada pelo nome do arquivo (ou "Outros")
     - Tipo: Classic (padrão) · Ano: em branco · Status: Rascunho

PADRÃO DAS FOTOS (já é o que está na sua pasta):
     nome.jpeg      → foto principal
     nome 2.jpeg    → frente
     nome 3.jpeg    → traseira

COMO USAR:
     python seed_from_photos.py

Depois é só abrir o site: os 83 carros aparecem com as fotos.
Rodar de novo recria tudo do zero (seguro).
"""

import sys, os, re, json
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.infra.database import engine, SessionLocal, Base, CarModel, ManufacturerModel, CategoryModel
from src.core.entities import CarClass, CarStatus

UPLOAD_DIR = Path("uploads")
VALID_EXT = (".jpeg", ".jpg", ".png", ".webp")

# ── Montadoras e categorias (dados reais de referência) ─────────────────────
MANUFACTURERS = [
    "Volkswagen", "Ferrari", "Lamborghini", "Ford", "Chevrolet", "Fiat",
    "Porsche", "BMW", "Mercedes-Benz", "Toyota", "Jaguar", "Nissan",
    "Mitsubishi", "Jeep", "Renault", "Kia", "Hummer", "Aston Martin",
    "Dodge", "Outros",
]
CATEGORIES = [
    ("Supercar", "Carros esportivos de altíssimo desempenho"),
    ("Sports", "Carros esportivos"),
    ("Classic", "Carros clássicos e antigos"),
    ("Muscle", "Muscle cars americanos"),
    ("Racing", "Carros de competição"),
    ("Luxury", "Carros de luxo"),
]

# ── Palpite de montadora pelo nome do arquivo ───────────────────────────────
GUESS_MAP = {
    "Volkswagen": ["fusca", "brasilia", "kombi", "gol", "golf", "santana", "beatle",
                   "puma", "spider", "sprinter", "gordin", "doblo", "voyage", "parati"],
    "Ferrari": ["ferrari"],
    "Lamborghini": ["lamborg"],
    "Ford": ["mustang", "ford", "f1000", "galaxy", "ranger", "corcell", "corcel"],
    "Chevrolet": ["opala", "chevete", "veraneio", "a10", "camelo", "astra", "corsa", "spin", "gurgel"],
    "Fiat": ["147", "uno", "punto", "500", "tl bege"],
    "Porsche": ["porsche"],
    "BMW": ["bmw", "z3", "mini cooper"],
    "Mercedes-Benz": ["mercedes"],
    "Toyota": ["corolla", "hilux", "supra"],
    "Jaguar": ["jaguar"],
    "Nissan": ["skyline"],
    "Mitsubishi": ["lancer"],
    "Jeep": ["jeep", "jimny", "compass", "def", "bugre"],
    "Renault": ["renault"],
    "Kia": ["kia"],
    "Hummer": ["hummer"],
    "Aston Martin": ["aston"],
    "Dodge": ["dodge"],
}


def guess_manufacturer(base: str) -> str:
    b = base.lower()
    for mfr, kws in GUESS_MAP.items():
        if any(k in b for k in kws):
            return mfr
    return "Outros"


def base_slot(stem: str):
    """Separa 'nome 2' -> ('nome', 2); 'nome' -> ('nome', 1)."""
    m = re.match(r"^(.*?)[ ]([123])$", stem)
    return (m.group(1), int(m.group(2))) if m else (stem, 1)


def agrupar_fotos():
    grupos = defaultdict(dict)  # base -> {slot: filename}
    for f in sorted(UPLOAD_DIR.iterdir()):
        if not f.is_file() or f.suffix.lower() not in VALID_EXT:
            continue
        stem = f.stem
        base, slot = base_slot(stem)
        if base == "cocell laranja":       # corrige erro de digitação
            base = "corcell laranja"
        while slot in grupos[base]:        # evita colisão de slot (ex: bmw 25)
            slot += 1
        grupos[base][slot] = f.name

    # junta órfãos (sem principal) cujo nome é prefixo de um carro completo
    principais = {b for b, s in grupos.items() if 1 in s}
    for orb in [b for b, s in list(grupos.items()) if 1 not in s]:
        cand = sorted([p for p in principais if p.startswith(orb + " ")], key=len)
        if cand:
            alvo = cand[0]
            for slot, nome in list(grupos[orb].items()):
                ns = slot
                while ns in grupos[alvo]:
                    ns += 1
                grupos[alvo][ns] = nome
            del grupos[orb]
    return grupos


def seed():
    Base.metadata.create_all(bind=engine)

    if not UPLOAD_DIR.exists():
        print(f"❌ Pasta '{UPLOAD_DIR}' não encontrada.")
        return

    db = SessionLocal()
    try:
        # 1. Montadoras
        mfr_por_nome = {}
        existentes = {m.name: m for m in db.query(ManufacturerModel).all()}
        for name in MANUFACTURERS:
            m = existentes.get(name)
            if not m:
                m = ManufacturerModel(name=name)
                db.add(m)
            mfr_por_nome[name] = m
        db.commit()
        for name, m in mfr_por_nome.items():
            db.refresh(m)

        # 2. Categorias
        cat_existentes = {c.name: c for c in db.query(CategoryModel).all()}
        for name, desc in CATEGORIES:
            if name not in cat_existentes:
                c = CategoryModel(name=name, description=desc)
                db.add(c)
        db.commit()
        cat_classic = db.query(CategoryModel).filter(CategoryModel.name == "Classic").first()

        # 3. Limpa carros antigos
        apagados = db.query(CarModel).delete()
        db.commit()
        print(f"🗑️  {apagados} carro(s) antigo(s) removido(s).")

        # 4. Cria carros a partir das fotos
        grupos = agrupar_fotos()
        criados = 0
        for i, base in enumerate(sorted(grupos), 1):
            slots = grupos[base]
            urls = [f"/uploads/{slots[s]}" for s in sorted(slots)]
            mfr_nome = guess_manufacturer(base)
            carro = CarModel(
                name=f"Carro #{i}",                 # nome provisório
                manufacturer_id=mfr_por_nome[mfr_nome].id,
                category_id=cat_classic.id,
                year=None,
                color=None,
                scale="1:32",
                class_=CarClass.CLASSIC,
                description=None,
                trivia=None,
                image_urls=json.dumps(urls),
                status=CarStatus.DRAFT,
            )
            db.add(carro)
            criados += 1
        db.commit()

        print(f"✅ {criados} carro(s) criado(s) com as fotos vinculadas.")
        print("   Todos como RASCUNHO — abra o site e renomeie/ajuste cada um.")
        print("   Montadora foi adivinhada pelo nome do arquivo (revise se precisar).")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
