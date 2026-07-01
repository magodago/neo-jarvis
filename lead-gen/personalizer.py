#!/usr/bin/env python3
"""
NEO Email Personalizer v1
Genera emails personalizados para cada lead usando DeepSeek Flash.
"""
import json, csv, os, sys, time, urllib.request, re
from datetime import datetime

LEAD_DIR = os.path.join(os.path.dirname(__file__), "data")
OUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUT_DIR, exist_ok=True)

# Columnas del CSV
FIELDS = ["nombre","ciudad","tipo","web","email","mensaje_personalizado","asunto"]

def log(m):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}")

def get_ds_key():
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("DEEPSEEK_API_KEY="):
                    return line.split("=",1)[1].strip().strip('"\'').strip()
    return ""

def call_deepseek(prompt, max_tokens=300):
    """Call DeepSeek Flash API"""
    key = get_ds_key()
    if not key: return None
    
    data = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.8,
    }).encode()
    
    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        text = result["choices"][0]["message"]["content"].strip()
        # Clean markdown
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        return text
    except Exception as e:
        log(f"  DeepSeek error: {e}")
        return None

def generate_email(lead):
    """Generate personalized email for a lead"""
    nombre = lead.get("nombre","")
    ciudad = lead.get("ciudad","")
    tipo = lead.get("tipo","negocio")
    web = lead.get("web","No")
    
    prompt = f"""Eres NEO Labs, una agencia de diseño web premium en España. Genera un email de venta CORTO y PERSONALIZADO para:

Negocio: {nombre}
Tipo: {tipo}
Ciudad: {ciudad}
Web actual: {web if web and web != "No" else "NO TIENE WEB"}

REGLAS:
- Máximo 4 líneas, directo
- Tono cercano pero profesional
- Menciona el nombre del negocio y ciudad
- Ofrece: web premium desde 299€ (valor real 1.200€), diseño único por sector, lista en 48h
- Incluye CTA: que respondan al email para más info
- Si no tiene web: menciónalo como oportunidad
- Si tiene web básica: di que puedes mejorarla
- NO uses markdown, asteriscos ni negritas
- Firma: NEO Labs | neolabs.es

Devuelve SOLO el cuerpo del email, sin asunto."""
    
    email = call_deepseek(prompt)
    if not email:
        # Fallback
        web_text = "hemos visto que no tienes web" if (not web or web == "No") else "hemos visto tu web y podemos mejorarla"
        email = f"Hola, soy de NEO Labs. {web_text}. Creamos webs premium con diseño único para {tipo}s en {ciudad}. Desde 299€, lista en 48h. ¿Te interesa? Escríbenos y te enviamos una propuesta sin compromiso. Un saludo, NEO Labs."
    
    # Generate subject
    subj_prompt = f"Genera un asunto de email corto y atractivo (máx 8 palabras) para ofrecer una web premium a {nombre} en {ciudad}. Responde solo el asunto, sin comillas."
    asunto = call_deepseek(subj_prompt, max_tokens=50)
    if not asunto:
        asunto = f"Web premium para {nombre} - {ciudad}"
    
    return email.strip(), asunto.strip()

def process_csv(csv_path):
    """Process all leads in a CSV file"""
    leads = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(row)
    
    log(f"Procesando {len(leads)} leads de {csv_path}")
    
    results = []
    for i, lead in enumerate(leads):
        log(f"  [{i+1}/{len(leads)}] {lead.get('nombre','?')[:30]}...")
        email, asunto = generate_email(lead)
        lead["email_encontrado"] = lead.get("email", "")
        lead["asunto"] = asunto
        lead["mensaje_personalizado"] = email
        results.append(lead)
        time.sleep(1)  # Rate limit
    
    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    name = os.path.splitext(os.path.basename(csv_path))[0]
    out_path = os.path.join(OUT_DIR, f"{name}_personalizados_{ts}.csv")
    fieldnames = list(leads[0].keys()) + ["asunto","mensaje_personalizado"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(results)
    
    log(f"\n✓ Guardado: {out_path}")
    log(f"  Total: {len(results)} emails generados")
    
    # Print preview
    for r in results[:2]:
        print(f"\n--- {r.get('nombre','?')} ---")
        print(f"Asunto: {r.get('asunto','')}")
        print(f"Email: {r.get('mensaje_personalizado','')[:200]}...")
    
    return out_path

def main():
    import argparse
    parser = argparse.ArgumentParser(description="NEO Email Personalizer")
    parser.add_argument("--input", "-i", help="CSV de leads (o último generado)")
    args = parser.parse_args()
    
    if args.input:
        process_csv(args.input)
    else:
        # Find latest CSV
        csvs = sorted([f for f in os.listdir(LEAD_DIR) if f.endswith(".csv")], reverse=True)
        if not csvs:
            log("No hay CSVs en data/. Ejecuta scraper.py primero.")
            return
        process_csv(os.path.join(LEAD_DIR, csvs[0]))

if __name__ == "__main__":
    main()
