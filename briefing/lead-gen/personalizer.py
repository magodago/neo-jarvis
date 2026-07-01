#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Personalizador de emails NEO - Estilo premium con conversion maxima"""
import json, csv, os, sys, urllib.request

BASE = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE, "data")
OUTPUT_DIR = os.path.join(BASE, "output")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# DeepSeek API
_env_key = os.environ.get("DEEPSEEK_API_KEY", "sk-fallback")
DEEPSEEK_KEY = _env_key
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-v4-flash"

LANDING = "https://magodago.github.io/neo-jarvis/landing/"

NEGOCIO = {
    "restaurantes": "restaurante",
    "clinicas": "centro medico",
    "abogados": "despacho de abogados",
    "talleres": "taller mecanico",
    "peluquerias": "peluqueria",
}

def generar_email(lead):
    nombre = lead["nombre"]
    ciudad = lead.get("ciudad", "tu zona")
    sector = lead["sector"]
    negocio = NEGOCIO.get(sector, "negocio")

    prompt = (
        "Escribe un email de ventas REAL para " + nombre + ", un " + negocio + " en " + ciudad + ".\n"
        "Formato:\n"
        "ASUNTO: [asunto]\n"
        "CUERPO: [texto]\n\n"
        "REGLAS ESTRICTAS:\n"
        "- NO uses ** ni * ni markdown. Solo texto plano.\n"
        "- Suena a persona real, no a plantilla. Nada de 'listo para crecer' ni frases hechas.\n"
        "- Menciona el negocio por su nombre: " + nombre + "\n"
        "- 3 planes: BASICA 299EUR, PREMIUM 599EUR (el mas popular), PREMIUM+CURSO 699EUR\n"
        "- Link ejemplos: " + LANDING + "\n"
        "- Pide respuesta, no llamada. 'Respondeme a este email y te paso ejemplos'\n"
        "- Maximo 80 palabras en el cuerpo\n"
        "- Firma: -- David | NEO Labs | neolabs.es\n"
        "- Espanol correcto sin faltas de ortografia"
    )

    try:
        payload = json.dumps({
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.5,
        }).encode()
        req = urllib.request.Request(
            API_URL, data=payload,
            headers={
                "Authorization": "Bearer " + DEEPSEEK_KEY,
                "Content-Type": "application/json",
            },
        )
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        content = result["choices"][0]["message"]["content"]

        if "ASUNTO:" in content and "CUERPO:" in content:
            parts = content.split("CUERPO:", 1)
            subj = parts[0].replace("ASUNTO:", "").strip()
            body = parts[1].strip()
        elif "|" in content:
            parts = content.split("|", 1)
            subj = parts[0].strip()
            body = parts[1].strip()
        else:
            subj = nombre + " - Tu web profesional desde 299EUR"
            body = content
        return subj, body
    except Exception as e:
        print("  API err " + nombre + ": " + str(e))
        return fallback(nombre, ciudad, negocio, sector)

def fallback(nombre, ciudad, negocio, sector):
    subj = nombre + ", tu web profesional desde 299EUR"
    body = (
        "Hola, soy David de NEO Labs.\n\n"
        "Hemos disenado webs para " + negocio + "s como " + nombre
        + " en " + ciudad + " y queremos ofrecerte lo mismo.\n\n"
        "Nuestros planes:\n"
        "* BASICA 299EUR - Web responsive + SEO + formulario + hosting\n"
        "* PREMIUM 599EUR - Diseno premium + SEO completo + blog + panel (el mas popular)\n"
        "* PREMIUM+CURSO 699EUR - Todo + curso IA Operativa (valor 297EUR)\n\n"
        "Ver ejemplos: " + LANDING + "\n\n"
        "10 minutos sin compromiso para ensenarte lo que podemos hacer.\n\n"
        "Saludos,\n"
        "-- David | Equipo NEO Labs\n"
        "neolabs.es"
    )
    return subj, body

def personalizar_todos():
    csv_path = os.path.join(DATA_DIR, "leads.csv")
    if not os.path.exists(csv_path):
        print("No hay leads. Ejecuta scraper.py primero.")
        return []
    with open(csv_path, "r", encoding="utf-8") as f:
        leads = list(csv.DictReader(f))
    print("Personalizando " + str(len(leads)) + " emails...")
    emails = []
    for i, lead in enumerate(leads):
        nombre = lead["nombre"]
        print("  [" + str(i + 1) + "/" + str(len(leads)) + "] " + nombre + "...", end=" ", flush=True)
        subj, body = generar_email(lead)
        emails.append({
            "nombre": nombre,
            "email_destino": lead.get("email", ""),
            "asunto": subj,
            "cuerpo": body,
            "sector": lead.get("sector", ""),
            "ciudad": lead.get("ciudad", ""),
        })
        print("OK")
    csv_out = os.path.join(OUTPUT_DIR, "emails.csv")
    with open(csv_out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "nombre", "email_destino", "asunto", "cuerpo", "sector", "ciudad",
        ])
        w.writeheader()
        w.writerows(emails)
    print("\n" + str(len(emails)) + " emails generados en " + csv_out)
    return emails

if __name__ == "__main__":
    personalizar_todos()
