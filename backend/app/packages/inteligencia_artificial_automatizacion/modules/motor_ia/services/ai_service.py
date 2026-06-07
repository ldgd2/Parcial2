import json
import base64
import os
import re
from openai import AsyncOpenAI
from app.core.config import settings
from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.schemas.ai_schemas import AnalisisEstructuradoIA, FichaTecnica

# Cliente de OpenAI normal para evitar problemas de "Tool Use" en modelos gratuitos
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
)

async def analizar_transcripcion_whisper(
    texto_crudo: str, 
    categorias_disponibles: list[dict], 
    prioridades_disponibles: list[dict],
    vehiculo_info: str = "",
    evidencias_urls: list[str] = []
) -> AnalisisEstructuradoIA:
    """
    Analiza el reporte usando un prompt de JSON crudo para máxima compatibilidad.
    """
    cat_str = ", ".join([f"{c['id']}:{c['nombre']}" for c in categorias_disponibles])
    pri_str = ", ".join([f"{p['id']}:{p['nombre']}" for p in prioridades_disponibles])

    tiene_imagenes = len(evidencias_urls) > 0

    if tiene_imagenes:
        contexto_media = "Analiza el reporte de voz/texto Y LAS IMÁGENES adjuntas."
        regla_oro = "REGLA DE ORO: En el campo \"resumen_taller\", DEBES mencionar explícitamente qué observas en las fotos para respaldar tu diagnóstico."
    else:
        contexto_media = "Analiza ÚNICAMENTE el reporte de voz/texto transcrito. NO hay imágenes adjuntas."
        regla_oro = "REGLA DE ORO: Basa tu diagnóstico SOLO en lo que el cliente describió con palabras. NO menciones ni supongas imágenes, fotos ni evidencias visuales."

    system_prompt = f"""
Eres un mecánico experto en diagnóstico remoto. {contexto_media}
Debes responder ÚNICAMENTE con un objeto JSON.

{regla_oro}

REGLAS CRÍTICAS DE DIAGNÓSTICO:
1. PERSISTENCIA: Si un cliente reporta una avería (ej: "se me rompió la correa", "el motor humea"), asume que el daño está presente AHORA. No supongas que ya se arregló.
2. DEDUCCIÓN PROACTIVA: Si el reporte es vago (ej: "ayuda", "no prende"), analiza las fotos exhaustivamente. Busca fugas de líquidos, piezas rotas, deformaciones en neumáticos, o luces de advertencia en el tablero.
3. EXPLICACIONES TÉCNICAS: Debes buscar posibles explicaciones y causas raíz del problema, incluso si el cliente no las menciona. Tu objetivo es preparar al mecánico para lo que se va a encontrar.

VEHÍCULO: {vehiculo_info}
CATEGORÍAS (ID:Nombre): {cat_str}
PRIORIDADES (ID:Nombre): {pri_str}

Responde con este formato exacto:
{{
  "es_valida": true,
  "titulo_emergencia": "Título corto y profesional",
  "resumen_taller": "Menciona detalladamente lo que ves en las fotos y escuchas en el audio.",
  "id_categoria": {categorias_disponibles[0]['id'] if categorias_disponibles else 0},
  "id_prioridad": {prioridades_disponibles[0]['id'] if prioridades_disponibles else 0},
  "ficha_tecnica": {{
    "diagnostico_probable": "Explicación técnica de la falla.",
    "posibles_causas": ["Causa 1", "Causa 2"],
    "piezas_necesarias": ["p1", "p2"],
    "repuestos_sugeridos": ["r1", "r2"],
    "protocolo_tecnico": ["paso 1", "paso 2"]
  }},
  "recomendaciones_taller": "...",
  "motivo_rechazo": null
}}
"""

    full_prompt = f"{system_prompt}\n\nREPORTE DEL CLIENTE: {texto_crudo}"
    
    user_content = [
        {"type": "text", "text": full_prompt}
    ]
    
    print(f"Procesando {len(evidencias_urls)} imagenes para la IA...")
    for img_url in evidencias_urls[:5]:
        image_data = img_url
        if "/uploads/" in img_url or "localhost" in img_url or settings.APP_HOST in img_url or not img_url.startswith('http'):
            try:
                filename = img_url.split('/')[-1]
                file_path = os.path.join("uploads", filename)
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode('utf-8')
                        ext = filename.split('.')[-1].lower()
                        mime_ext = 'jpeg' if ext in ['jpg', 'jpeg'] else ext
                        image_data = f"data:image/{mime_ext};base64,{b64}"
                        print(f"Imagen cargada como base64: {filename}")
            except Exception as e:
                print(f"Error base64: {e}")


        user_content.append({
            "type": "image_url",
            "image_url": {"url": image_data}
        })

    try:
        print(f"Invocando IA ({settings.OPENROUTER_MODEL_NAME}) en modo COMPATIBLE...")
        
        # Override to a multimodal model if the default doesn't support images well
        model_name = settings.OPENROUTER_MODEL_NAME
        if tiene_imagenes and "llama" in model_name.lower():
            model_name = "google/gemini-flash-1.5-8b"
            print(f"Cambiando a {model_name} porque el modelo actual no soporta vision correctamente.")

        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": user_content},
            ],
            response_format={ "type": "json_object" } if "gemini" in model_name.lower() or "gpt" in model_name.lower() else None,
            timeout=60
        )
        
        content = response.choices[0].message.content
        import re
        import json
        # Limpiar posible basura de markdown
        clean_json = re.sub(r'```json\s*|\s*```', '', content).strip()
        data = json.loads(clean_json)
        
        # Asegurar que motivo_rechazo no sea nulo
        if "motivo_rechazo" not in data or data["motivo_rechazo"] is None:
            data["motivo_rechazo"] = ""
            
        return AnalisisEstructuradoIA(**data)

    except Exception as e:
        import traceback
        print(f"Fallo total de IA (Timeout o Error): {str(e)}")
        traceback.print_exc()
        
        # Fallback manual para no bloquear la app
        return AnalisisEstructuradoIA(
            es_valida=True,
            titulo_emergencia="Reporte en Proceso",
            resumen_taller="La IA no pudo procesar el reporte, pero se ha registrado la solicitud.",
            id_categoria=categorias_disponibles[0]['id'] if categorias_disponibles else 1,
            id_prioridad=prioridades_disponibles[1]['id'] if len(prioridades_disponibles) > 1 else 1,
            ficha_tecnica=FichaTecnica(
                diagnostico_probable="Pendiente de revisión manual",
                posibles_causas=["No se pudo determinar vía IA"],
                piezas_necesarias=[],
                repuestos_sugeridos=[],
                protocolo_tecnico=["Revisar evidencias físicas"]
            ),
            recomendaciones_taller="Verificar el vehículo físicamente.",
            motivo_rechazo=""
        )
