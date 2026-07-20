"""
Busca informações do carro na Wikipédia (pt, com fallback en).

Em vez de chutar o primeiro resultado (que erra feio em nomes curtos
tipo "C15"), devolve uma LISTA de candidatos já filtrados — só artigos
que realmente falam de veículo — para o Lucas escolher o certo.

Usa só a biblioteca padrão (urllib). Respeita http(s)_proxy.
"""

import json
import unicodedata
import urllib.parse
import urllib.request

UA = "LucasGarage/1.0 (catalogo de miniaturas; contato via venure.com.br)"
TIMEOUT = 8

# Sinais de que o artigo é sobre veículo
AUTO = (
    "automovel", "carro", "picape", "pick-up", "caminhonete", "caminhao",
    "utilitario", "veiculo", "motor", "montadora", "esportivo", "seda",
    "suv", "cupe", "coupe", "hatch", "perua", "modelo de",
)
# Sinais de que o artigo é sobre pessoa (piloto, ator...)
PESSOA = ("piloto", "nasceu", "futebolista", "automobilista", "cantor", "ator", "atriz")


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


def _titulos(idioma: str, termo: str, n: int = 6):
    url = (
        f"https://{idioma}.wikipedia.org/w/api.php?action=query&list=search&format=json"
        f"&srlimit={n}&srsearch={urllib.parse.quote(termo)}"
    )
    try:
        return [h["title"] for h in _get(url).get("query", {}).get("search", [])]
    except Exception:
        return []


def _resumo(idioma: str, titulo: str):
    url = f"https://{idioma}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(titulo)}"
    try:
        d = _get(url)
    except Exception:
        return None
    extrato = (d.get("extract") or "").strip()
    if not extrato:
        return None
    return {
        "titulo": d.get("title") or titulo,
        "descricao_curta": d.get("description") or "",
        "resumo": extrato,
        "url": (d.get("content_urls", {}).get("desktop", {}) or {}).get("page", ""),
    }


def _e_veiculo(r) -> bool:
    blob = _norm(r["resumo"][:400] + " " + r["descricao_curta"])
    if any(p in blob for p in PESSOA) and not any(a in _norm(r["descricao_curta"]) for a in ("automovel", "carro")):
        return False
    return any(a in blob for a in AUTO)


def _pontuar(r, nome: str, montadora: str) -> float:
    titulo = _norm(r["titulo"])
    blob = _norm(r["resumo"][:400] + " " + r["descricao_curta"])
    sc = 0.0
    if montadora and _norm(montadora) in titulo:
        sc += 2
    if nome and _norm(nome) in titulo:
        sc += 3
    sc += sum(1 for a in AUTO if a in blob) * 0.1
    return sc


def buscar_candidatos(nome: str, montadora: str = "", termo_livre: str = "", limite: int = 5):
    """
    Devolve lista de candidatos [{titulo, descricao_curta, resumo, url}],
    ordenados por relevância. Lista vazia se não achar nada de veículo.
    """
    nome = (nome or "").strip()
    montadora = (montadora or "").strip()
    termo = (termo_livre or "").strip() or (f"{montadora} {nome}".strip() if montadora else nome)
    if not termo:
        return []

    achados, vistos = [], set()
    for idioma in ("pt", "en"):
        for titulo in _titulos(idioma, termo):
            if _norm(titulo) in vistos:
                continue
            vistos.add(_norm(titulo))
            r = _resumo(idioma, titulo)
            if not r or not _e_veiculo(r):
                continue
            r["idioma"] = idioma
            achados.append((_pontuar(r, nome, montadora), r))
            if len(achados) >= limite:
                break
        if achados:  # já achou em português, não precisa do inglês
            break

    achados.sort(key=lambda x: -x[0])
    return [r for _, r in achados[:limite]]


def curiosidade(resumo: str, limite: int = 320) -> str:
    """Corta o resumo numa curiosidade curta, sem cortar frase no meio."""
    txt = (resumo or "").strip()
    if len(txt) <= limite:
        return txt
    corte = txt[:limite]
    fim = corte.rfind(". ")
    return (corte[: fim + 1] if fim > 60 else corte.rstrip() + "...").strip()
