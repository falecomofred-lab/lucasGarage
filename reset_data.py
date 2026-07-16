"""
🧹 RESET DO BANCO DE DADOS - Lucas Garage

O que este script faz:
1. Cria as tabelas (se ainda não existirem)
2. APAGA todos os carros (limpa dados fictícios / de teste)
3. Garante as montadoras e categorias corretas (dados de referência reais)

COMO USAR:
    python reset_data.py

Depois disso, a coleção fica VAZIA e pronta para você cadastrar os carros
de verdade (pelo site em "Novo Carro") ou importar as fotos com import_photos.py.
"""

import sys
import os

# Garante que a raiz do projeto está no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.infra.database import engine, SessionLocal, Base, CarModel, ManufacturerModel, CategoryModel

# ── Dados de referência (reais, não fictícios) ──────────────────────────────
MANUFACTURERS = [
    "Ferrari", "Porsche", "Lamborghini", "Ford", "Chevrolet", "Bugatti",
    "McLaren", "Mercedes-Benz", "BMW", "Audi", "Jaguar", "Maserati",
    "Aston Martin", "Koenigsegg", "Pagani", "Nissan", "Toyota", "Honda",
    "Volkswagen", "Dodge",
]

CATEGORIES = [
    ("Supercar", "Carros esportivos de altíssimo desempenho"),
    ("Sports", "Carros esportivos"),
    ("Classic", "Carros clássicos e antigos"),
    ("Muscle", "Muscle cars americanos"),
    ("Racing", "Carros de competição"),
    ("Luxury", "Carros de luxo"),
]


def reset():
    # 1. Cria tabelas se não existirem
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 2. Apaga TODOS os carros (limpa qualquer dado fictício/antigo)
        deleted = db.query(CarModel).delete()
        db.commit()
        print(f"🗑️  {deleted} carro(s) removido(s) do banco.")

        # 3. Garante montadoras
        existentes = {m.name for m in db.query(ManufacturerModel).all()}
        novas = 0
        for name in MANUFACTURERS:
            if name not in existentes:
                db.add(ManufacturerModel(name=name))
                novas += 1
        db.commit()
        print(f"🏢 Montadoras: {len(MANUFACTURERS)} no total ({novas} nova(s)).")

        # 4. Garante categorias
        cats_existentes = {c.name for c in db.query(CategoryModel).all()}
        novas_cats = 0
        for name, desc in CATEGORIES:
            if name not in cats_existentes:
                db.add(CategoryModel(name=name, description=desc))
                novas_cats += 1
        db.commit()
        print(f"🏷️  Categorias: {len(CATEGORIES)} no total ({novas_cats} nova(s)).")

        print("\n✅ Banco limpo e pronto! A coleção está VAZIA, sem dados fictícios.")
        print("   Cadastre carros pelo site (botão 'Novo Carro') ou use import_photos.py.")

    finally:
        db.close()


if __name__ == "__main__":
    reset()
