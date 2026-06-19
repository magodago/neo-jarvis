# IA Operativa — Sesión 1: Fundamentos y Estrategia

**Duración:** 3.5h (210 min)
**Formato:** 50% teoría → 25% demo → 25% taller práctico

---

## 1. HOOK INICIAL (00:00-00:10)

### 📍 Escena
Entras, pones el crono. Sin introducciones largas. Directo a la demo.

### 🎬 Guión del instructor

> "Voy a hacer algo rápido. ¿Alguien tiene un proceso tedioso que haga cada semana?"
>
> *(Esperas 5 segundos. Alguien dirá algo. Si no, usas el tuyo)*
>
> "Vale. Cada semana recojo feedback del equipo, lo paso a Excel, hago un resumen para dirección. Me lleva 2 horas."
>
> *(Abres pantalla compartida. Muestras n8n ya preparado)*
>
> "Voy a hacer eso ahora mismo en 30 segundos."
>
> *(Ejecutas el flujo. Envías un correo de prueba. El agente: lee el correo, extrae el feedback con IA, lo pasa a Google Sheets, genera un resumen ejecutivo y lo envía a Slack)*
>
> *(Silencio de 3 segundos mientras lo procesan)*
>
> "Eso no es el futuro. Es lo que puedes hacer esta tarde cuando llegues a tu mesa."
>
> *(Pasas a la siguiente slide)*

### 🛠 Demo 1: "El workflow mágico" (preparación)

**Qué necesitas tener preparado ANTES de la sesión:**
- n8n corriendo en local o cloud (Render)
- Un workflow que haga: recibir email → IA extrae datos → Google Sheets → Slack
- Email de prueba ya escrito
- Slack workspace con un canal de prueba
- Google Sheets con columnas preparadas

**Script del flujo n8n:**
```
1. Webhook node (recibe POST con email)
2. AI node (Claude/GPT): "Extrae los siguientes campos del correo: [asunto, remitente, categoría, acción requerida, urgencia]. Devuelve JSON."
3. Google Sheets node: añade fila con los datos extraídos
4. Slack node: envía resumen a #feedback-ia
5. Respond to webhook: devuelve JSON con resultado
```

**Si falla:** Ten un backup grabado en video.

---

## 2. IA SIN HYPE: QUÉ ES REALMENTE (00:10-00:30)

### 📍 Slides

| Slide | Contenido | Notas del instructor |
|-------|-----------|---------------------|
| T1 | Título: "IA sin hype" — Fondo negro, texto dorado grande | "Vamos a quitar todo el humo" |
| T2 | **Mito 1:** "La IA va a sustituirte" → **Realidad:** "La IA va a sustituir TAREAS, no TRABAJOS" | Ejemplo: "Nadie fue sustituido por Excel. Pero los que sabían Excel valían más." |
| T3 | **Mito 2:** "La IA alucina, no es fiable" → **Realidad:** "Como un becario con acceso ilimitado. Supervisas, no delegas ciegamente." | "El 80% de los errores de IA son errores de prompting, no de la IA." |
| T4 | **Mito 3:** "Es solo ChatGPT" → **Realidad:** "ChatGPT es un asistente. La IA es un ecosistema." | |
| T5 | **Los 3 tipos de IA que importan hoy** | Tarjeta visual con iconos |
| T6 | **Generativa:** Texto, imagen, código, audio. Crea contenido nuevo. | Demo breve: mismo prompt en GPT y Claude |
| T7 | **Predictiva:** Datos → patrones → forecasts. No crea, analiza. | "Cuando Amazon te recomienda, eso es predictiva." |
| T8 | **Agentes:** Observan → razonan → actúan. Automatización autónoma. | "El workflow del principio. Eso es un agente." |
| T9 | **Los 3 resolviendo el mismo problema** | Split screen con 3 casos paralelos |

### 🎬 Guión

> **Slide T2:**
> "Primer mito: 'la IA va a sustituirte'. Llevamos 2 años oyéndolo. En 2023 se destruyeron 0 empleos netos por IA en España. Se CREARON 45.000 empleos nuevos relacionados con IA.
>
> La IA no sustituye personas. Sustituye tareas repetitivas. Lo que pasó con Excel en los 90: los que sabían Excel valían más. Los que no, perdieron valor. La IA es exactamente lo mismo."
>
> **Slide T5-T8:**
> "Hay 3 tipos de IA que necesitas conocer. No 50. No los 500 de Gartner. TRES.
>
> **Generativa** — la que crea contenido. ChatGPT, Claude, Midjourney. Escribir un email, generar una imagen, redactar un informe.
>
> **Predictiva** — la que analiza datos y encuentra patrones. Detectar fraude, predecir ventas, segmentar clientes. No crea, descubre.
>
> **Agentes** — la que ACTÚA. No solo responde, hace cosas. Conecta APIs, toma decisiones, ejecuta procesos. Esto es lo que va a cambiar tu trabajo este año."

### 🛠 Demo 2: El mismo problema, 3 enfoques

**Preparación:** Ten 3 ventanas abiertas con:
1. **Generativa:** ChatGPT con un prompt para resumir un documento largo
2. **Predictiva:** Una hoja de cálculo con forecast de ventas generado por IA
3. **Agentes:** n8n con workflow funcionando

**Problema:** "Un cliente envía un correo quejándose de un retraso"

1. **Generativa:** Pides a ChatGPT que redacte una respuesta profesional → genera el email en 3s
2. **Predictiva:** El sistema analiza históricos de quejas y predice probabilidad de cancelación → 87%
3. **Agentes:** El agente recibe el correo, busca el pedido en el CRM, comprueba estado de envío, redacta respuesta con datos concretos y la envía para aprobación → 45s vs 20min

---

## 3. MAPA DE OPORTUNIDADES (00:30-01:00)

### 📍 Slides

| Slide | Contenido | Notas |
|-------|-----------|-------|
| T10 | "¿Dónde pongo esto?" — Título sección | Transición visual |
| T11 | **Reuniones:** Transcripción → Resumen → Action Items → CRM | "15h/semana → 2h" |
| T12 | **Correos:** Priorización → Drafting → Respuestas automáticas → Archivo | "Tu bandeja de entrada gestionada por IA" |
| T13 | **Documentación:** Actas → Informes → Documentación técnica → Propuestas | "Lo más infravalorado" |
| T14 | **Datos:** Análisis → Dashboards → Anomalías → Forecasts | "Sin saber SQL ni Python" |
| T15 | **Código:** Revisión → Generación → Debugging → Documentación | "Para los que tienen equipo técnico" |
| T16 | **Checklist de oportunidades** — documento imprimible | Se entrega a los alumnos |

### 🎬 Guión

> **Slide T11:**
> "Reuniones. 15 horas a la semana. 60 al mes. 720 al año.
>
> Con IA: grabas la reunión (o conectas el calendario), obtienes transcripción automática, resumen ejecutivo, action items con responsables y fechas, y se sincroniza con tu CRM o proyecto.
>
> No es teoría. Es lo que hago cada semana con el comité de empresa."
>
> *(Aquí puedes contar tu caso real: cómo automatizaste las actas del comité)*
>
> **Slide T16:**
> "Cada uno va a recibir una checklist. En los próximos 15 minutos, quiero que marquéis los procesos de vuestro trabajo que aparecen aquí. No hace falta que sepáis cómo automatizarlos todavía. Solo identificarlos.
>
> Tres reglas:
> 1. Si te aburre hacerlo → candidato
> 2. Si lo haces más de 1h/semana → candidato
> 3. Si requiere copiar-pegar datos → candidato"

### 📝 Taller 1: Checklist de oportunidades (25 min)

**Material:** Documento "Checklist de Automatización" (se entrega impreso y en PDF)

**Enunciado:**

```
CHECKLIST DE OPORTUNIDADES IA

Para cada proceso, marca:
[ ] Lo hago semanalmente
[ ] Me lleva >30min
[ ] Es repetitivo
[ ] Sigue siempre el mismo patrón
[ ] Me aburre / me frustra

PROCESOS:

☐ Resumir reuniones / generar actas
☐ Redactar correos profesionales
☐ Priorizar bandeja de entrada
☐ Escribir informes periódicos
☐ Analizar datos en Excel/Sheets
☐ Generar dashboards
☐ Revisar documentación
☐ Buscar información en múltiples fuentes
☐ Preparar presentaciones
☐ Hacer seguimiento de tareas
☐ Responder preguntas frecuentes
☐ Onboarding de nuevos miembros
☐ Traducir documentos
☐ Extraer datos de PDFs/imágenes
☐ Generar propuestas / presupuestos

Ahora: marca tus TOP 3 por IMPACTO esperado
1.
2.
3.
```

**Dinámica:** 10 min individual → 10 min compartir en parejas → 5 min puesta en común

---

## 4. PAUSA CAFÉ (01:00-01:15) ☕

---

## 5. CASOS REALES (01:15-01:45)

### 📍 Slides

| Slide | Contenido |
|-------|-----------|
| T17 | "De mi mesa a la tuya" — transición |
| T18 | **Caso 1:** Actas de comité de empresa |
| T19 | Antes: grabadora → desgrabar → resumir → enviar (4h) |
| T20 | Después: OMI graba → IA transcribe → IA resume → Slack (5 min) |
| T21 | Resultado: 95% de tiempo ahorrado, 0 errores de transcripción |
| T22 | **Caso 2:** Monitorización de proyectos con agentes |
| T23 | Antes: revisar 5 dashboards manualmente cada mañana (30min) |
| T24 | Después: agente revisa, detecta anomalías, alerta solo cuando algo va mal |
| T25 | **Caso 3:** Feedback de empleados → análisis de sentimiento |
| T26 | Antes: leer 50 respuestas, categorizar manualmente, buscar patrones |
| T27 | Después: IA categoriza, extrae tendencias, alerta sobre problemas |

### 🎬 Guión (esto es LO MÁS IMPORTANTE de la sesión)

**Importante:** Estos son TUS casos reales. No los memorices. Cuéntalos como lo que son: tu día a día. La autenticidad es lo que vende el curso.

> **Caso 1 — Actas de comité:**
> *(Cuéntalo con naturalidad, como si se lo contaras a un compañero)*
>
> "En el comité de empresa tenemos reuniones semanales. 2-3 horas. Yo era el que cogía notas, grababa con el móvil, luego pasaba horas desgrabando, resumiendo, enviando. 4 horas cada semana.
>
> Ahora: llevo el OMI puesto. Hablo. La IA transcribe en tiempo real. Cuando termina la reunión, en 5 minutos tengo: transcripción completa, resumen ejecutivo, action items. Lo envía a Slack automáticamente.
>
> 4 horas → 5 minutos. Eso son 200 horas al año."
>
> **Caso 2 — Monitorización de proyectos:**
> "Gestiono múltiples proyectos. Antes, cada mañana abría 5 dashboards diferentes. Jira, Azure DevOps, el CRM, el ERP, el panel de costes. 30 minutos de lectura.
>
> Ahora: un agente IT revisa todo cada hora. Si algo va mal (un ticket crítico sin asignar, un coste que se dispara, un hito que se retrasa), me avisa por Telegram. Si todo va bien, silencio. He pasado de 30 min/día a 0. Y encima no se me escapa nada."

---

## 6. TALLER: DIAGNÓSTICO DE TU EQUIPO (01:45-02:30)

### 📝 Taller 2: Mapa de automatización (45 min)

**Material:** Plantilla "Mapa de Automatización" (se entrega en papel + digital)

**Enunciado:**

```
MAPA DE AUTOMATIZACIÓN
Nombre: ___________  Departamento: ___________  Fecha: ___________

Para cada proceso que identificaste antes, completa:

PROCESO 1: ___________________________
  Tiempo actual: ___ h/semana
  Dolor (1-5): ___
  Complejidad técnica (1-5): ___  
  Impacto esperado (1-5): ___
  ¿Se puede hacer con herramientas sin código? Sí / No
  Prioridad: Alta / Media / Baja

PROCESO 2: ___________________________
  ...

TOP 3 PRIORIDADES (impacto × dolor ÷ complejidad):

1. _______________ (puntuación: ___)
2. _______________ (puntuación: ___)
3. _______________ (puntuación: ___)
```

**Dinámica:**
- 15 min: individual. Cada alumno completa su mapa
- 15 min: en parejas. Se explican mutuamente sus top 3
- 10 min: compartir los más interesantes en grupo
- 5 min: instructor recoge patrones

**Objetivo:** Que cada alumno se vaya con 3 procesos concretos que sabe que puede automatizar.

---

## 7. DEMO EN VIVO: AUTOMATIZACIÓN DESDE CERO (02:30-03:00)

### 🛠 Demo 3: Construir una automatización en vivo

**Preparación (CRÍTICA):**
- n8n abierto con proyecto vacío
- Una ventana con el proceso que vas a automatizar (elegido de los alumnos en el taller anterior, o uno de reserva)
- API keys ya configuradas en n8n
- **IMPORTANTE:** Ten el workflow ya creado en otra pestaña por si falla. Lo arrastras y dices "esto ya lo tenía preparado, vamos a verlo"

**Proceso a automatizar (elige uno de los alumnos, o usa este de reserva):**

> "Voy a coger el proceso de [nombre del alumno]. 'Cada semana recibo consultas por Slack, las copio a Excel, busco información, redacto respuesta y la envío'. Vamos a hacerlo en directo."

**Flujo en vivo:**
```
1. Slack webhook (recibe consulta) → 
2. AI node (analiza y categoriza la consulta) → 
3. HTTP node (busca info en fuente relevante) → 
4. AI node (redacta respuesta con los datos) → 
5. Google Sheets (registra la consulta y respuesta) → 
6. Slack (envía respuesta)
```

**Lo que dices mientras construyes:**
> "Primero, recibir la consulta. Añado un webhook de Slack... así. Segundo, necesito que entienda de qué va. Añado un nodo de IA, le digo 'categoriza esta consulta en técnica, comercial o soporte'... Tercero..."
>
> *(Construyes nodo a nodo, explicando cada paso. No más de 2 min por nodo)*

**Tiempo total de construcción:** 10-12 minutos
**Prueba:** Ejecutas con un mensaje de prueba. Funciona (o tienes el backup)

**Cierre de la demo:**
> "Eso que acabáis de ver, desde cero, son 12 minutos. Si lo hiciera todos los días, en una semana tendría 5 procesos automatizados. En un mes, mi trabajo sería otro."

---

## 8. CIERRE Y PREPARACIÓN (03:00-03:30)

### 📍 Slides

| Slide | Contenido |
|-------|-----------|
| T28 | "Resumen de hoy" — 3 puntos clave |
| T29 | **1.** La IA no es magia, es una herramienta más |
| T30 | **2.** Identifica procesos, no herramientas |
| T31 | **3.** Empieza por UN proceso, no por el ecosistema completo |
| T32 | **Ejercicio entre sesiones** |
| T33 | Traer 5 procesos documentados con: tiempo actual, dolor, pasos |
| T34 | "La semana que viene: herramientas. Vais a tocar." |
| T35 | Q&A — Diapositiva final con QR a comunidad |

### 🎬 Guión de cierre

> "Tres cosas que quiero que recordéis de hoy:
>
> Primera: la IA no es magia. Es una herramienta. Como Excel, como Slack. Cuanto antes la tratéis como tal, antes empezaréis a usarla de verdad.
>
> Segunda: el orden importa. Primero identificas el proceso. Luego piensas cómo automatizarlo. No al revés. La gente compra ChatGPT y luego busca problemas. Ese es el error.
>
> Tercera: empezad por UNO. Un solo proceso. Automatizadlo bien. Luego otro. En tres meses tendréis vuestro trabajo transformado.
>
> Entre hoy y la siguiente sesión: quiero que traigáis 5 procesos de vuestro trabajo documentados. No hace falta que sepáis cómo automatizarlos. Solo: qué hacéis, cuánto os lleva, qué pasos seguís.
>
> La semana que viene: herramientas. Vais a tocar código. Vais a escribir prompts. Vais a construir vuestro primer automatismo.
>
> ¿Preguntas?"

---

## 9. MATERIALES QUE ENTREGAS AL FINAL

- [ ] Presentación completa (PDF)
- [ ] Checklist de oportunidades IA
- [ ] Mapa de automatización (plantilla)
- [ ] Guía de recursos entre sesiones
- [ ] Enlace a comunidad privada

---

## 10. CHECKLIST DEL INSTRUCTOR (día antes)

- [ ] n8n funcionando y accesible
- [ ] Workflow "mágico" listo y probado
- [ ] Workflow de construcción en vivo listo (y backup)
- [ ] Cuentas demo: ChatGPT, Claude, n8n
- [ ] Proyector y sonido probados
- [ ] Slides cargadas y funcionando
- [ ] Plantillas impresas (o QR para descargar)
- [ ] Slack channel de prueba creado
- [ ] Google Sheets de prueba creado
- [ ] 3 ventanas preparadas (GPT, Sheets, n8n)
- [ ] Internet funcionando (plan B: hotspot móvil)
- [ ] Botella de agua 🫡
