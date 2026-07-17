from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Enum, ForeignKey
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
    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    year = Column(Integer)
    color = Column(String(50))
    scale = Column(String(20), default="1:32")
    class_ = Column(Enum(CarClass), nullable=False)
    description = Column(Text)
    trivia = Column(Text)
    image_urls = Column(Text)  # JSON string
    status = Column(Enum(CarStatus), default=CarStatus.DRAFT)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    # relationships
    manufacturer = relationship("ManufacturerModel", back_populates="cars")
    category = relationship("CategoryModel", back_populates="cars")
    comments = relationship("CommentModel", back_populates="car", cascade="all, delete-orphan")

class CommentModel(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    author_name = Column(String(100), nullable=False)
    author_email = Column(String(100))
    rating = Column(Integer, nullable=False)  # 1-5 estrelas
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    # relationship
    car = relationship("CarModel", back_populates="comments")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
