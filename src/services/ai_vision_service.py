"""
Serviço de identificação de carros por foto usando Google Gemini (IA).

Como funciona:
1. Lucas envia a foto da miniatura
2. Gemini analisa e retorna: nome, montadora, ano, cor, classe
3. O formulário é preenchido automaticamente

Requer GEMINI_API_KEY (grátis):
1. Acesse: https://aistudio.google.com/apikey
2. Clique "Create API Key"
3. Crie arquivo .env na raiz do projeto:
   GEMINI_API_KEY=sua-chave-aqui
"""

import os
import json
import base64
import httpx

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

PROMPT = """Analise esta foto de um carro em miniatura (escala 1:32).
Identifique o carro real que ela representa e responda APENAS com JSON válido, sem markdown:

{
  "name": "nome completo do modelo (ex: Ferrari F40)",
  "manufacturer": "nome da montadora (ex: Ferrari)",
  "year": ano de lançamento do modelo real (número, ex: 1987),
  "color": "cor principal da miniatura em português (ex: Vermelho)",
  "class": "uma destas opções: sports, classic, supercar, muscle, racing, luxury",
  "description": "descrição curta do carro real em português (1-2 frases)",
  "trivia": "uma curiosidade interessante sobre o carro em português (1 frase)",
  "confidence": "high, medium ou low"
}

Se não conseguir identificar com certeza, use confidence "low" e dê seu melhor palpite."""


async def identify_car_from_photo(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    """Envia a foto para o Gemini e retorna os dados identificados."""

    if not GEMINI_API_KEY:
        return {
            "error": "GEMINI_API_KEY não configurada",
            "help": "Pegue sua chave grátis em https://aistudio.google.com/apikey e adicione no arquivo .env: GEMINI_API_KEY=sua-chave"
        }

    image_b64 = base64.b64encode(image_bytes).decode()

    payload = {
        "contents": [{
            "parts": [
                {"text": PROMPT},
                {"inline_data": {"mime_type": mime_type, "data": image_b64}}
            ]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{GEMINI_URL}?key={GEMINI_API_KEY}",
                json=payload
            )
            response.raise_for_status()
            data = response.json()

        text = data["candidates"][0]["content"]["parts"][0]["text"]
        # Limpar possíveis marcações
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        result = json.loads(text)
        result["success"] = True
        return result

    except httpx.HTTPStatusError as e:
        return {"error": f"Erro da API Gemini: {e.response.status_code}", "detail": e.response.text[:200]}
    except (KeyError, json.JSONDecodeError) as e:
        return {"error": f"Resposta inesperada da IA: {str(e)[:100]}"}
    except Exception as e:
        return {"error": f"Erro: {str(e)[:100]}"}
