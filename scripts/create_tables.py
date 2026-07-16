import sys
import os

# Adiciona a raiz do projeto ao sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infra.database import Base, engine

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")

if __name__ == "__main__":
    create_tables()
