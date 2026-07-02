#!/usr/bin/env python3
"""Test DeepSeek personalization"""
import json, urllib.request, os, sys, time

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
print(f"Key length: {len(DEEPSEEK_KEY)}")

if len(DEEPSEEK_KEY) < 10:
    print("No key!")
    sys.exit(1)

# Test DeepSeek personalization
prompt = """Escribe un email de ventas CORTO y HUMANO para La Taberna de Peñalver, un restaurante en Madrid.

REGLAS ESTRICTAS:
- El email debe SONAR a persona real escribiendo a otra persona. Nada de marketing, nada de frases hechas.
- Sin ** ni * ni markdown. Texto plano.
- Máximo 4 líneas en el cuerpo.
- Menciona el negocio por su nombre.
- NO pongas precios ni planes. Eso se habla después.
- Pide respuesta, no llamada: "responde a este mail y te paso ejemplos"
- Firma: -- David | NEO Labs
- Español correcto, natural, como hablarías con otro empresario.

FORMATO:
ASUNTO: [asunto corto]
CUERPO: [3-4 líneas]"""

payload = json.dumps({
    "model": "deepseek-v4-flash",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 300,
    "temperature": 0.7,
}).encode()

req = urllib.request.Request(
    "https://api.deepseek.com/v1/chat/completions",
    data=payload,
    headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
)

try:
    resp = urllib.request.urlopen(req, timeout=20)
    result = json.loads(resp.read())
    content = result["choices"][0]["message"]["content"]
    print("RESPUESTA DeepSeek:")
    print(content)
    print()
    
    if "ASUNTO:" in content and "CUERPO:" in content:
        print("✅ Formato correcto!")
    else:
        print("⚠️ Formato inesperado")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
