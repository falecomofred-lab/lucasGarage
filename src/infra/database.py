from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from src.core.config import settings
from src.core.entities import CarClass, CarStatus
import json

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ManufacturerModel(Base):
    __tablename__ = "manufacturers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    country = Column(String(50))
    founded_year = Column(Integer)
    logo_url = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    # relationship
    cars = relationship("CarModel", back_populates="manufacturer")

class CategoryModel(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    icon = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    # relationship
    cars = relationship("CarModel", back_populates="category")

class CarModel(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    year = Column(Integer, nullable=False)
    color = Column(String(50), nullable=False)
    scale = Column(String(20), default="1:32")
    class_ = Column(Enum(CarClass), nullable=False)
    description = Column(Text)
    trivia = Column(Text)
    image_urls = Column(Text, default="[]")  # JSON string com default
    status = Column(Enum(CarStatus), default=CarStatus.DRAFT)
    # Atributos de batalha manuais (Super Trunfo). Se nulos, são calculados automaticamente.
    velocidade = Column(Integer, nullable=True)
    potencia = Column(Integer, nullable=True)
    # Baralho Super Trunfo: letra do naipe (A, B, C...) e a carta Super Trunfo
    letra = Column(String, nullable=True)
    super_trunfo = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    # relationships
    manufacturer = relationship("ManufacturerModel", back_populates="cars")
    category = relationship("CategoryModel", back_populates="cars")


def ensure_columns():
    """Adiciona colunas novas em bancos SQLite já existentes (migração leve)."""
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            cols = [r[1] for r in conn.execute(text("PRAGMA table_info(cars)")).fetchall()]
            if cols:  # só se a tabela cars já existe
                if "velocidade" not in cols:
                    conn.execute(text("ALTER TABLE cars ADD COLUMN velocidade INTEGER"))
                if "potencia" not in cols:
                    conn.execute(text("ALTER TABLE cars ADD COLUMN potencia INTEGER"))
                if "letra" not in cols:
                    conn.execute(text("ALTER TABLE cars ADD COLUMN letra VARCHAR"))
                if "super_trunfo" not in cols:
                    conn.execute(text("ALTER TABLE cars ADD COLUMN super_trunfo BOOLEAN DEFAULT 0"))
                conn.commit()
    except Exception:
        pass

class RatingModel(Base):
    """Estrela (1 a 5) dada por um amigo do Lucas a um carro."""
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id", ondelete="CASCADE"), index=True, nullable=False)
    stars = Column(Integer, nullable=False)  # 1..5
    created_at = Column(DateTime, server_default=func.now())


class CommentModel(Base):
    """Comentário de um amigo do Lucas em um carro da vitrine."""
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id", ondelete="CASCADE"), index=True, nullable=False)
    author = Column(String(60), default="Anônimo")
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class LikeModel(Base):
    """Curtida (❤️) de um amigo em um carro da vitrine."""
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id", ondelete="CASCADE"), index=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class GameRoomModel(Base):
    """Sala de duelo online do Super Trunfo (estado completo em JSON)."""
    __tablename__ = "game_rooms"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(12), unique=True, index=True, nullable=False)
    data = Column(Text)  # JSON com o estado do jogo
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
