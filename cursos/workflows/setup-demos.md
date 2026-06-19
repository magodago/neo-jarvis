# Guía de Setup Técnico — Sesión 1

## Lo que necesitas ANTES de la sesión

---

## 1. n8n funcionando

```bash
# Ver si ya está corriendo
curl http://localhost:5678/healthz
# Si responde {"status":"ok"} → ya está

# Si no, arrancarlo:
n8n start --port=5678
# Acceder: http://localhost:5678
```

**Configurar cuenta owner** (la primera vez):
1. Abrir http://localhost:5678
2. Crear usuario: `david@neolabs.com` / contraseña que uses
3. Ve a Settings → API → Generate API Key (opcional, para imports)

---

## 2. Importar los workflows

Opción A — Desde la UI de n8n:
1. Abrir http://localhost:5678
2. Workflows → Add Workflow → Import from File
3. Seleccionar el JSON correspondiente

Opción B — Desde terminal (si tienes API key):
```bash
curl -X POST http://localhost:5678/rest/workflows \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: tu-api-key" \
  -d @workflows/demo1-workflow-magico.json
```

**Workflows a importar:**
| Archivo | Demo | Para qué |
|---------|------|----------|
| `demo1-workflow-magico.json` | Hook inicial | Recibir → IA extraer → Sheets → Slack |
| `demo3-construccion-vivo.json` | Construcción en vivo | Clasificar consultas por categoría |

---

## 3. Configurar credenciales

**OpenAI / Claude** (necesitas al menos una):
1. Settings → Credentials → Add
2. Tipo: OpenAI (o Anthropic si usas Claude)
3. API Key: la que tengas
4. Nombre: "IA Curso"

**Google Sheets** (para Demo 1):
1. Credentials → Add → Google Sheets
2. OAuth: "Sign in with Google"
3. Usa tu cuenta de Gmail (formulasia76@gmail.com o la que uses)
4. Crea una hoja nueva: https://sheets.new
5. Nómbrala: "Curso IA - Demo 1"
6. Copia el ID de la hoja (de la URL: /spreadsheets/d/[ID]/edit)
7. En el workflow Demo 1, edita el nodo "Guardar en Sheets" y pega el Sheet ID

**Slack** (para Demo 1):
1. Crea un canal en tu Slack: `#curso-ia-demo`
2. Credentials → Add → Slack
3. "Sign in with Slack" → selecciona el workspace
4. En el workflow Demo 1, edita "Notificar Slack" → pon el channel name

---

## 4. Probar Demo 1 (el hook)

```bash
# Enviar mensaje de prueba al workflow
curl -X POST http://localhost:5678/webhook/curso-ia-demo1 \
  -H "Content-Type: application/json" \
  -d '{
    "mensaje": "El cliente García está frustrado porque el proyecto lleva 2 semanas retrasado. Necesitamos una reunión urgente para re-planificar."
  }'
```

**Qué debería pasar:**
1. Webhook recibe el mensaje ✅
2. IA extrae: categoría, urgencia, resumen ✅
3. Google Sheets guarda una fila ✅
4. Slack notifica en #curso-ia-demo ✅
5. Webhook responde con los datos extraídos ✅

**Si falla:**
- ¿OpenAI key configurada? → Ve a Credentials
- ¿Google Sheets autenticado? → Revisa OAuth
- ¿Slack channel existe? → Crea #curso-ia-demo
- ¿Los nodos tienen la credencial asignada? → Edita nodo → Credential

---

## 5. Probar Demo 3 (construcción en vivo)

```bash
curl -X POST http://localhost:5678/webhook/curso-ia-demo3 \
  -H "Content-Type: application/json" \
  -d '{"consulta": "El servidor de producción lleva caído 2 horas"}'
```

Debería responder con categoría "tecnica" y una respuesta.

```bash
curl -X POST http://localhost:5678/webhook/curso-ia-demo3 \
  -H "Content-Type: application/json" \
  -d '{"consulta": "Quiero información sobre el plan premium"}'
```

Debería responder con categoría "comercial".

---

## 6. Tener backups por si falla Internet

**Plan B — Demo grabada:**
Graba un video de 30 segundos del workflow funcionando. Si el directo falla, lo pones.

**Plan C — Script Python (sin n8n):**
```bash
# Si n8n se cae, usas este script directamente
python3 ~/neo-jarvis/cursos/workflows/demo-fallback.py
```

(Voy a crear ese script a continuación)

---

## 7. El día de la sesión (checklist rápido)

- [ ] n8n corriendo: `curl http://localhost:5678/healthz`
- [ ] Demo 1 probada con mensaje de prueba
- [ ] Demo 3 probada con mensaje de prueba
- [ ] Ventanas preparadas en el escritorio (Slack, Sheets, n8n, Postman/curl)
- [ ] Google Sheets abierta y visible
- [ ] Canal de Slack abierto y visible
- [ ] Backup grabado por si falla
- [ ] Proyector funcionando
- [ ] Internet (plan B: hotspot móvil)
