"""
Publica TODAS as cartas de uma vez (tira do rascunho).

Roda tanto no seu PC quanto no PythonAnywhere — não usa internet.

  Ver quantas mudariam, sem gravar:
      python publicar_todas.py

  Publicar de verdade:
      python publicar_todas.py --gravar
"""

import sys

from src.infra.database import SessionLocal, CarModel, Base, engine


def main():
    gravar = "--gravar" in sys.argv
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        total = db.query(CarModel).count()
        rascunhos = [c for c in db.query(CarModel).all()
                     if str(getattr(c.status, "value", c.status)) != "published"]

        print("=" * 60)
        print("Total de cartas no banco: %d" % total)
        print("Ainda em rascunho:        %d" % len(rascunhos))
        print("=" * 60)

        if not rascunhos:
            print("\nTodas já estão publicadas. Nada a fazer.")
            return

        for c in rascunhos[:15]:
            print("  · %s (id %s)" % (c.name, c.id))
        if len(rascunhos) > 15:
            print("  ... e mais %d" % (len(rascunhos) - 15))

        if gravar:
            from src.core.entities import CarStatus
            for c in rascunhos:
                c.status = CarStatus.PUBLISHED
            db.commit()
            print("\n✅ %d cartas publicadas. Todas as %d aparecem na vitrine." % (len(rascunhos), total))
        else:
            print("\n(simulação — rode com --gravar para publicar)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
