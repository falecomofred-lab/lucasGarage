"""
Serviço para buscar imagens públicas de fabricantes.

Integra com múltiplas APIs:
- Wikimedia Commons (gratuito, muito acervo)
- Pixabay (gratuito, mas limitado)
- Unsplash (gratuito, legal)

As imagens são cacheadas localmente por 30 dias.
"""

import httpx
import asyncio
from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import json
import re
from urllib.parse import quote

@dataclass
class PublicImage:
    """Representa uma imagem pública"""
    url: str
    source: str  # wikimedia, pixabay, unsplash
    license: str  # CC-BY-SA, etc
    title: str
    attribution: str
    thumbnail_url: Optional[str] = None


class ManufacturerImageService:
    """Busca imagens públicas de carros fabricantes"""

    # Config das APIs
    WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"
    PIXABAY_API = "https://pixabay.com/api/"
    UNSPLASH_API = "https://api.unsplash.com/search/photos"

    def __init__(
        self,
        cache_dir: Path = Path("./data/image_cache"),
        pixabay_key: Optional[str] = None,
        unsplash_key: Optional[str] = None
    ):
        """
        Inicializa o serviço.

        Args:
            cache_dir: Diretório para cache
            pixabay_key: Chave da API Pixabay (opcional)
            unsplash_key: Chave da API Unsplash (opcional)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.pixabay_key = pixabay_key
        self.unsplash_key = unsplash_key

        self.cache_ttl = timedelta(days=30)

    def _get_cache_path(self, manufacturer: str, model: str) -> Path:
        """Gera caminho do cache para um modelo"""
        cache_name = f"{manufacturer}_{model}".lower().replace(" ", "_")
        return self.cache_dir / f"{cache_name}.json"

    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Verifica se o cache ainda é válido"""
        if not cache_path.exists():
            return False

        file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        return datetime.now() - file_time < self.cache_ttl

    def _load_cache(self, manufacturer: str, model: str) -> Optional[List[PublicImage]]:
        """Carrega imagens do cache se disponível"""
        cache_path = self._get_cache_path(manufacturer, model)

        if self._is_cache_valid(cache_path):
            with open(cache_path) as f:
                data = json.load(f)
                return [PublicImage(**img) for img in data]

        return None

    def _save_cache(self, manufacturer: str, model: str, images: List[PublicImage]):
        """Salva imagens em cache"""
        cache_path = self._get_cache_path(manufacturer, model)

        with open(cache_path, 'w') as f:
            json.dump(
                [
                    {
                        'url': img.url,
                        'source': img.source,
                        'license': img.license,
                        'title': img.title,
                        'attribution': img.attribution,
                        'thumbnail_url': img.thumbnail_url,
                    }
                    for img in images
                ],
                f,
                indent=2
            )

    async def _fetch_wikimedia(self, manufacturer: str, model: str) -> List[PublicImage]:
        """
        Busca imagens no Wikimedia Commons.

        Endpoint: https://commons.wikimedia.org/w/api.php
        Vantagem: Enorme acervo de carros, imagens de alta qualidade
        Limite: Rate limit suave
        """
        try:
            async with httpx.AsyncClient() as client:
                # Busca 1: por modelo específico
                query = f"{manufacturer} {model} car"

                params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'allimages',
                    'aiprop': 'url',
                    'aisort': 'timestamp',
                    'aidir': 'descending',
                    'aifrom': quote(query),
                    'ailimit': 10,
                }

                response = await client.get(self.WIKIMEDIA_API, params=params)
                data = response.json()

                images = []
                for img_data in data.get('query', {}).get('allimages', []):
                    # Busca metadados
                    file_name = img_data['name']

                    meta_params = {
                        'action': 'query',
                        'format': 'json',
                        'titles': f"File:{file_name}",
                        'prop': 'imageinfo|pageterms',
                        'iiprop': 'url|canonicaltitle',
                        'wbptterms': 'label|description',
                    }

                    meta_response = await client.get(
                        self.WIKIMEDIA_API,
                        params=meta_params,
                        timeout=5
                    )
                    meta_data = meta_response.json()

                    pages = meta_data.get('query', {}).get('pages', {})
                    for page_id, page_data in pages.items():
                        if 'imageinfo' in page_data:
                            img_info = page_data['imageinfo'][0]

                            images.append(PublicImage(
                                url=img_info['url'],
                                thumbnail_url=img_info['url'] + '?width=200',
                                source='wikimedia',
                                license='CC-BY-SA',
                                title=file_name,
                                attribution='Wikimedia Commons'
                            ))

                return images[:5]  # Retorna top 5

        except Exception as e:
            print(f"Erro ao buscar Wikimedia: {e}")
            return []

    async def _fetch_pixabay(self, manufacturer: str, model: str) -> List[PublicImage]:
        """
        Busca imagens no Pixabay.

        Requer API key (gratuita).
        Vantagem: Imagens livres de direitos
        Limite: 50 req/hora sem chave
        """
        if not self.pixabay_key:
            return []

        try:
            async with httpx.AsyncClient() as client:
                query = f"{manufacturer} {model} car"

                params = {
                    'q': query,
                    'key': self.pixabay_key,
                    'per_page': 3,
                    'image_type': 'photo',
                }

                response = await client.get(self.PIXABAY_API, params=params)
                data = response.json()

                images = []
                for hit in data.get('hits', []):
                    images.append(PublicImage(
                        url=hit['largeImageURL'],
                        thumbnail_url=hit['previewURL'],
                        source='pixabay',
                        license='Free to use',
                        title=hit.get('tags', ''),
                        attribution=f"Photo by {hit.get('user', 'Unknown')} on Pixabay"
                    ))

                return images

        except Exception as e:
            print(f"Erro ao buscar Pixabay: {e}")
            return []

    async def _fetch_unsplash(self, manufacturer: str, model: str) -> List[PublicImage]:
        """
        Busca imagens no Unsplash.

        Requer API key (gratuita).
        Vantagem: Excelente qualidade, legal para usar
        Limite: 50 req/hora
        """
        if not self.unsplash_key:
            return []

        try:
            async with httpx.AsyncClient() as client:
                query = f"{manufacturer} {model} car"

                headers = {
                    'Authorization': f'Client-ID {self.unsplash_key}'
                }

                params = {
                    'query': query,
                    'per_page': 3,
                    'order_by': 'relevance',
                }

                response = await client.get(
                    self.UNSPLASH_API,
                    params=params,
                    headers=headers
                )
                data = response.json()

                images = []
                for result in data.get('results', []):
                    images.append(PublicImage(
                        url=result['urls']['regular'],
                        thumbnail_url=result['urls']['thumb'],
                        source='unsplash',
                        license='Unsplash License (Free)',
                        title=result.get('description', ''),
                        attribution=f"Photo by {result['user']['name']} on Unsplash"
                    ))

                return images

        except Exception as e:
            print(f"Erro ao buscar Unsplash: {e}")
            return []

    async def fetch_images(
        self,
        manufacturer: str,
        model: str,
        year: Optional[int] = None,
        force_refresh: bool = False
    ) -> List[PublicImage]:
        """
        Busca imagens públicas para um modelo de carro.

        Ordem de preferência:
        1. Wikimedia Commons (melhor qualidade e legibilidade)
        2. Unsplash (opcional, requer chave)
        3. Pixabay (opcional, requer chave)

        Args:
            manufacturer: Nome do fabricante (Ferrari, Lamborghini, etc)
            model: Modelo do carro (F40, Countach, etc)
            year: Ano (opcional, para buscar mais específico)
            force_refresh: Ignora cache e busca novamente

        Returns:
            Lista de imagens públicas
        """
        # Verificar cache
        if not force_refresh:
            cached = self._load_cache(manufacturer, model)
            if cached:
                return cached

        all_images = []

        # Busca em paralelo
        tasks = [
            self._fetch_wikimedia(manufacturer, model),
        ]

        # Adiciona APIs opcionais se tiver chaves
        if self.pixabay_key:
            tasks.append(self._fetch_pixabay(manufacturer, model))
        if self.unsplash_key:
            tasks.append(self._fetch_unsplash(manufacturer, model))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combina resultados
        for result in results:
            if isinstance(result, list):
                all_images.extend(result)

        # Remove duplicatas por URL
        seen_urls = set()
        unique_images = []
        for img in all_images:
            if img.url not in seen_urls:
                unique_images.append(img)
                seen_urls.add(img.url)

        # Cache (se encontrou algo)
        if unique_images:
            self._save_cache(manufacturer, model, unique_images)

        return unique_images[:10]  # Retorna top 10

    async def update_all_cars_images(self, cars_data: List[Dict]) -> Dict[str, int]:
        """
        Atualiza imagens para todos os carros.

        Útil para job agendado.

        Args:
            cars_data: Lista de dicts com {manufacturer, model, year}

        Returns:
            Stats de quantas foram atualizadas
        """
        stats = {
            'total': len(cars_data),
            'success': 0,
            'error': 0,
            'from_cache': 0
        }

        for car in cars_data:
            try:
                # Verifica cache
                cache_path = self._get_cache_path(car['manufacturer'], car['model'])
                if self._is_cache_valid(cache_path):
                    stats['from_cache'] += 1
                    continue

                # Busca
                images = await self.fetch_images(
                    car['manufacturer'],
                    car['model'],
                    car.get('year')
                )

                if images:
                    stats['success'] += 1
                else:
                    stats['error'] += 1

                # Rate limiting (evita sobrecarregar APIs)
                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"Erro ao buscar imagens para {car}: {e}")
                stats['error'] += 1

        return stats


# Função de teste
async def test_service():
    """Testa o serviço de imagens"""
    service = ManufacturerImageService()

    # Busca imagens do Ferrari F40
    images = await service.fetch_images("Ferrari", "F40", 1987)

    print(f"🖼️  Encontradas {len(images)} imagens:")
    for img in images[:3]:
        print(f"  - {img.source}: {img.title}")
        print(f"    URL: {img.url}")
        print()
