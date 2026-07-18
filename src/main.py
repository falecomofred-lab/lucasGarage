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

# Garante que todas as tabelas existam (inclui ratings e comments)
from src.infra.database import Base, engine
Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Cria ambiente Jinja2 com cache DESABILITADO
jinja_env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    autoescape=select_autoescape(['html', 'xml']),
    cache_size=0
)

# ══════════════ LOGIN SIMPLES (protege o painel do Lucas) ══════════════
import hmac, hashlib
from fastapi.responses import RedirectResponse

AUTH_COOKIE = "lg_auth"

def _auth_token() -> str:
    return hmac.new(settings.SECRET_KEY.encode(), b"lucas-garage-authed", hashlib.sha256).hexdigest()

def is_authed(request: Request) -> bool:
    return request.cookies.get(AUTH_COOKIE) == _auth_token()

def _needs_login(request: Request):
    """Se não estiver logado, devolve um redirect para /login; senão None."""
    if not is_authed(request):
        return RedirectResponse(url="/login", status_code=303)
    return None


@app.get("/login")
async def login_page(request: Request):
    template = jinja_env.get_template("pages/login.html")
    erro = request.query_params.get("erro") == "1"
    return HTMLResponse(template.render(request=request, erro=erro))


@app.post("/login")
async def do_login(request: Request):
    form = await request.form()
    senha = (form.get("password", "") or "").strip()
    if senha == settings.DASHBOARD_PASSWORD:
        resp = RedirectResponse(url="/", status_code=303)
        resp.set_cookie(AUTH_COOKIE, _auth_token(), httponly=True,
                        max_age=60 * 60 * 24 * 30, samesite="lax")
        return resp
    return RedirectResponse(url="/login?erro=1", status_code=303)


@app.get("/logout")
async def logout():
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie(AUTH_COOKIE)
    return resp


@app.get("/")
async def dashboard(request: Request, db=Depends(get_db)):
    guard = _needs_login(request)
    if guard:
        return guard

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

    # Montadoras que têm carros (para o filtro no topo)
    filter_mfrs = sorted({
        (mfr_map[c.manufacturer_id].name if c.manufacturer_id in mfr_map else "Outros")
        for c in cars
    })

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
        level=level,
        filter_mfrs=filter_mfrs
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
    # Logo garantida (Clearbit) para aparecer nos cards
    for m in manufacturers:
        m.logo_url = get_logo_url(m.name, m.logo_url)
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

    # Média de estrelas, nº de comentários e curtidas por carro
    from src.infra.database import RatingModel, CommentModel, LikeModel
    from sqlalchemy import func as safunc
    rating_map = {}
    for cid, avg, cnt in db.query(RatingModel.car_id, safunc.avg(RatingModel.stars), safunc.count(RatingModel.id)).group_by(RatingModel.car_id).all():
        rating_map[cid] = {"avg": round(float(avg or 0), 1), "count": int(cnt or 0)}
    comment_count_map = {}
    for cid, cnt in db.query(CommentModel.car_id, safunc.count(CommentModel.id)).group_by(CommentModel.car_id).all():
        comment_count_map[cid] = int(cnt or 0)
    like_map = {}
    for cid, cnt in db.query(LikeModel.car_id, safunc.count(LikeModel.id)).group_by(LikeModel.car_id).all():
        like_map[cid] = int(cnt or 0)

    # nº de montadoras distintas com carros
    n_marcas = len({c.manufacturer_id for c in cars if c.manufacturer_id})

    template = jinja_env.get_template("pages/vitrine.html")
    html = template.render(
        request=request,
        cars=sorted(cars, key=lambda c: (score_map.get(c.id, 0)), reverse=True),
        mfr_map=mfr_map,
        score_map=score_map,
        rarity_map=rarity_map,
        rating_map=rating_map,
        comment_count_map=comment_count_map,
        like_map=like_map,
        total=len(all_cars),
        shown=len(cars),
        n_marcas=n_marcas,
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


# ══════════════ AVALIAÇÕES (ESTRELAS) E COMENTÁRIOS ══════════════

@app.post("/car/{car_id}/rate")
async def rate_car(car_id: int, request: Request, db=Depends(get_db)):
    """Amigo do Lucas dá de 1 a 5 estrelas a um carro."""
    from src.infra.database import RatingModel
    from sqlalchemy import func as safunc

    form = await request.form()
    try:
        stars = int(form.get("stars", 0))
    except (TypeError, ValueError):
        stars = 0
    if stars < 1 or stars > 5:
        return JSONResponse(content={"error": "estrelas de 1 a 5"}, status_code=400)

    db.add(RatingModel(car_id=car_id, stars=stars))
    db.commit()

    avg, cnt = db.query(safunc.avg(RatingModel.stars), safunc.count(RatingModel.id))\
        .filter(RatingModel.car_id == car_id).first()
    return JSONResponse(content={"avg": round(float(avg or 0), 1), "count": int(cnt or 0)})


@app.get("/car/{car_id}/comments")
async def list_comments(car_id: int, db=Depends(get_db)):
    """Lista os comentários de um carro (para a vitrine)."""
    from src.infra.database import CommentModel
    rows = db.query(CommentModel).filter(CommentModel.car_id == car_id)\
        .order_by(CommentModel.created_at.desc()).all()
    return JSONResponse(content=[{"author": r.author or "Anônimo", "text": r.text} for r in rows])


@app.post("/car/{car_id}/comment")
async def add_comment(car_id: int, request: Request, db=Depends(get_db)):
    """Amigo do Lucas deixa um comentário em um carro."""
    from src.infra.database import CommentModel
    form = await request.form()
    author = (form.get("author", "") or "").strip()[:60] or "Anônimo"
    text = (form.get("text", "") or "").strip()[:500]
    if not text:
        return JSONResponse(content={"error": "comentário vazio"}, status_code=400)

    db.add(CommentModel(car_id=car_id, author=author, text=text))
    db.commit()
    return JSONResponse(content={"ok": True, "author": author, "text": text})


@app.post("/car/{car_id}/like")
async def like_car(car_id: int, db=Depends(get_db)):
    """Amigo do Lucas curte um carro (❤️)."""
    from src.infra.database import LikeModel
    from sqlalchemy import func as safunc
    db.add(LikeModel(car_id=car_id))
    db.commit()
    total = db.query(safunc.count(LikeModel.id)).filter(LikeModel.car_id == car_id).scalar()
    return JSONResponse(content={"likes": int(total or 0)})


@app.get("/edit/{car_id}")
async def edit_car_page(car_id: int, request: Request, db=Depends(get_db)):
    guard = _needs_login(request)
    if guard:
        return guard
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

    guard = _needs_login(request)
    if guard:
        return guard

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
async def delete_car_action(car_id: int, request: Request, db=Depends(get_db)):
    """Exclui um carro da coleção (ação do Lucas na tela de edição)."""
    from fastapi.responses import RedirectResponse
    import logging

    guard = _needs_login(request)
    if guard:
        return guard

    logger = logging.getLogger(__name__)

    repo = SQLAlchemyCarRepository(db)
    ok = await repo.delete(car_id)
    logger.info(f"Carro {car_id} excluído: {ok}")
    return RedirectResponse(url="/", status_code=303)


@app.post("/edit/{car_id}/photos")
async def upload_photos(car_id: int, request: Request, db=Depends(get_db)):
    """Salva as fotos do carro (principal, frente, traseira)."""
    import uuid

    guard = _needs_login(request)
    if guard:
        return guard

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


@app.get("/super-trunfo")
async def super_trunfo(request: Request, db=Depends(get_db)):
    """Jogo de Super Trunfo com as miniaturas do Lucas (local, passa-e-joga)."""
    from src.infra.repositories import SQLAlchemyManufacturerRepository
    from src.utils.generators import battle_stats

    repo = SQLAlchemyCarRepository(db)
    mfr_repo = SQLAlchemyManufacturerRepository(db)
    all_cars = await repo.get_all()
    manufacturers = await mfr_repo.get_all()
    for m in manufacturers:
        m.logo_url = get_logo_url(m.name, m.logo_url)
    mfr_map = {m.id: m for m in manufacturers}

    def _st(c):
        return c.status.value if hasattr(c.status, "value") else c.status
    publicados = [c for c in all_cars if _st(c) == "published"]
    cars = publicados if publicados else all_cars

    deck = []
    for c in cars:
        urls = [u for u in (c.image_urls or []) if u]
        mfr = mfr_map.get(c.manufacturer_id)
        deck.append({
            "id": c.id,
            "name": c.name,
            "mfr": mfr.name if mfr else "",
            "logo": (mfr.logo_url if mfr else "") or "",
            "photo": urls[0] if urls else "",
            "stats": battle_stats(c),
        })

    template = jinja_env.get_template("pages/super_trunfo.html")
    return HTMLResponse(template.render(request=request, deck=deck))


# ══════════════ DUELO ONLINE (Super Trunfo por link, tempo real via polling) ══════════════
import json as _json
import uuid as _uuid
import random as _random
import string as _string

_ATTR_DIR = {"velocidade": "high", "potencia": "high", "ano": "low", "raridade": "high"}


async def _montar_deck(db):
    from src.infra.repositories import SQLAlchemyManufacturerRepository
    from src.utils.generators import battle_stats
    repo = SQLAlchemyCarRepository(db)
    mfr_repo = SQLAlchemyManufacturerRepository(db)
    all_cars = await repo.get_all()
    manufacturers = await mfr_repo.get_all()
    for m in manufacturers:
        m.logo_url = get_logo_url(m.name, m.logo_url)
    mfr_map = {m.id: m for m in manufacturers}

    def _st(c):
        return c.status.value if hasattr(c.status, "value") else c.status
    publicados = [c for c in all_cars if _st(c) == "published"]
    cars = publicados if publicados else all_cars

    deck = []
    for c in cars:
        urls = [u for u in (c.image_urls or []) if u]
        mfr = mfr_map.get(c.manufacturer_id)
        deck.append({
            "id": c.id, "name": c.name,
            "mfr": mfr.name if mfr else "",
            "logo": (mfr.logo_url if mfr else "") or "",
            "photo": urls[0] if urls else "",
            "stats": battle_stats(c),
        })
    return deck


def _carregar_sala(db, code):
    from src.infra.database import GameRoomModel
    room = db.query(GameRoomModel).filter(GameRoomModel.code == code).first()
    if not room:
        return None, None
    return room, _json.loads(room.data)


def _salvar_sala(db, room, data):
    room.data = _json.dumps(data)
    db.commit()


def _quem_sou(data, token):
    """Índice (0-based) do jogador com esse token, ou -1 (espectador)."""
    for i, p in enumerate(data.get("players", [])):
        if token and p.get("token") == token:
            return i
    return -1


def _ativos(data):
    return [i for i, p in enumerate(data["players"]) if not p.get("out") and p["pile"]]


def _resolver(data, attr):
    players = data["players"]
    ativos = _ativos(data)
    tops = {i: players[i]["pile"][0] for i in ativos}
    vals = {i: tops[i]["stats"][attr] for i in ativos}
    melhor = min(vals.values()) if _ATTR_DIR[attr] == "low" else max(vals.values())
    vencedores = [i for i in ativos if vals[i] == melhor]
    coletadas = [tops[i] for i in ativos]
    for i in ativos:
        players[i]["pile"].pop(0)
    data["last"] = {
        "attr": attr,
        "plays": [{"i": i, "name": players[i]["name"], "card": tops[i], "val": vals[i]} for i in ativos],
        "winner": vencedores[0] if len(vencedores) == 1 else -1,
    }
    if len(vencedores) == 1:
        w = vencedores[0]
        outras = [tops[i] for i in ativos if i != w]
        players[w]["pile"].extend([tops[w]] + outras + data["pot"])
        data["pot"] = []
        data["chooser"] = w
    else:
        data["pot"].extend(coletadas)
    data["phase"] = "reveal"


MAX_JOGADORES = 6


@app.post("/game/new")
async def game_new(db=Depends(get_db)):
    from src.infra.database import GameRoomModel
    deck = await _montar_deck(db)
    if len(deck) < 2:
        return JSONResponse(content={"error": "Publique pelo menos 2 carros para jogar."}, status_code=400)

    code = "".join(_random.choices(_string.ascii_uppercase + _string.digits, k=5))
    host_token = _uuid.uuid4().hex
    data = {
        "deck": deck,
        "players": [{"token": host_token, "name": "Jogador 1", "pile": [], "out": False}],
        "host_token": host_token,
        "pot": [], "chooser": 0, "rodada": 1, "phase": "lobby", "last": None,
        "max": MAX_JOGADORES,
    }
    db.add(GameRoomModel(code=code, data=_json.dumps(data)))
    db.commit()
    return JSONResponse(content={"code": code, "token": host_token, "player": 0})


@app.post("/game/{code}/join")
async def game_join(code: str, request: Request, db=Depends(get_db)):
    form = await request.form()
    token = form.get("token") or ""
    room, data = _carregar_sala(db, code)
    if not room:
        return JSONResponse(content={"error": "Sala não encontrada"}, status_code=404)
    i = _quem_sou(data, token)
    if i >= 0:
        return JSONResponse(content={"token": token, "player": i})
    if data["phase"] != "lobby" or len(data["players"]) >= data.get("max", MAX_JOGADORES):
        return JSONResponse(content={"token": "", "player": -1})  # espectador
    novo = _uuid.uuid4().hex
    idx = len(data["players"])
    data["players"].append({"token": novo, "name": f"Jogador {idx + 1}", "pile": [], "out": False})
    _salvar_sala(db, room, data)
    return JSONResponse(content={"token": novo, "player": idx})


@app.post("/game/{code}/start")
async def game_start(code: str, request: Request, db=Depends(get_db)):
    form = await request.form()
    token = form.get("token") or ""
    room, data = _carregar_sala(db, code)
    if not room:
        return JSONResponse(content={"error": "Sala não encontrada"}, status_code=404)
    if token != data["host_token"]:
        return JSONResponse(content={"error": "Só o host pode começar."}, status_code=403)
    if data["phase"] != "lobby" or len(data["players"]) < 2:
        return JSONResponse(content={"error": "Precisa de pelo menos 2 jogadores."}, status_code=409)

    d = data["deck"][:]
    _random.shuffle(d)
    n = len(data["players"])
    for p in data["players"]:
        p["pile"] = []
    for k, card in enumerate(d):
        data["players"][k % n]["pile"].append(card)
    data["deck"] = []
    data["phase"] = "playing"
    data["chooser"] = 0
    data["rodada"] = 1
    _salvar_sala(db, room, data)
    return JSONResponse(content={"ok": True})


@app.get("/game/{code}/state")
async def game_state(code: str, token: str = "", db=Depends(get_db)):
    room, data = _carregar_sala(db, code)
    if not room:
        return JSONResponse(content={"error": "Sala não encontrada"}, status_code=404)
    you = _quem_sou(data, token)
    phase = data["phase"]
    players = data["players"]
    resumo = [{"name": p["name"], "count": len(p["pile"]), "out": bool(p.get("out"))} for p in players]

    out = {
        "phase": phase,
        "you": you,
        "isHost": (token == data["host_token"]),
        "chooser": data["chooser"],
        "chooserName": players[data["chooser"]]["name"] if players else "",
        "rodada": data["rodada"],
        "players": resumo,
        "nplayers": len(players),
    }
    if phase in ("playing", "reveal") and 0 <= you < len(players) and players[you]["pile"]:
        out["yourCard"] = players[you]["pile"][0]
    if phase in ("reveal", "over"):
        out["last"] = data["last"]
    if phase == "over":
        ativos = _ativos(data)
        out["winner"] = ativos[0] if ativos else -1
        out["winnerName"] = players[ativos[0]]["name"] if ativos else ""
    return JSONResponse(content=out)


@app.post("/game/{code}/choose")
async def game_choose(code: str, request: Request, db=Depends(get_db)):
    form = await request.form()
    token = form.get("token") or ""
    attr = form.get("attr") or ""
    room, data = _carregar_sala(db, code)
    if not room:
        return JSONResponse(content={"error": "Sala não encontrada"}, status_code=404)
    you = _quem_sou(data, token)
    if data["phase"] != "playing" or you != data["chooser"] or attr not in _ATTR_DIR:
        return JSONResponse(content={"ok": False}, status_code=409)
    _resolver(data, attr)
    _salvar_sala(db, room, data)
    return JSONResponse(content={"ok": True})


@app.post("/game/{code}/next")
async def game_next(code: str, db=Depends(get_db)):
    room, data = _carregar_sala(db, code)
    if not room:
        return JSONResponse(content={"error": "Sala não encontrada"}, status_code=404)
    if data["phase"] == "reveal":
        # elimina quem ficou sem cartas
        for p in data["players"]:
            if not p["pile"]:
                p["out"] = True
        ativos = _ativos(data)
        data["rodada"] += 1
        if len(ativos) <= 1 or data["rodada"] > 500:
            data["phase"] = "over"
        else:
            # garante que quem escolhe está ativo
            n = len(data["players"])
            if data["chooser"] not in ativos:
                for passo in range(1, n + 1):
                    cand = (data["chooser"] + passo) % n
                    if cand in ativos:
                        data["chooser"] = cand
                        break
            data["phase"] = "playing"
        _salvar_sala(db, room, data)
    return JSONResponse(content={"ok": True})


@app.get("/jogo/{code}")
async def jogo_online(code: str, request: Request, db=Depends(get_db)):
    room, _ = _carregar_sala(db, code)
    if not room:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/super-trunfo", status_code=303)
    template = jinja_env.get_template("pages/jogo_online.html")
    return HTMLResponse(template.render(request=request, code=code))


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}


# ══════════════ PWA (instalável no celular) ══════════════
@app.get("/manifest.webmanifest")
async def manifest():
    return JSONResponse(content={
        "name": "Lucas Garage",
        "short_name": "Lucas Garage",
        "description": "Coleção premium de miniaturas 1:32",
        "start_url": "/vitrine",
        "display": "standalone",
        "background_color": "#0a0a0a",
        "theme_color": "#0a0a0a",
        "icons": [
            {"src": "/static/icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}
        ]
    }, media_type="application/manifest+json")


@app.get("/sw.js")
async def service_worker():
    from fastapi.responses import Response
    js = (
        "self.addEventListener('install', function(e){ self.skipWaiting(); });\n"
        "self.addEventListener('activate', function(e){ self.clients.claim(); });\n"
        "self.addEventListener('fetch', function(e){});\n"
    )
    return Response(content=js, media_type="application/javascript")


@app.get("/vitrine/poster.png")
async def vitrine_poster(db=Depends(get_db)):
    """Gera uma imagem-pôster da coleção inteira para compartilhar."""
    from fastapi.responses import Response
    from src.utils.generators import calculate_score, collector_level
    from src.services.card_image import gerar_poster

    repo = SQLAlchemyCarRepository(db)
    all_cars = await repo.get_all()

    def _st(c):
        return c.status.value if hasattr(c.status, "value") else c.status
    publicados = [c for c in all_cars if _st(c) == "published"]
    cars = publicados if publicados else all_cars
    cars = sorted(cars, key=lambda c: calculate_score(c), reverse=True)

    itens = []
    for c in cars[:9]:
        urls = [u for u in (c.image_urls or []) if u]
        p = Path(settings.UPLOAD_DIR) / urls[0][len("/uploads/"):] if (urls and urls[0].startswith("/uploads/")) else None
        itens.append((c.name, p))

    total_score = sum(calculate_score(c) for c in all_cars)
    png = gerar_poster(itens, len(all_cars), total_score, collector_level(total_score))
    return Response(content=png, media_type="image/png")
