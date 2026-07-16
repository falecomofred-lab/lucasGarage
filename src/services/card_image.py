"""
Gera o CARD-IMAGEM do carro (PNG) para o Lucas compartilhar no WhatsApp.
Mesma identidade do app: fundo preto, vermelho Ferrari, visual de card de colecionador.
"""

from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Paleta (igual ao app)
BLACK = (10, 10, 10)
DARK = (23, 23, 23)
GRAPHITE = (38, 38, 38)
FERRARI = (255, 40, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)

RARITY_COLORS = {
    "S": (255, 215, 0),     # ouro
    "A": (255, 40, 0),      # vermelho
    "B": (100, 150, 255),   # azul
    "C": (150, 150, 150),   # cinza
}

W, H = 1080, 1350
PHOTO_H = 760


def _font(size, bold=True):
    """Carrega uma fonte TTF de forma robusta (com fallback)."""
    candidatos = [
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
    ]
    for c in candidatos:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size)
    except Exception:
        return ImageFont.load_default()


def _cover(img, w, h):
    """Recorta a imagem preenchendo w x h (estilo object-cover, centralizado)."""
    img = img.convert("RGB")
    ow, oh = img.size
    scale = max(w / ow, h / oh)
    nw, nh = int(ow * scale), int(oh * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return img.crop((left, top, left + w, top + h))


def _center_text(draw, cx, y, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw / 2, y), text, font=font, fill=fill)


def gerar_card(car, mfr_name, score, rarity, photo_path: Path | None) -> bytes:
    card = Image.new("RGB", (W, H), BLACK)
    draw = ImageDraw.Draw(card)

    # brilho vermelho no topo
    glow = Image.new("RGB", (W, H), BLACK)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W * 0.1, -300, W * 0.9, 400], fill=(60, 12, 6))
    card = Image.blend(card, glow, 0.5)
    draw = ImageDraw.Draw(card)

    # ── FOTO ──
    if photo_path and Path(photo_path).exists():
        try:
            photo = _cover(Image.open(photo_path), W, PHOTO_H)
            card.paste(photo, (0, 0))
        except Exception:
            draw.rectangle([0, 0, W, PHOTO_H], fill=GRAPHITE)
            _center_text(draw, W / 2, PHOTO_H / 2 - 40, "1:32", _font(90), (60, 60, 60))
    else:
        draw.rectangle([0, 0, W, PHOTO_H], fill=GRAPHITE)
        _center_text(draw, W / 2, PHOTO_H / 2 - 40, "1:32", _font(90), (60, 60, 60))

    # degradê preto na base da foto
    grad = Image.new("L", (1, PHOTO_H), 0)
    for y in range(PHOTO_H):
        grad.putpixel((0, y), int(255 * max(0, (y - PHOTO_H * 0.55) / (PHOTO_H * 0.45))))
    grad = grad.resize((W, PHOTO_H))
    black_img = Image.new("RGB", (W, PHOTO_H), BLACK)
    card.paste(black_img, (0, 0), grad)
    draw = ImageDraw.Draw(card)

    # ── BADGE DE RARIDADE (círculo) ──
    rc = RARITY_COLORS.get(rarity, GRAY)
    draw.ellipse([40, 40, 150, 150], fill=rc)
    _center_text(draw, 95, 62, rarity, _font(62), BLACK)

    # ID no canto
    _center_text(draw, W - 100, 62, f"#{car.id}", _font(48), FERRARI)

    # ── NOME ──
    y = PHOTO_H - 130
    nome = (car.name or "").upper()
    if len(nome) > 20:
        nome = nome[:19] + "…"
    draw.text((60, y), nome, font=_font(64), fill=WHITE)

    # montadora · ano · cor
    sub = " · ".join([x for x in [mfr_name, str(car.year) if car.year else None, car.color] if x])
    draw.text((62, y + 78), sub.upper(), font=_font(30, bold=False), fill=GRAY)

    # ── STATS ──
    sy = PHOTO_H + 70
    draw.line([60, sy - 20, W - 60, sy - 20], fill=(40, 40, 40), width=2)

    draw.text((60, sy), "COLLECTOR SCORE", font=_font(28, bold=False), fill=GRAY)
    draw.text((60, sy + 40), str(score), font=_font(96), fill=FERRARI)
    draw.text((60 + _tw(draw, str(score), _font(96)) + 20, sy + 100), "pts", font=_font(36, bold=False), fill=GRAY)

    draw.text((W - 420, sy), "RARIDADE", font=_font(28, bold=False), fill=GRAY)
    draw.text((W - 420, sy + 40), f"CLASSE {rarity}", font=_font(72), fill=rc)

    # escala
    draw.text((W - 420, sy + 140), f"ESCALA {car.scale or '1:32'}", font=_font(30, bold=False), fill=GRAY)

    # ── RODAPÉ / MARCA ──
    fy = H - 90
    draw.rectangle([0, fy - 20, W, H], fill=DARK)
    draw.text((60, fy), "LUCAS", font=_font(44), fill=WHITE)
    lw = _tw(draw, "LUCAS ", _font(44))
    draw.text((60 + lw, fy), "GARAGE", font=_font(44), fill=FERRARI)
    _center_text(draw, W - 160, fy + 8, "Coleção 1:32", _font(30, bold=False), GRAY)

    out = BytesIO()
    card.save(out, format="PNG")
    return out.getvalue()


def _tw(draw, text, font):
    b = draw.textbbox((0, 0), text, font=font)
    return b[2] - b[0]
