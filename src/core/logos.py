"""
Logos das montadoras — imagens coloridas gratuitas (car-logos-dataset, licença MIT),
servidas pela CDN jsDelivr. Funciona direto no navegador, sem API key.

Fonte: https://github.com/filippofilip95/car-logos-dataset
"""

import re
import unicodedata

BASE = "https://cdn.jsdelivr.net/gh/filippofilip95/car-logos-dataset@master/logos/optimized/"

# Nome da montadora (como está no banco) -> nome do arquivo (slug) no dataset
SLUGS = {
    "Ferrari": "ferrari",
    "Volkswagen": "volkswagen",
    "Lamborghini": "lamborghini",
    "Ford": "ford",
    "Chevrolet": "chevrolet",
    "Fiat": "fiat",
    "Porsche": "porsche",
    "BMW": "bmw",
    "Mercedes-Benz": "mercedes-benz",
    "Mercedes": "mercedes-benz",
    "Toyota": "toyota",
    "Jaguar": "jaguar",
    "Nissan": "nissan",
    "Mitsubishi": "mitsubishi",
    "Jeep": "jeep",
    "Renault": "renault",
    "Kia": "kia",
    "Hummer": "hummer",
    "Aston Martin": "aston-martin",
    "Dodge": "dodge",
    "Maserati": "maserati",
    "McLaren": "mclaren",
    "Bugatti": "bugatti",
    "Audi": "audi",
    "Honda": "honda",
    "Alfa Romeo": "alfa-romeo",
    "Peugeot": "peugeot",
    "Citroën": "citroen",
    "Volvo": "volvo",
    "Mini": "mini",
    "Suzuki": "suzuki",
    "Subaru": "subaru",
    "Hyundai": "hyundai",
    "Lexus": "lexus",
    "Land Rover": "land-rover",
    "Bentley": "bentley",
    "Rolls-Royce": "rolls-royce",
    "Koenigsegg": "koenigsegg",
    "Pagani": "pagani",

    # ── Americanas ──
    "Cadillac": "cadillac", "Chrysler": "chrysler", "Buick": "buick",
    "Pontiac": "pontiac", "GMC": "gmc", "Lincoln": "lincoln",
    "Tesla": "tesla", "RAM": "ram", "Ram": "ram", "Rivian": "rivian",
    "Plymouth": "plymouth", "Oldsmobile": "oldsmobile", "Mercury": "mercury",
    "Saturn": "saturn", "Eagle": "eagle", "AMC": "amc", "Studebaker": "studebaker",
    "Hudson": "hudson", "Packard": "packard", "DeSoto": "desoto",
    "Shelby": "ford", "Saleen": "saleen", "Hennessey": "hennessey",
    "Panoz": "panoz", "Vector": "vector", "Fisker": "fisker",

    # ── Europeias ──
    "Opel": "opel", "Seat": "seat", "SEAT": "seat", "Skoda": "skoda", "Škoda": "skoda",
    "Lancia": "lancia", "Maybach": "maybach", "Smart": "smart", "Dacia": "dacia",
    "Saab": "saab", "Polestar": "polestar", "Alpine": "alpine", "Abarth": "abarth",
    "Lotus": "lotus", "Morgan": "morgan", "Caterham": "caterham", "Noble": "noble",
    "TVR": "tvr", "Vauxhall": "vauxhall", "Spyker": "spyker", "Wiesmann": "wiesmann",
    "Bristol": "bristol", "De Tomaso": "de-tomaso", "Iso": "iso",
    "Bizzarrini": "bizzarrini", "Facel Vega": "facel-vega", "Venturi": "venturi",
    "Ginetta": "ginetta", "Marcos": "marcos", "Jensen": "jensen", "Ariel": "ariel",
    "Radical": "radical", "Austin": "austin", "Morris": "morris",
    "Triumph": "triumph", "MG": "mg", "Riley": "riley", "Hillman": "hillman",
    "Simca": "simca", "Talbot": "talbot",

    # ── Asiáticas ──
    "Mazda": "mazda", "Acura": "acura", "Infiniti": "infiniti", "Genesis": "genesis",
    "Datsun": "datsun", "Daihatsu": "daihatsu", "Isuzu": "isuzu",
    "SsangYong": "ssangyong", "Tata": "tata", "Chery": "chery", "BYD": "byd",
    "Geely": "geely", "Great Wall": "great-wall", "Scion": "scion",
    "Holden": "holden", "Troller": "troller",

    # ── Apelidos e grafias que o Lucas pode escrever ──
    "Cadilaque": "cadillac", "Cadilac": "cadillac", "Caddy": "cadillac",
    "Chevy": "chevrolet", "GM": "chevrolet", "VW": "volkswagen",
    "Volks": "volkswagen", "Merc": "mercedes-benz", "Beemer": "bmw",
    "Rolls Royce": "rolls-royce", "Alfa": "alfa-romeo", "Citroen": "citroen",
    "Land-Rover": "land-rover", "Range Rover": "land-rover",
    "Astom Martin": "aston-martin", "Lambo": "lamborghini",
}


def _slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", s.lower().strip()).strip("-")
    return s


def get_logo_url(manufacturer_name: str, db_logo_url: str | None = None) -> str | None:
    """
    Retorna a URL do logo da montadora:
    1. Logo local salva no banco (/static/...) tem prioridade
    2. car-logos-dataset (CDN jsDelivr) pelo nome da marca
    3. None se não houver marca (o template esconde o selo)
    """
    if db_logo_url and db_logo_url.startswith("/static"):
        return db_logo_url

    if not manufacturer_name or manufacturer_name.strip().lower() in ("outros", "outro", "—", ""):
        return None

    # 1) exceção do catálogo  2) apelido conhecido  3) slug derivado do nome
    try:
        from src.core.montadoras import EXCECOES_SLUG
    except Exception:
        EXCECOES_SLUG = {}

    slug = (EXCECOES_SLUG.get(manufacturer_name)
            or SLUGS.get(manufacturer_name)
            or _slugify(manufacturer_name))
    if not slug:
        return None
    return f"{BASE}{slug}.png"
