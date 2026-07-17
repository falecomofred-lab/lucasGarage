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

    slug = SLUGS.get(manufacturer_name) or _slugify(manufacturer_name)
    if not slug:
        return None
    return f"{BASE}{slug}.png"
