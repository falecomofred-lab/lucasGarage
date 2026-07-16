"""
Serviços da aplicação.

Os módulos de OCR/IA (ocr_service, ai_vision_service, manufacturer_image_service)
NÃO são importados automaticamente aqui de propósito: eles dependem de bibliotecas
pesadas (easyocr, etc.) e o app não precisa delas para funcionar.

Se um dia quiser usá-los, importe direto o módulo específico, ex:
    from src.services.ocr_service import CarOCRService
"""
