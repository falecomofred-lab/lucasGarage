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


# ══════════════════ SUPER TRUNFO (atributos de batalha) ══════════════════

import hashlib

# Base de Velocidade/Potência por classe (0-99)
_BATTLE_BASE = {
    "supercar": (94, 90),
    "racing":   (96, 88),
    "sports":   (84, 80),
    "muscle":   (80, 94),
    "luxury":   (76, 82),
    "classic":  (66, 64),
}

_RARITY_POINTS = {"S": 96, "A": 86, "B": 72, "C": 58}


def battle_auto(car) -> dict:
    """Velocidade/Potência automáticas (a partir da classe + nome)."""
    class_val = car.class_.value if hasattr(car.class_, "value") else str(car.class_)
    base_vel, base_pot = _BATTLE_BASE.get(class_val, (60, 60))
    seed = int(hashlib.md5((car.name or str(car.id or "")).encode()).hexdigest(), 16)
    j1 = seed % 9 - 4          # -4..+4
    j2 = (seed // 9) % 9 - 4
    return {
        "velocidade": max(40, min(99, base_vel + j1)),
        "potencia": max(40, min(99, base_pot + j2)),
    }


LETRAS = ["A", "B", "C", "D", "E", "F", "G", "H"]


def atribuir_letras(itens):
    """
    Distribui as letras do baralho automaticamente pela FORÇA da carta.

    itens = lista de (id, forca). As mais fortes viram A, depois B, C...
    Divide em até 8 grupos proporcionais, então o baralho se reequilibra
    sozinho quando o Lucas cadastra carros novos (a letra não é gravada).

    Devolve {id: {"letra": "A", "codigo": "A3"}}
    """
    import math
    ordenados = sorted(itens, key=lambda t: (-t[1], t[0]))
    n = len(ordenados)
    if n == 0:
        return {}
    grupos = min(len(LETRAS), n)
    tam = math.ceil(n / grupos)
    out = {}
    for pos, (cid, _forca) in enumerate(ordenados):
        gi = min(pos // tam, grupos - 1)
        out[cid] = {"letra": LETRAS[gi], "codigo": f"{LETRAS[gi]}{pos - gi * tam + 1}"}
    return out


def duelo(cartas, attr_key, direcao="high"):
    """
    Resolve uma rodada de Super Trunfo entre N cartas.

    Regras (clássicas):
      1. A carta Super Trunfo vence todas as outras...
      2. ...MENOS as cartas de letra A, que derrubam o Super Trunfo.
      3. Sem Super Trunfo em jogo, compara o atributo escolhido.

    `cartas` = lista de dicts com 'stats', 'letra' e 'super'.
    Devolve (indices_vencedores, motivo). Empate = mais de um índice.
    """
    idx_super = [i for i, c in enumerate(cartas) if c.get("super")]

    if idx_super:
        s = idx_super[0]
        matadores = [i for i, c in enumerate(cartas)
                     if i != s and str(c.get("letra") or "").upper() == "A"]
        if matadores:
            # Entre as letras A, decide o atributo
            vals = {i: cartas[i]["stats"][attr_key] for i in matadores}
            melhor = min(vals.values()) if direcao == "low" else max(vals.values())
            return [i for i in matadores if vals[i] == melhor], "letra_a"
        return [s], "super_trunfo"

    vals = {i: c["stats"][attr_key] for i, c in enumerate(cartas)}
    melhor = min(vals.values()) if direcao == "low" else max(vals.values())
    return [i for i in vals if vals[i] == melhor], "atributo"


CLASS_PT = {
    "sports": "Esportivo",
    "classic": "Clássico",
    "supercar": "Superesportivo",
    "muscle": "Muscle car",
    "racing": "Competição",
    "luxury": "Luxo",
}


def _opcoes(correta, candidatos, n=4):
    """Monta n alternativas: a correta + distratores únicos, embaralhadas."""
    import random
    vistos = {str(correta).strip().lower()}
    opts = [correta]
    for c in candidatos:
        if c is None:
            continue
        c = str(c).strip()
        if not c or c.lower() in vistos:
            continue
        vistos.add(c.lower())
        opts.append(c)
        if len(opts) >= n:
            break
    random.shuffle(opts)
    return opts, opts.index(correta)


def _fmt_unid(n) -> str:
    """21529464 -> '21,5 milhões'  ·  1337 -> '1.337'"""
    n = int(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}".replace(".", ",") + " milhões"
    if n >= 1000:
        return f"{n:,}".replace(",", ".")
    return str(n)


def perguntas_do_carro(car, mfr_nome, outros) -> list:
    """
    Gera perguntas de múltipla escolha a partir dos dados que já temos.
    `outros` = lista de dicts {name, mfr, year, class_, color} das outras miniaturas.
    Não usa IA nem internet.
    """
    import random
    nome = car.name or "esta miniatura"
    perguntas = []

    # 1) Ano de lançamento
    if car.year:
        anos = [o.get("year") for o in outros if o.get("year") and o.get("year") != car.year]
        random.shuffle(anos)
        extras = anos[:3] or [car.year - 5, car.year + 4, car.year - 11]
        opts, idx = _opcoes(str(car.year), [str(a) for a in extras])
        perguntas.append({"pergunta": f"Em que ano saiu o {nome}?", "opcoes": opts, "correta": idx})

    # 2) Montadora
    if mfr_nome:
        marcas = list({o.get("mfr") for o in outros if o.get("mfr") and o.get("mfr") != mfr_nome})
        random.shuffle(marcas)
        opts, idx = _opcoes(mfr_nome, marcas[:3] or ["Ferrari", "Volkswagen", "Ford"])
        perguntas.append({"pergunta": f"Qual montadora fabricou o {nome}?", "opcoes": opts, "correta": idx})

    # 3) Categoria
    cval = car.class_.value if hasattr(car.class_, "value") else str(car.class_)
    if cval in CLASS_PT:
        certa = CLASS_PT[cval]
        outras = [v for k, v in CLASS_PT.items() if k != cval]
        random.shuffle(outras)
        opts, idx = _opcoes(certa, outras[:3])
        perguntas.append({"pergunta": f"Em que categoria o {nome} se encaixa?", "opcoes": opts, "correta": idx})

    # 4) Cor da miniatura
    if car.color:
        cores = list({o.get("color") for o in outros if o.get("color") and o.get("color") != car.color})
        random.shuffle(cores)
        opts, idx = _opcoes(car.color, cores[:3] or ["Preto", "Prata", "Azul"])
        perguntas.append({"pergunta": f"Qual a cor desta miniatura do {nome}?", "opcoes": opts, "correta": idx})

    # 5) Unidades produzidas — pergunta forte, os números são bem distintos
    prod = getattr(car, "produzidos", None)
    if prod:
        outros_prod = [o.get("produzidos") for o in outros if o.get("produzidos") and o.get("produzidos") != prod]
        random.shuffle(outros_prod)
        extras = outros_prod[:3] or [prod * 12, max(60, prod // 15), prod * 120]
        opts, idx = _opcoes(_fmt_unid(prod), [_fmt_unid(x) for x in extras])
        perguntas.append({
            "pergunta": f"Quantas unidades do {nome} foram fabricadas?",
            "opcoes": opts, "correta": idx,
        })

    # 6) Peso
    peso = getattr(car, "peso", None)
    if peso:
        outros_peso = [o.get("peso") for o in outros if o.get("peso") and abs(o.get("peso") - peso) > 60]
        random.shuffle(outros_peso)
        extras = [f"{p} kg" for p in outros_peso[:3]] or [
            f"{peso + 380} kg", f"{max(400, peso - 320)} kg", f"{peso + 750} kg"
        ]
        opts, idx = _opcoes(f"{peso} kg", extras)
        perguntas.append({"pergunta": f"Quanto pesa o {nome}?", "opcoes": opts, "correta": idx})

    # 7) Atributo de batalha (Super Trunfo)
    st = battle_stats(car)
    vel = st["velocidade"]
    distratores = [str(max(1, vel - random.randint(6, 18))), str(min(99, vel + random.randint(6, 18))),
                   str(max(1, vel - random.randint(20, 32)))]
    opts, idx = _opcoes(str(vel), distratores)
    perguntas.append({"pergunta": f"Qual a Velocidade do {nome} no Super Trunfo?", "opcoes": opts, "correta": idx})

    random.shuffle(perguntas)
    return perguntas[:5]


# Estimativa quando não há dado real (peso em kg, unidades fabricadas)
_FICHA_BASE = {
    "supercar": {"peso": 1450, "produzidos": 3000},
    "racing":   {"peso": 1150, "produzidos": 800},
    "sports":   {"peso": 1350, "produzidos": 90000},
    "muscle":   {"peso": 1650, "produzidos": 300000},
    "luxury":   {"peso": 1850, "produzidos": 120000},
    "classic":  {"peso": 1050, "produzidos": 900000},
}


def ficha_auto(car) -> dict:
    """Peso e unidades produzidas estimados pela classe (com variação estável)."""
    class_val = car.class_.value if hasattr(car.class_, "value") else str(car.class_)
    base = _FICHA_BASE.get(class_val, {"peso": 1300, "produzidos": 200000})
    seed = int(hashlib.md5((car.name or str(car.id or "")).encode()).hexdigest(), 16)
    var_p = (seed % 21) - 10                 # -10% a +10%
    var_u = ((seed // 21) % 61) - 30         # -30% a +30%
    return {
        "peso": max(400, int(base["peso"] * (1 + var_p / 100))),
        "produzidos": max(50, int(base["produzidos"] * (1 + var_u / 100))),
    }


def battle_stats(car) -> dict:
    """
    Atributos de batalha do Super Trunfo. Usa os valores MANUAIS do carro
    (velocidade/potencia) quando preenchidos; senão calcula automaticamente.
    Direção de vitória: velocidade/potência/raridade -> MAIOR vence; ano -> MAIS ANTIGO vence.
    """
    auto = battle_auto(car)
    fauto = ficha_auto(car)
    mv = getattr(car, "velocidade", None)
    mp = getattr(car, "potencia", None)
    peso = getattr(car, "peso", None)
    prod = getattr(car, "produzidos", None)
    return {
        "velocidade": max(1, min(99, int(mv))) if mv else auto["velocidade"],
        "potencia": max(1, min(99, int(mp))) if mp else auto["potencia"],
        "ano": car.year or 2000,
        "raridade": _RARITY_POINTS.get(rarity_label(car), 60),
        # dado REAL do Wikidata quando existe; estimado quando não
        "peso": int(peso) if peso else fauto["peso"],
        "produzidos": int(prod) if prod else fauto["produzidos"],
    }
