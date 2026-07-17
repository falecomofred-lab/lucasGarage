from fastapi import FastAPI, Depends, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path

# Carregar variáveis do .env (GEMINI_API_KEY, etc) - opcional
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv não instalado - IA por foto fica desativada

from src.core.config import settings
from src.core.logos import get_logo_url
from src.infra.database import get_db
from src.infra.repositories import SQLAlchemyCarRepository
from src.api import cars_router

from jinja2 import Environment, FileSystemLoader, select_autoescape

app = FastAPI(
    title="Lucas Garage",
    version="0.1.0",
    description="Catálogo digital premium para miniaturas 1:32 com OCR automático"
)

# Registrar rotas da API
app.include_router(cars_router)

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Cria ambiente Jinja2 com cache DESABILITADO
jinja_env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    autoescape=select_autoescape(['html', 'xml']),
    cache_size=0
)

@app.get("/")
async def dashboard(request: Request, db=Depends(get_db)):
    from src.infra.repositories import SQLAlchemyManufacturerRepository

    repo = SQLAlchemyCarRepository(db)
    mfr_repo = SQLAlchemyManufacturerRepository(db)

    cars = await repo.get_all()
    manufacturers = await mfr_repo.get_all()

    # Mapa de montadoras por id (para nome + logo nos cards)
    # Logo garantida: banco local > Clearbit > banco externo
    for m in manufacturers:
        m.logo_url = get_logo_url(m.name, m.logo_url)
    mfr_map = {m.id: m for m in manufacturers}

    # Estatísticas da coleção
    total = len(cars)
    published = sum(1 for c in cars if str(c.status.value if hasattr(c.status, 'value') else c.status) == 'published')
    drafts = total - published

    # Collector Score e nível do colecionador
    from src.utils.generators import calculate_score, collector_level, rarity_label
    score_map = {c.id: calculate_score(c) for c in cars}
    rarity_map = {c.id: rarity_label(c) for c in cars}
    total_score = sum(score_map.values())
    level = collector_level(total_score)

    template = jinja_env.get_template("dashboard.html")
    html = template.render(
        request=request,
        cars=sorted(cars, key=lambda c: c.id or 0),
        mfr_map=mfr_map,
        total=total,
        published=published,
        drafts=drafts,
        score_map=score_map,
        rarity_map=rarity_map,
        total_score=total_score,
        level=level
    )
    return HTMLResponse(content=html)


@app.get("/vitrine")
async def vitrine(request: Request, db=Depends(get_db)):
    """Página pública/premium da coleção — feita para o Lucas compartilhar com amigos."""
    from src.infra.repositories import SQLAlchemyManufacturerRepository
    from src.utils.generators import calculate_score, collector_level, rarity_label

    repo = SQLAlchemyCarRepository(db)
    mfr_repo = SQLAlchemyManufacturerRepository(db)

    all_cars = await repo.get_all()
    manufacturers = await mfr_repo.get_all()
    mfr_map = {m.id: m for m in manufacturers}

    # Mostra só os publicados; se nenhum estiver publicado ainda, mostra todos
    def _st(c):
        return c.status.value if hasattr(c.status, "value") else c.status
    publicados = [c for c in all_cars if _st(c) == "published"]
    cars = publicados if publicados else all_cars

    score_map = {c.id: calculate_score(c) for c in all_cars}
    rarity_map = {c.id: rarity_label(c) for c in all_cars}
    total_score = sum(score_map.values())
    level = collector_level(total_score)

    template = jinja_env.get_template("pages/vitrine.html")
    html = template.render(
        request=request,
        cars=sorted(cars, key=lambda c: (score_map.get(c.id, 0)), reverse=True),
        mfr_map=mfr_map,
        score_map=score_map,
        rarity_map=rarity_map,
        total=len(all_cars),
        shown=len(cars),
        total_score=total_score,
        level=level,
    )
    return HTMLResponse(content=html)


@app.get("/car/{car_id}")
async def car_detail(car_id: int, request: Request, db=Depends(get_db)):
    """Card digital premium do carro — com QR Code e compartilhamento."""
    from src.infra.repositories import SQLAlchemyManufacturerRepository
    from src.utils.generators import calculate_score, rarity_label, car_qrcode

    car_repo = SQLAlchemyCarRepository(db)
    mfr_repo = SQLAlchemyManufacturerRepository(db)

    car = await car_repo.get_by_id(car_id)
    if not car:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/", status_code=303)

    manufacturers = await mfr_repo.get_all()
    mfr = next((m for m in manufacturers if m.id == car.manufacturer_id), None)
    mfr_name = mfr.name if mfr else "—"
    logo = get_logo_url(mfr_name, mfr.logo_url if mfr else None) if mfr else None

    images = [u for u in (car.image_urls or []) if u]
    base_url = str(request.base_url).rstrip("/")
    class_val = car.class_.value if hasattr(car.class_, "value") else str(car.class_)

    # Texto do compartilhamento WhatsApp
    share_text = (
        f"🏎️ *{car.name}* ({mfr_name}, {car.year})\n"
        f"⭐ Raridade: {rarity_label(car)} · {calculate_score(car)} pts\n"
        f"🎨 Cor: {car.color}\n"
        f"Veja na minha coleção Lucas Garage: {base_url}/car/{car.id}"
    )

    template = jinja_env.get_template("pages/detail.html")
    html = template.render(
        request=request,
        car=car,
        car_name=car.name,
        mfr_name=mfr_name,
        logo=logo,
        images=images,
        score=calculate_score(car),
        rarity=rarity_label(car),
        class_label=class_val.title(),
        qrcode=car_qrcode(car.id, base_url),
        share_text=share_text,
    )
    return HTMLResponse(content=html)

@app.get("/car/{car_id}/card.png")
async def car_share_card(car_id: int, db=Depends(get_db)):
    """Gera a IMAGEM (PNG) do card para compartilhar no WhatsApp."""
    from fastapi.responses import Response, RedirectResponse
    from src.infra.repositories import SQLAlchemyManufacturerRepository
    from src.utils.generators import calculate_score, rarity_label
    from src.services.card_image import gerar_card

    car_repo = SQLAlchemyCarRepository(db)
    car = await car_repo.get_by_id(car_id)
    if not car:
        return RedirectResponse(url="/", status_code=303)

    mfr_repo = SQLAlchemyManufacturerRepository(db)
    manufacturers = await mfr_repo.get_all()
    mfr = next((m for m in manufacturers if m.id == car.manufacturer_id), None)
    mfr_name = mfr.name if mfr else ""

    # caminho da foto principal
    photo_path = None
    urls = [u for u in (car.image_urls or []) if u]
    if urls and urls[0].startswith("/uploads/"):
        photo_path = Path(settings.UPLOAD_DIR) / urls[0][len("/uploads/"):]

    png = gerar_card(car, mfr_name, calculate_score(car), rarity_label(car), photo_path)
    return Response(content=png, media_type="image/png")


@app.get("/edit/{car_id}")
async def edit_car_page(car_id: int, request: Request, db=Depends(get_db)):
    from src.infra.repositories import SQLAlchemyManufacturerRepository, SQLAlchemyCategoryRepository

    car_repo = SQLAlchemyCarRepository(db)
    mfr_repo = SQLAlchemyManufacturerRepository(db)
    cat_repo = SQLAlchemyCategoryRepository(db)

    car = await car_repo.get_by_id(car_id)
    manufacturers = await mfr_repo.get_all()
    categories = await cat_repo.get_all()
    all_cars = await car_repo.get_all()

    # Logo garantida para todas as montadoras (banco local > Clearbit > externa)
    for m in manufacturers:
        m.logo_url = get_logo_url(m.name, m.logo_url)

    manufacturer_logo = None
    manufacturer_name = None
    if car and car.manufacturer_id:
        mfr = next((m for m in manufacturers if m.id == car.manufacturer_id), None)
        if mfr:
            manufacturer_name = mfr.name
            manufacturer_logo = mfr.logo_url

    # Mapa id -> logo_url para troca dinâmica no front (JavaScript)
    logo_map = {m.id: (m.logo_url or "") for m in manufacturers}

    # Índice do carro
    sorted_cars = sorted(all_cars, key=lambda c: c.id)
    current_index = next((i+1 for i, c in enumerate(sorted_cars) if c.id == car_id), 0)
    total_cars = len(sorted_cars)

    # Próximo carro
    next_car_id = None
    for i, c in enumerate(sorted_cars):
        if c.id == car_id and i < len(sorted_cars) - 1:
            next_car_id = sorted_cars[i+1].id
            break

    # Criar objeto vazio seguro se car não existir
    car_data = car if car else None

    # QR Code do carro (para imprimir e colar na miniatura)
    from src.utils.generators import car_qrcode
    base_url = str(request.base_url).rstrip("/")
    qrcode = car_qrcode(car_id, base_url) if car else None

    template = jinja_env.get_template("pages/edit_car.html")
    html = template.render(
        request=request,
        car=car_data,
        manufacturers=manufacturers,
        categories=categories,
        manufacturer_logo=manufacturer_logo,
        manufacturer_name=manufacturer_name,
        logo_map=logo_map,
        current_index=current_index,
        total_cars=total_cars,
        next_car_id=next_car_id,
        has_car=car is not None,
        saved=request.query_params.get("saved") == "1",
        qrcode=qrcode
    )
    return HTMLResponse(content=html)

@app.post("/edit/{car_id}")
async def save_car(car_id: int, request: Request, db=Depends(get_db)):
    from src.core.entities import CarClass, CarStatus, Car
    from fastapi.responses import RedirectResponse
    import logging

    logger = logging.getLogger(__name__)

    try:
        form = await request.form()
        repo = SQLAlchemyCarRepository(db)

        car = await repo.get_by_id(car_id)

        # Validações básicas
        name = form.get("name", "").strip()
        if not name:
            logger.warning("Campo 'name' vazio")
            return RedirectResponse(url=f"/edit/{car_id}", status_code=303)

        manufacturer_id_str = form.get("manufacturer_id", "").strip()
        category_id_str = form.get("category_id", "").strip()
        year_str = form.get("year", "").strip()
        class_str = form.get("class_", "").strip()

        if not all([manufacturer_id_str, category_id_str, year_str, class_str]):
            logger.warning("Campos obrigatórios vazios")
            return RedirectResponse(url=f"/edit/{car_id}", status_code=303)

        try:
            manufacturer_id = int(manufacturer_id_str)
            category_id = int(category_id_str)
            year = int(year_str)
        except ValueError as e:
            logger.error(f"Erro ao converter valores numéricos: {e}")
            return RedirectResponse(url=f"/edit/{car_id}", status_code=303)

        # Validar classe
        try:
            class_enum = CarClass(class_str)
        except ValueError:
            logger.error(f"Classe inválida: {class_str}")
            return RedirectResponse(url=f"/edit/{car_id}", status_code=303)

        if car:
            # Atualizar existente
            logger.info(f"Atualizando carro {car_id}")
            car.name = name
            car.manufacturer_id = manufacturer_id
            car.category_id = category_id
            car.year = year
            car.color = form.get("color", "").strip()
            car.class_ = class_enum
            car.scale = form.get("scale", "1:32").strip()
            car.description = form.get("description", "").strip() or None
            car.trivia = form.get("trivia", "").strip() or None
            car.status = CarStatus(form.get("status", "draft"))
        else:
            # Criar novo
            logger.info(f"Criando novo carro com id {car_id}")
            car = Car(
                id=car_id,  # Usar car_id fornecido
                name=name,
                manufacturer_id=manufacturer_id,
                category_id=category_id,
                year=year,
                color=form.get("color", "").strip(),
                class_=class_enum,
                scale=form.get("scale", "1:32").strip(),
                description=form.get("description", "").strip() or None,
                trivia=form.get("trivia", "").strip() or None,
                status=CarStatus(form.get("status", "draft"))
            )

        await repo.save(car)
        logger.info(f"Carro {car.id} salvo com sucesso")

        # Volta para a edição com confirmação de salvo
        return RedirectResponse(url=f"/edit/{car.id}?saved=1", status_code=303)

    except Exception as e:
        logger.error(f"Erro ao salvar carro: {e}")
        return RedirectResponse(url=f"/edit/{car_id}", status_code=303)

@app.post("/delete/{car_id}")
async def delete_car_action(car_id: int, db=Depends(get_db)):
    """Exclui um carro da coleção (ação do Lucas na tela de edição)."""
    from fastapi.responses import RedirectResponse
    import logging
    logger = logging.getLogger(__name__)

    repo = SQLAlchemyCarRepository(db)
    ok = await repo.delete(car_id)
    logger.info(f"Carro {car_id} excluído: {ok}")
    return RedirectResponse(url="/", status_code=303)


@app.post("/edit/{car_id}/photos")
async def upload_photos(car_id: int, request: Request, db=Depends(get_db)):
    """Salva as fotos do carro (principal, frente, traseira)."""
    import uuid

    repo = SQLAlchemyCarRepository(db)
    car = await repo.get_by_id(car_id)
    if not car:
        return JSONResponse(content={"error": "Carro não encontrado"}, status_code=404)

    form = await request.form()
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Slots fixos: 0=principal, 1=frente, 2=traseira
    slots = {"photo_main": 0, "photo_front": 1, "photo_rear": 2}
    urls = list(car.image_urls or [])
    while len(urls) < 3:
        urls.append("")

    saved = 0
    for field, index in slots.items():
        file = form.get(field)
        if file and hasattr(file, "filename") and file.filename:
            ext = Path(file.filename).suffix.lower() or ".jpg"
            if ext not in (".jpg", ".jpeg", ".png", ".webp"):
                continue
            filename = f"car{car_id}_{field}_{uuid.uuid4().hex[:8]}{ext}"
            content = await file.read()
            (upload_dir / filename).write_bytes(content)
            urls[index] = f"/uploads/{filename}"
            saved += 1

    car.image_urls = urls
    await repo.save(car)

    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/edit/{car_id}", status_code=303)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
