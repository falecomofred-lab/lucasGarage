"""
Adiciona um catálogo grande de montadoras ao banco, sem duplicar.

Rode uma vez:      python seed_montadoras.py
Pode rodar de novo — ele só insere o que ainda não existe.

Todas as marcas abaixo têm logo confirmado no car-logos-dataset,
então o selo aparece automaticamente no card.
"""

from src.infra.database import SessionLocal, ManufacturerModel, Base, engine

MONTADORAS = [
    # ── Italianas ──
    ("Ferrari", "Itália"), ("Lamborghini", "Itália"), ("Maserati", "Itália"),
    ("Alfa Romeo", "Itália"), ("Fiat", "Itália"), ("Pagani", "Itália"),
    ("Bugatti", "França"), ("Lancia", "Itália"), ("Abarth", "Itália"),
    ("De Tomaso", "Itália"), ("Bizzarrini", "Itália"), ("Iso", "Itália"),

    # ── Alemãs ──
    ("Porsche", "Alemanha"), ("BMW", "Alemanha"), ("Mercedes-Benz", "Alemanha"),
    ("Audi", "Alemanha"), ("Volkswagen", "Alemanha"), ("Opel", "Alemanha"),
    ("Maybach", "Alemanha"), ("Smart", "Alemanha"), ("Wiesmann", "Alemanha"),

    # ── Britânicas ──
    ("Aston Martin", "Reino Unido"), ("Jaguar", "Reino Unido"),
    ("Bentley", "Reino Unido"), ("Rolls-Royce", "Reino Unido"),
    ("McLaren", "Reino Unido"), ("Land Rover", "Reino Unido"),
    ("Mini", "Reino Unido"), ("Lotus", "Reino Unido"), ("Morgan", "Reino Unido"),
    ("Caterham", "Reino Unido"), ("TVR", "Reino Unido"), ("Noble", "Reino Unido"),
    ("Vauxhall", "Reino Unido"), ("MG", "Reino Unido"), ("Triumph", "Reino Unido"),
    ("Austin", "Reino Unido"), ("Morris", "Reino Unido"), ("Jensen", "Reino Unido"),
    ("Ginetta", "Reino Unido"), ("Ariel", "Reino Unido"), ("Bristol", "Reino Unido"),

    # ── Americanas ──
    ("Ford", "EUA"), ("Chevrolet", "EUA"), ("Dodge", "EUA"),
    ("Cadillac", "EUA"), ("Chrysler", "EUA"), ("Buick", "EUA"),
    ("Pontiac", "EUA"), ("GMC", "EUA"), ("Lincoln", "EUA"),
    ("Jeep", "EUA"), ("Hummer", "EUA"), ("Tesla", "EUA"),
    ("RAM", "EUA"), ("Rivian", "EUA"), ("Plymouth", "EUA"),
    ("Oldsmobile", "EUA"), ("Mercury", "EUA"), ("Saturn", "EUA"),
    ("AMC", "EUA"), ("Studebaker", "EUA"), ("Packard", "EUA"),
    ("Hudson", "EUA"), ("DeSoto", "EUA"), ("Saleen", "EUA"),
    ("Hennessey", "EUA"), ("Panoz", "EUA"), ("Fisker", "EUA"),

    # ── Japonesas ──
    ("Toyota", "Japão"), ("Honda", "Japão"), ("Nissan", "Japão"),
    ("Mazda", "Japão"), ("Mitsubishi", "Japão"), ("Subaru", "Japão"),
    ("Suzuki", "Japão"), ("Lexus", "Japão"), ("Acura", "Japão"),
    ("Infiniti", "Japão"), ("Datsun", "Japão"), ("Daihatsu", "Japão"),
    ("Isuzu", "Japão"), ("Scion", "Japão"),

    # ── Coreanas e chinesas ──
    ("Hyundai", "Coreia do Sul"), ("Kia", "Coreia do Sul"),
    ("Genesis", "Coreia do Sul"), ("SsangYong", "Coreia do Sul"),
    ("BYD", "China"), ("Chery", "China"), ("Geely", "China"),
    ("Great Wall", "China"),

    # ── Francesas e outras europeias ──
    ("Renault", "França"), ("Peugeot", "França"), ("Citroën", "França"),
    ("Alpine", "França"), ("Venturi", "França"), ("Talbot", "França"),
    ("Simca", "França"), ("Volvo", "Suécia"), ("Saab", "Suécia"),
    ("Koenigsegg", "Suécia"), ("Polestar", "Suécia"), ("Seat", "Espanha"),
    ("Skoda", "Tchéquia"), ("Dacia", "Romênia"), ("Spyker", "Holanda"),

    # ── Outras ──
    ("Holden", "Austrália"), ("Tata", "Índia"), ("Troller", "Brasil"),
    ("Outros", None),
]


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    criadas, existentes = 0, 0
    try:
        for nome, pais in MONTADORAS:
            achou = db.query(ManufacturerModel).filter(
                ManufacturerModel.name.ilike(nome)
            ).first()
            if achou:
                existentes += 1
                continue
            db.add(ManufacturerModel(name=nome, country=pais))
            criadas += 1
        db.commit()
    finally:
        db.close()

    print(f"✅ {criadas} montadoras novas adicionadas")
    print(f"↩️  {existentes} já existiam (nada duplicado)")
    print(f"📋 Total no catálogo: {criadas + existentes}")
    print("\nO Lucas já pode escolher qualquer uma na lista do editor.")


if __name__ == "__main__":
    main()
