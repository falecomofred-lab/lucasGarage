"""
Geradores do Lucas Garage:
- QR Code de cada miniatura (via API pública, sem instalar biblioteca)
- Collector Score (pontuação de raridade)
- Nível de Colecionador
"""

from urllib.parse import quote

# ══════════════════ QR CODE ══════════════════

def qrcode_url(data: str, size: int = 200) -> str:
    """
    Gera URL de QR Code usando a API pública qrserver.com (grátis, sem key).
    Lucas imprime e cola na base da miniatura física.
    """
    return f"https://api.qrserver.com/v1/create-qr-code/?size={size}x{size}&data={quote(data)}"


def car_qrcode(car_id: int, base_url: str = "http://localhost:8000") -> str:
    """QR Code que leva direto ao card digital do carro."""
    return qrcode_url(f"{base_url}/car/{car_id}")


# ══════════════════ COLLECTOR SCORE ══════════════════

# Pontos base por classe (raridade)
CLASS_POINTS = {
    "supercar": 90,
    "racing": 80,
    "luxury": 70,
    "sports": 60,
    "muscle": 55,
    "classic": 50,
}

CLASS_LABELS = {
    "supercar": "S",
    "racing": "A",
    "luxury": "A",
    "sports": "B",
    "muscle": "B",
    "classic": "C",
}


def calculate_score(car) -> int:
    """
    Collector Score de um carro:
    - Base pela classe (raridade)
    - Bônus de antiguidade (+5 pts por década)
    - Bônus de ficha completa (+10 descrição, +5 trivia, +5 por foto)
    """
    class_val = car.class_.value if hasattr(car.class_, "value") else str(car.class_)
    score = CLASS_POINTS.get(class_val, 40)

    # Antiguidade: carros mais antigos valem mais
    if car.year:
        decades = max(0, (2026 - car.year) // 10)
        score += min(decades * 5, 40)  # máximo +40

    # Ficha completa
    if car.description:
        score += 10
    if car.trivia:
        score += 5
    if car.image_urls:
        score += 5 * len([u for u in car.image_urls if u])

    return score


def rarity_label(car) -> str:
    """Letra de raridade (S, A, B, C) baseada na classe."""
    class_val = car.class_.value if hasattr(car.class_, "value") else str(car.class_)
    return CLASS_LABELS.get(class_val, "C")


# ══════════════════ NÍVEL DE COLECIONADOR ══════════════════

LEVELS = [
    (0,     "🔰 Iniciante"),
    (1000,  "🚗 Colecionador"),
    (3000,  "🏎️ Entusiasta"),
    (5000,  "⭐ Mestre de Garagem"),
    (7000,  "👑 Lenda das Miniaturas"),
]


def collector_level(total_score: int) -> str:
    """Nível do Lucas baseado na pontuação total da coleção."""
    level = LEVELS[0][1]
    for threshold, name in LEVELS:
        if total_score >= threshold:
            level = name
    return level
