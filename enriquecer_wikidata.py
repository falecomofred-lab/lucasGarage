"""
Enriquece as cartas com dados REAIS do Wikidata.

Busca por carro: peso (kg), unidades produzidas e sugestão de classe.
Roda no SEU PC (a Wikipédia/Wikidata é bloqueada no PythonAnywhere grátis).

  1) Ver o que seria alterado, SEM gravar nada:
        python enriquecer_wikidata.py

  2) Gravar de verdade, depois de conferir o relatório:
        python enriquecer_wikidata.py --gravar

Sempre faça backup do banco antes de gravar.
"""

import json
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

from src.infra.database import SessionLocal, CarModel, ManufacturerModel, Base, engine

UA = "LucasGarage/1.0 (colecao de miniaturas; contato via venure.com.br)"
TIMEOUT = 20
PAUSA = 0.4          # respeita o servidor do Wikidata

# Propriedades do Wikidata
P_MASSA = "P2067"
P_PRODUZIDOS = "P1092"
P_INSTANCIA = "P31"

# Q-ids que indicam tipo de veículo -> classe sugerida
TIPO_CLASSE = {
    "Q815018": "supercar",    # supercarro
    "Q1875621": "sports",     # carro esportivo
    "Q192152": "sports",      # sports car
    "Q2001305": "muscle",     # muscle car
    "Q1420": "classic",       # automóvel
    "Q3231690": "classic",    # automóvel de passeio
    "Q116267": "luxury",      # carro de luxo
    "Q194356": "racing",      # carro de corrida
}


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


def _norm(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn").strip()


def buscar_qid(termo):
    """Acha o Q-id do modelo no Wikidata."""
    url = ("https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json"
           "&language=pt&uselang=pt&limit=5&search=" + urllib.parse.quote(termo))
    try:
        d = _get(url)
    except Exception:
        return None, None
    for item in d.get("search", []):
        desc = _norm(item.get("description", ""))
        # só aceita se a descrição indicar veículo (evita cair em música, filme, pessoa)
        if any(k in desc for k in ("autom", "carro", "veic", "supercarro", "picape",
                                   "caminhon", "suv", "car", "vehicle")):
            return item["id"], item.get("label")
    return None, None


def dados_do_qid(qid):
    """Extrai peso, unidades produzidas e tipo."""
    try:
        d = _get("https://www.wikidata.org/wiki/Special:EntityData/%s.json" % qid)
        claims = d["entities"][qid]["claims"]
    except Exception:
        return {}

    def numero(prop):
        try:
            snak = claims[prop][0]["mainsnak"]["datavalue"]["value"]
            valor = float(str(snak["amount"]).lstrip("+"))
            unidade = snak.get("unit", "")
            # massa às vezes vem em toneladas ou libras
            if prop == P_MASSA:
                if unidade.endswith("Q11570"):        # quilograma
                    return int(valor)
                if unidade.endswith("Q11573"):        # tonelada? (guarda-chuva)
                    return int(valor * 1000)
                if unidade.endswith("Q100995"):       # libra
                    return int(valor * 0.4536)
                if valor < 50:                        # provavelmente tonelada
                    return int(valor * 1000)
            return int(valor)
        except Exception:
            return None

    tipos = []
    for c in claims.get(P_INSTANCIA, []):
        try:
            tipos.append(c["mainsnak"]["datavalue"]["value"]["id"])
        except Exception:
            pass

    classe = None
    for t in tipos:
        if t in TIPO_CLASSE:
            classe = TIPO_CLASSE[t]
            break

    return {
        "peso": numero(P_MASSA),
        "produzidos": numero(P_PRODUZIDOS),
        "classe": classe,
        "tipos": tipos,
    }


def main():
    gravar = "--gravar" in sys.argv
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    marcas = {m.id: m.name for m in db.query(ManufacturerModel).all()}
    carros = db.query(CarModel).order_by(CarModel.id).all()

    print("=" * 78)
    print("ENRIQUECIMENTO PELO WIKIDATA — %s" % ("GRAVANDO" if gravar else "SIMULAÇÃO (nada será salvo)"))
    print("=" * 78)
    print("%-4s %-28s %-9s %-12s %s" % ("id", "carro", "peso", "produzidos", "classe sugerida"))
    print("-" * 78)

    achou = falhou = 0
    for c in carros:
        marca = marcas.get(c.manufacturer_id, "") or ""
        if marca.lower() in ("outros", "outro"):
            marca = ""
        termo = ("%s %s" % (marca, c.name or "")).strip()

        qid, rotulo = buscar_qid(termo)
        time.sleep(PAUSA)

        if not qid:
            falhou += 1
            print("%-4s %-28s %s" % (c.id, (c.name or "")[:28], "— não encontrado"))
            continue

        info = dados_do_qid(qid)
        time.sleep(PAUSA)

        classe_atual = c.class_.value if hasattr(c.class_, "value") else str(c.class_)
        sugestao = info.get("classe")
        muda_classe = sugestao and sugestao != classe_atual

        print("%-4s %-28s %-9s %-12s %s" % (
            c.id,
            (c.name or "")[:28],
            info.get("peso") or "—",
            info.get("produzidos") or "—",
            ("%s → %s" % (classe_atual, sugestao)) if muda_classe else "(mantém)",
        ))

        if info.get("peso") or info.get("produzidos"):
            achou += 1

        if gravar:
            if info.get("peso"):
                c.peso = info["peso"]
            if info.get("produzidos"):
                c.produzidos = info["produzidos"]
            # a classe NÃO é alterada automaticamente — veja a observação abaixo

    if gravar:
        db.commit()
        print("\n✅ Peso e unidades gravados no banco.")
    else:
        print("\n(simulação — rode com --gravar para salvar)")

    print("\n%d carros com dado real · %d sem correspondência no Wikidata" % (achou, falhou))
    print("\nA CLASSE não é alterada automaticamente de propósito: a coluna acima é")
    print("só uma sugestão para você e o Lucas revisarem. Mudar a classe muda o")
    print("equilíbrio do baralho inteiro, então é decisão de vocês, carta a carta.")
    db.close()


if __name__ == "__main__":
    main()
