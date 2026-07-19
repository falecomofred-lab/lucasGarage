"""
Busca curiosidades/história do carro na Wikipédia (pt, com fallback en).

Usa só a biblioteca padrão (urllib) — sem instalar nada.
Respeita a variável de ambiente http(s)_proxy, necessária no PythonAnywhere.
"""

import json
import urllib.parse
import urllib.request

UA = "LucasGarage/1.0 (catalogo de miniaturas; contato via venure.com.br)"
TIMEOUT = 8


def _get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


def _resumo(idioma: str, titulo: str):
    """Resumo direto de uma página da Wikipédia."""
    url = f"https://{idioma}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(titulo)}"
    try:
        d = _get(url)
    except Exception:
        return None
    if not d or d.get("type") == "https://mediawiki.org/wiki/HyperSwitch/errors/not_found":
        return None
    extrato = (d.get("extract") or "").strip()
    if not extrato:
        return None
    return {
        "titulo": d.get("title") or titulo,
        "resumo": extrato,
        "url": (d.get("content_urls", {}).get("desktop", {}) or {}).get("page", ""),
    }


def _buscar_titulo(idioma: str, termo: str):
    """Procura o título mais provável antes de pedir o resumo."""
    url = (
        f"https://{idioma}.wikipedia.org/w/api.php?action=query&list=search&format=json"
        f"&srlimit=1&srsearch={urllib.parse.quote(termo)}"
    )
    try:
        d = _get(url)
        hits = d.get("query", {}).get("search", [])
        return hits[0]["title"] if hits else None
    except Exception:
        return None


def buscar_carro(nome: str, montadora: str = "", ano=None):
    """
    Devolve {'titulo','resumo','url'} do carro, ou None se não achar.
    Tenta português primeiro; se falhar, tenta inglês.
    """
    nome = (nome or "").strip()
    if not nome:
        return None

    termo = f"{montadora} {nome}".strip() if montadora else nome

    for idioma in ("pt", "en"):
        # 1) tenta o termo direto como título
        r = _resumo(idioma, termo)
        if r:
            return r
        # 2) busca o título certo e tenta de novo
        titulo = _buscar_titulo(idioma, f"{termo} carro" if idioma == "pt" else f"{termo} car")
        if titulo:
            r = _resumo(idioma, titulo)
            if r:
                return r
    return None


def curiosidade(resumo: str, limite: int = 320) -> str:
    """Corta o resumo numa curiosidade curta, sem cortar frase no meio."""
    txt = (resumo or "").strip()
    if len(txt) <= limite:
        return txt
    corte = txt[:limite]
    fim = corte.rfind(". ")
    return (corte[: fim + 1] if fim > 60 else corte.rstrip() + "...").strip()
