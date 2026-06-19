#!/usr/bin/env python3
"""
Plan C — Demo fallback para Sesión 1 del curso IA Operativa.
Simula el workflow de n8n sin necesidad de n8n, OpenAI, ni Slack.

Funciona 100% offline. Solo necesita Python 3.
"""
import json, sys, os, time
from datetime import datetime

# ============================================================
# CONFIG (cámbialo si quieres)
# ============================================================
DEMO_MODE = "hook"  # "hook" = Demo 1 (workflow mágico) | "build" = Demo 3 (en vivo)

# ============================================================
# DEMO 1 — Workflow Mágico
# ============================================================
def demo_hook():
    print("\n" + "="*60)
    print("🎯 DEMO 1 — Workflow Mágico")
    print("="*60 + "\n")
    
    # PASO 1: Recibir mensaje
    mensaje = input("[1/5] Pega el mensaje del 'cliente':\n> ")
    print(f"\n📥 Recibido: {mensaje[:80]}...\n")
    time.sleep(1)
    
    # PASO 2: IA extrae datos (simulado con reglas)
    print("🤖 [2/5] IA analizando mensaje...")
    time.sleep(2)
    
    palabras = mensaje.lower()
    if any(w in palabras for w in ["urge", "caído", "roto", "error", "crítico", "frustrado"]):
        urgencia = "alta"
    elif any(w in palabras for w in ["duda", "consulta", "info", "información"]):
        urgencia = "baja"
    else:
        urgencia = "media"
    
    if any(w in palabras for w in ["servidor", "técnico", "bug", "error", "caído"]):
        categoria = "soporte"
    elif any(w in palabras for w in ["precio", "presupuesto", "venta", "comprar", "plan"]):
        categoria = "comercial"
    elif any(w in palabras for w in ["proyecto", "reunión", "cliente", "interno"]):
        categoria = "interna"
    else:
        categoria = "general"
    
    print(f"  → Categoría: {categoria}")
    print(f"  → Urgencia: {urgencia}")
    print(f"  → Resumen: {mensaje[:60]}...")
    time.sleep(1)
    
    # PASO 3: Guardar en Google Sheets (simulado)
    print(f"\n📊 [3/5] Guardando en Google Sheets...")
    time.sleep(1.5)
    fila = {
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "mensaje": mensaje,
        "categoria": categoria,
        "urgencia": urgencia,
        "resumen": mensaje[:80]
    }
    print(f"  → Fila añadida: {json.dumps(fila, indent=2)}")
    time.sleep(1)
    
    # PASO 4: Notificar Slack (simulado)
    print(f"\n🔔 [4/5] Notificando Slack...")
    time.sleep(1)
    print(f"  → #curso-ia-demo: Nuevo mensaje procesado")
    print(f"  → Categoría: {categoria} | Urgencia: {urgencia}")
    time.sleep(1)
    
    # PASO 5: Responder
    print(f"\n✅ [5/5] Respondiendo al webhook...")
    time.sleep(0.5)
    
    resultado = {
        "status": "ok",
        "procesado": True,
        "categoria": categoria,
        "urgencia": urgencia,
        "resumen": mensaje[:80],
        "tiempo_total": "12 segundos"
    }
    print(f"\n📦 RESPUESTA:\n{json.dumps(resultado, indent=2)}")
    print(f"\n⏱️  Tiempo total: ~12 segundos")
    print(f"💡 Antes: 2 horas. Ahora: 12 segundos.")
    print(f"📈 Ahorro: 99.8%\n")


# ============================================================
# DEMO 3 — Construcción en Vivo
# ============================================================
def demo_build():
    print("\n" + "="*60)
    print("🔧 DEMO 3 — Construcción en Vivo")
    print("="*60)
    print("(Clasificador inteligente de consultas)\n")
    
    consulta = input("¿Qué consulta ha recibido el equipo?\n> ")
    
    print("\n🔍 Paso 1: Recibir consulta ✅")
    time.sleep(0.5)
    
    print("🤖 Paso 2: IA categorizando...")
    time.sleep(2)
    
    # Reglas de categorización
    palabras = consulta.lower()
    if any(w in palabras for w in ["servidor", "error", "bug", "caído", "técnico", "código"]):
        categoria = "técnica"
        consejo = "Revisa logs del servidor y prioriza según impacto"
    elif any(w in palabras for w in ["precio", "presupuesto", "venta", "comprar", "plan", "demo"]):
        categoria = "comercial"
        consejo = "Prepara propuesta personalizada con pricing y casos de éxito"
    elif any(w in palabras for w in ["ayuda", "problema", "no funciona", "duda"]):
        categoria = "soporte"
        consejo = "Abre ticket y asigna según SLA del cliente"
    else:
        categoria = "interna"
        consejo = "Deriva al departamento correspondiente"
    
    print(f"\n  📌 Categoría detectada: {categoria.upper()}")
    print(f"  💡 Consejo: {consejo}")
    time.sleep(1)
    
    print("\n🚦 Paso 3: Router por categoría...")
    time.sleep(1)
    rutas = {"técnica": "→ IA Respuesta técnica", 
             "comercial": "→ IA Respuesta comercial",
             "soporte": "→ IA Respuesta soporte",
             "interna": "→ Notificar responsable"}
    print(f"  {rutas[categoria]}")
    time.sleep(1)
    
    print(f"\n✅ Paso 4: Respondiendo...")
    time.sleep(1)
    
    respuestas = {
        "técnica": f"Gracias por reportarlo. El equipo técnico revisará el incidente y te dará feedback en 2 horas.",
        "comercial": f"Te enviamos información sobre nuestros planes. ¿Te parece bien que te llame un comercial mañana?",
        "soporte": f"Hemos abierto un ticket de soporte. Te mantendremos informado.",
        "interna": f"Consulta registrada. Se deriva al departamento correspondiente."
    }
    
    print(f"\n📬 RESPUESTA GENERADA:")
    print(f"  \"{respuestas[categoria]}\"")
    print(f"\n⏱️  Tiempo total de construcción: 12 minutos")
    print(f"💡 Sin escribir código. Solo arrastrar nodos.\n")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("""
╔════════════════════════════════════════╗
║   CURSO IA OPERATIVA — DEMO FALLBACK   ║
║   Plan C: funciona sin internet 🚀     ║
╚════════════════════════════════════════╝
""")
    
    if "--hook" in sys.argv:
        demo_hook()
    elif "--build" in sys.argv:
        demo_build()
    else:
        print("Elige demo:")
        print("  python3 demo-fallback.py --hook    (Demo 1: Workflow Mágico)")
        print("  python3 demo-fallback.py --build   (Demo 3: Construcción en Vivo)")
