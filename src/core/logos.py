"""
Logos das montadoras — URLs confiáveis via Clearbit Logo API.
Funciona direto no navegador, sem API key, sem script de download.

Formato: https://logo.clearbit.com/{dominio-da-marca}
"""

# Nome da montadora -> domínio oficial
MANUFACTURER_DOMAINS = {
    "Ferrari": "ferrari.com",
    "Lamborghini": "lamborghini.com",
    "Maserati": "maserati.com",
    "Alfa Romeo": "alfaromeo.com",
    "Lancia": "lancia.com",
    "Pagani": "pagani.com",
    "Porsche": "porsche.com",
    "BMW": "bmw.com",
    "Mercedes-Benz": "mercedes-benz.com",
    "Audi": "audi.com",
    "Volkswagen": "vw.com",
    "Opel": "opel.com",
    "Maybach": "mercedes-benz.com",
    "McLaren": "mclaren.com",
    "Jaguar": "jaguar.com",
    "Rolls-Royce": "rolls-roycemotorcars.com",
    "Bentley": "bentleymotors.com",
    "Aston Martin": "astonmartin.com",
    "Lotus": "lotuscars.com",
    "MG": "mg.co.uk",
    "Bugatti": "bugatti.com",
    "Renault": "renault.com",
    "Peugeot": "peugeot.com",
    "Citroën": "citroen.com",
    "Alpine": "alpinecars.com",
    "Ford": "ford.com",
    "Chevrolet": "chevrolet.com",
    "Dodge": "dodge.com",
    "Plymouth": "stellantis.com",
    "Pontiac": "gm.com",
    "Oldsmobile": "gm.com",
    "Cadillac": "cadillac.com",
    "Corvette": "chevrolet.com",
    "Shelby": "shelby.com",
    "Hummer": "gmc.com",
    "Volvo": "volvocars.com",
    "Saab": "saab.com",
    "Koenigsegg": "koenigsegg.com",
    "Toyota": "toyota.com",
    "Nissan": "nissan-global.com",
    "Honda": "honda.com",
    "Mazda": "mazda.com",
    "Suzuki": "globalsuzuki.com",
    "Mitsubishi": "mitsubishi-motors.com",
    "Subaru": "subaru.com",
    "Daihatsu": "daihatsu.com",
    "Isuzu": "isuzu.co.jp",
    "Lexus": "lexus.com",
    "Acura": "acura.com",
    "Infiniti": "infiniti.com",
    "Hyundai": "hyundai.com",
    "Kia": "kia.com",
    "Seat": "seat.com",
    "Caterham": "caterhamcars.com",
    "Holden": "gm.com",
    "Tata": "tatamotors.com",
    "Mahindra": "mahindra.com",
}


def get_logo_url(manufacturer_name: str, db_logo_url: str | None = None) -> str | None:
    """
    Retorna a melhor URL de logo disponível:
    1. URL local (/static/...) salva no banco
    2. Clearbit (sempre funciona no navegador)
    3. URL externa salva no banco
    """
    # Logo local baixada tem prioridade máxima
    if db_logo_url and db_logo_url.startswith("/static"):
        return db_logo_url

    # Clearbit: confiável, sem key
    domain = MANUFACTURER_DOMAINS.get(manufacturer_name)
    if domain:
        return f"https://logo.clearbit.com/{domain}"

    # Fallback: o que tiver no banco
    return db_logo_url
