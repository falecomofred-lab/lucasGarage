"""
API REST para gerenciar carros.

Endpoints:
- GET    /api/cars                    # Listar com filtros
- POST   /api/cars                    # Criar novo
- GET    /api/cars/{id}               # Detalhe
- PUT    /api/cars/{id}               # Atualizar
- DELETE /api/cars/{id}               # Deletar
- POST   /api/cars/{id}/images        # Upload de imagens
"""

from fastapi import APIRouter, Depends, File, UploadFile, Query, HTTPException
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from src.infra.database import get_db
from src.infra.repositories import SQLAlchemyCarRepository
from src.core.entities import Car, CarClass, CarStatus

from pydantic import BaseModel


# ============================================================================
# Schemas
# ============================================================================

class CarResponse(BaseModel):
    id: int
    name: str
    manufacturer_id: int
    category_id: int
    year: int
    color: str
    class_: str
    scale: str
    status: str
    image_urls: Optional[List[str]] = None
    description: Optional[str] = None
    trivia: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CarCreateRequest(BaseModel):
    name: str
    manufacturer_id: int
    category_id: int
    year: int
    color: str
    class_: str
    scale: str = "1:32"
    description: Optional[str] = None
    trivia: Optional[str] = None


class CarUpdateRequest(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    class_: Optional[str] = None
    description: Optional[str] = None
    trivia: Optional[str] = None


# ============================================================================
# Setup
# ============================================================================

router = APIRouter(prefix="/api/cars", tags=["cars"])


# ============================================================================
# GET /api/cars - Listar com filtros
# ============================================================================

@router.get("", response_model=List[CarResponse])
async def list_cars(
    db=Depends(get_db),
    manufacturer_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    class_: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    year_min: Optional[int] = Query(None),
    year_max: Optional[int] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
):
    """Lista carros com filtros opcionais."""
    repo = SQLAlchemyCarRepository(db)
    cars = await repo.get_all()

    if manufacturer_id:
        cars = [c for c in cars if c.manufacturer_id == manufacturer_id]
    if category_id:
        cars = [c for c in cars if c.category_id == category_id]
    if class_:
        cars = [c for c in cars if (c.class_.value if hasattr(c.class_, "value") else c.class_) == class_]
    if color:
        cars = [c for c in cars if c.color and c.color.lower() == color.lower()]
    if year_min:
        cars = [c for c in cars if c.year and c.year >= year_min]
    if year_max:
        cars = [c for c in cars if c.year and c.year <= year_max]

    cars = cars[skip:skip + limit]
    return cars


# ============================================================================
# GET /api/cars/{car_id} - Detalhe
# ============================================================================

@router.get("/{car_id}", response_model=CarResponse)
async def get_car(car_id: int, db=Depends(get_db)):
    """Retorna detalhes de um carro específico"""
    repo = SQLAlchemyCarRepository(db)
    car = await repo.get_by_id(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Carro não encontrado")
    return car


# ============================================================================
# POST /api/cars - Criar novo
# ============================================================================

@router.post("", response_model=CarResponse, status_code=201)
async def create_car(request: CarCreateRequest, db=Depends(get_db)):
    """Cria um novo carro."""
    repo = SQLAlchemyCarRepository(db)
    new_car = Car(
        name=request.name,
        manufacturer_id=request.manufacturer_id,
        category_id=request.category_id,
        year=request.year,
        color=request.color,
        class_=CarClass(request.class_),
        scale=request.scale,
        description=request.description,
        trivia=request.trivia,
        status=CarStatus.DRAFT,
    )
    saved_car = await repo.save(new_car)
    return saved_car


# ============================================================================
# PUT /api/cars/{car_id} - Atualizar
# ============================================================================

@router.put("/{car_id}", response_model=CarResponse)
async def update_car(car_id: int, request: CarUpdateRequest, db=Depends(get_db)):
    """Atualiza dados de um carro"""
    repo = SQLAlchemyCarRepository(db)
    car = await repo.get_by_id(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Carro não encontrado")

    if request.name:
        car.name = request.name
    if request.year:
        car.year = request.year
    if request.color:
        car.color = request.color
    if request.class_:
        car.class_ = CarClass(request.class_)
    if request.description:
        car.description = request.description
    if request.trivia:
        car.trivia = request.trivia

    updated_car = await repo.save(car)
    return updated_car


# ============================================================================
# DELETE /api/cars/{car_id} - Deletar
# ============================================================================

@router.delete("/{car_id}", status_code=204)
async def delete_car(car_id: int, db=Depends(get_db)):
    """Deleta um carro"""
    repo = SQLAlchemyCarRepository(db)
    success = await repo.delete(car_id)
    if not success:
        raise HTTPException(status_code=404, detail="Carro não encontrado")
    return None


# ============================================================================
# POST /api/cars/{car_id}/images - Upload de imagens
# ============================================================================

@router.post("/{car_id}/images")
async def upload_car_images(
    car_id: int,
    files: List[UploadFile] = File(...),
    db=Depends(get_db),
):
    """Upload de imagens para um carro."""
    repo = SQLAlchemyCarRepository(db)
    car = await repo.get_by_id(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Carro não encontrado")

    from src.core.config import settings

    upload_dir = settings.UPLOAD_DIR / str(car_id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    import uuid

    # Só extensões de imagem são aceitas
    EXT_OK = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

    uploaded_urls = []
    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Envie apenas imagens.")

        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="Arquivo muito grande")

        # NUNCA usar o nome que veio no upload (pode conter "../" e escapar
        # da pasta). Geramos um nome próprio e seguro.
        ext = Path(file.filename or "").suffix.lower()
        if ext not in EXT_OK:
            ext = ".jpg"
        nome_seguro = f"car{car_id}_{uuid.uuid4().hex[:12]}{ext}"

        file_path = upload_dir / nome_seguro
        with open(file_path, "wb") as f:
            f.write(content)

        uploaded_urls.append(f"/uploads/{car_id}/{nome_seguro}")

    if not car.image_urls:
        car.image_urls = []
    car.image_urls.extend(uploaded_urls)
    await repo.save(car)

    return {"car_id": car_id, "uploaded_count": len(uploaded_urls), "urls": uploaded_urls}
