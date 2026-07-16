"""
Serviço de OCR para identificação automática de carros em miniaturas.

Usa EasyOCR para extrair texto da imagem e Claude para contexto inteligente.
"""

import easyocr
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass
from PIL import Image
import re
from datetime import datetime

@dataclass
class CarIdentification:
    """Resultado de identificação de um carro"""
    model_name: str
    manufacturer: str
    year: Optional[int] = None
    confidence: float = 0.0
    raw_text: str = ""
    extracted_features: Dict = None

    def __post_init__(self):
        if self.extracted_features is None:
            self.extracted_features = {}


class CarOCRService:
    """Serviço de OCR para identificar carros em imagens de miniaturas"""

    def __init__(self, languages: List[str] = None):
        """
        Inicializa o leitor OCR.

        Args:
            languages: Idiomas para OCR (default: português + inglês)
        """
        self.languages = languages or ['pt', 'en']
        # Inicializa lazy para não carregar desnecessariamente
        self._reader = None

    @property
    def reader(self):
        """Inicializa o reader apenas quando necessário (lazy loading)"""
        if self._reader is None:
            self._reader = easyocr.Reader(
                self.languages,
                gpu=False  # Ativar GPU se disponível
            )
        return self._reader

    async def extract_text_from_image(self, image_path: str) -> Dict:
        """
        Extrai todo o texto da imagem usando OCR.

        Args:
            image_path: Caminho da imagem

        Returns:
            Dicionário com texto extraído e confiança
        """
        try:
            results = self.reader.readtext(image_path, detail=1)

            # Agrupa por confiança
            texts = []
            for detection in results:
                text = detection[1]
                confidence = detection[2]

                # Filtra detecções com confiança baixa
                if confidence > 0.3:
                    texts.append({
                        'text': text,
                        'confidence': confidence
                    })

            full_text = ' '.join([t['text'] for t in texts])
            avg_confidence = sum([t['confidence'] for t in texts]) / len(texts) if texts else 0

            return {
                'success': True,
                'raw_text': full_text,
                'texts': texts,
                'average_confidence': avg_confidence
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'raw_text': '',
                'texts': []
            }

    def _parse_car_info(self, text: str) -> Dict:
        """
        Parse do texto OCR para extrair informações do carro.

        Tenta identificar:
        - Marca (Ferrari, Lamborghini, Porsche, etc)
        - Modelo (F40, Countach, 911, etc)
        - Ano
        - Geração

        Args:
            text: Texto extraído via OCR

        Returns:
            Dicionário com informações extraídas
        """
        text_upper = text.upper()

        # Dicionário de marcas conhecidas
        known_brands = {
            'FERRARI': ['F40', 'F50', '488', '812', 'TESTAROSSA', 'DAYTONA', '250'],
            'LAMBORGHINI': ['COUNTACH', 'DIABLO', 'MURCIÉLAGO', 'AVENTADOR'],
            'PORSCHE': ['911', '935', '959', 'CARRERA'],
            'BUGATTI': ['VEYRON', 'CHIRON'],
            'MCLAREN': ['F1', 'MP4', 'SENNA'],
            'FORD': ['MUSTANG', 'GT40'],
            'CHEVROLET': ['CORVETTE', 'CAMARO'],
            'JAGUAR': ['E-TYPE', 'XJ220'],
            'MERCEDES': ['300SL', 'AMG', 'SLS'],
            'BMW': ['M1', 'M3', 'M5'],
            'AUDI': ['R8', 'SPORT'],
        }

        identified_brand = None
        identified_model = None

        # Tenta encontrar marca e modelo
        for brand, models in known_brands.items():
            if brand in text_upper:
                identified_brand = brand
                # Procura pelo modelo da marca
                for model in models:
                    if model in text_upper:
                        identified_model = model
                        break
                break

        # Tenta extrair ano (4 dígitos entre 1900-2100)
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        year = int(year_match.group()) if year_match else None

        # Tenta extrair escala (1:XX)
        scale_match = re.search(r'1\s*:\s*(\d+)', text)
        scale = scale_match.group(0) if scale_match else "1:32"

        return {
            'brand': identified_brand,
            'model': identified_model,
            'year': year,
            'scale': scale,
            'text_contains_number_plate': 'PLACA' in text_upper or 'PLATE' in text_upper
        }

    async def identify_car(self, image_path: str) -> CarIdentification:
        """
        Identifica um carro na imagem.

        Pipeline:
        1. Extrai texto via OCR
        2. Parse para extrair marca/modelo
        3. Valida contra banco de conhecimento
        4. Retorna identificação com confiança

        Args:
            image_path: Caminho da imagem

        Returns:
            CarIdentification com resultado
        """
        # Step 1: OCR
        ocr_result = await self.extract_text_from_image(image_path)

        if not ocr_result['success']:
            return CarIdentification(
                model_name="Unknown",
                manufacturer="Unknown",
                confidence=0.0,
                raw_text=ocr_result.get('error', '')
            )

        raw_text = ocr_result['raw_text']

        # Step 2: Parse
        parsed = self._parse_car_info(raw_text)

        # Step 3: Construir resultado
        brand = parsed['brand'] or "Unknown"
        model = parsed['model'] or "Unknown"
        full_name = f"{brand} {model}".strip()

        # Confiança baseada em:
        # - OCR confidence (70%)
        # - Identificação de marca/modelo (30%)
        ocr_confidence = ocr_result.get('average_confidence', 0)
        parse_confidence = 1.0 if parsed['brand'] else 0.3

        total_confidence = (ocr_confidence * 0.7) + (parse_confidence * 0.3)

        return CarIdentification(
            model_name=full_name,
            manufacturer=brand,
            year=parsed['year'],
            confidence=min(total_confidence, 1.0),
            raw_text=raw_text,
            extracted_features=parsed
        )

    async def batch_identify(self, image_paths: List[str]) -> List[CarIdentification]:
        """
        Identifica múltiplos carros.

        Args:
            image_paths: Lista de caminhos de imagens

        Returns:
            Lista de CarIdentification
        """
        results = []
        for path in image_paths:
            result = await self.identify_car(path)
            results.append(result)
        return results


# Função utilitária para teste rápido
async def test_ocr(image_path: str):
    """Testa OCR em uma imagem"""
    service = CarOCRService()
    result = await service.identify_car(image_path)

    print(f"🎯 Identificação: {result.model_name}")
    print(f"📊 Confiança: {result.confidence:.1%}")
    print(f"📝 Texto bruto: {result.raw_text}")
    print(f"🔍 Características: {result.extracted_features}")

    return result
