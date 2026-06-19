# IA Operativa — Sesión 3: Flujos y Agentes

**Duración:** 3.5h (210 min)
**Formato:** 30% teoría → 30% demo → 40% taller práctico

---

## 1. APERTURA Y REVIEW (00:00-00:15)

### 📍 Slides

| Slide | Contenido |
|-------|-----------|
| T1 | "Bienvenidos al día 3" |
| T2 | **Review de automatismos** — los 3 mejores resultados de los alumnos |
| T3 | **El salto:** automatización → agente |
| T4 | Automatización: "Si X, entonces Y" (lineal) |
| T5 | Agente: "Observa, razona, decide, actúa" (autónomo) |

### 🎬 Guión

> "Habéis construido vuestro primer automatismo. Funciona. Os ahorra tiempo. Bien.
>
> Ahora: ¿y si en lugar de que el flujo haga siempre lo mismo, pudiera decidir QUÉ hacer según el contexto?
>
> Eso es la diferencia entre automatización y agente."
>
> *(Dibujas en pizarra o muestras slide)*
>
> "Automatización: llega un correo → siempre lo clasifica igual. Útil.
> Agente: llega un correo → decide si clasificarlo, responderlo, escalarlo o ignorarlo según su contenido. Siguiente nivel."
>
> "Hoy vais a construir vuestro primer agente."

---

## 2. DE LA AUTOMATIZACIÓN AL AGENTE (00:15-01:00)

### 📍 Slides

| Slide | Contenido | Notas |
|-------|-----------|-------|
| T6 | **¿Qué es un agente IA?** | Definición visual |
| T7 | Input → Razona → Decide → Usa herramientas → Actúa | Ciclo del agente |
| T8 | **NO es un chatbot** | "Un chat espera. Un agente hace." |
| T9 | **Componentes de un agente:** | |
| T10 | **Cerebro:** El modelo IA (GPT, Claude, etc.) | "Quién piensa" |
| T11 | **Herramientas:** APIs, bases de datos, Slack, correo | "Con qué actúa" |
| T12 | **Instrucciones:** Prompt del sistema, reglas, límites | "Cómo se comporta" |
| T13 | **Memoria:** Contexto, histórico, estado | "Qué recuerda" |
| T14 | **Puntos de control:** Supervisión humana | "Cuándo te pide permiso" |
| T15 | **Tipos de agentes:** | |
| T16 | **Asistente:** Responde cuando le llamas | "El más básico. Como Siri pero útil." |
| T17 | **Vigilante:** Monitoriza y alerta | "No actúa, solo avisa. Seguro." |
| T18 | **Ejecutor:** Hace tareas sin supervisión | "El que más tiempo ahorra. El que más cuidado requiere." |
| T19 | **Orquestador:** Coordina otros agentes | "El jefe de agentes." |
| T20 | Demo: mismo proceso 3 versiones | |

### 🛠 Demo 7: Mismo proceso, 3 niveles

**Preparación:** 3 workflows en n8n. Mismo proceso (gestión de incidencias), 3 niveles.

**Proceso:** "Un empleado reporta una incidencia por Slack"

**Nivel 1 — Automatización:** Recibe → categoriza (IA) → asigna a cola → notifica
```
Slack → IA clasifica → Asigna equipo → Slack "Incidencia registrada"
(Siempre igual. No importa el contexto.)
```

**Nivel 2 — Asistente:** Recibe → analiza → decide acción → ejecuta o pregunta
```
Slack → IA analiza gravedad →
  [URGENTE] → Crea ticket prioritario → Slack "Ticket #123 creado, asignado a soporte" → Email a soporte
  [NORMAL] → Crea ticket normal → Slack "Ticket #124 creado"
  [DUDA] → Slack "¿Puedes dar más detalles?"
```

**Nivel 3 — Agente ejecutor:** Autónomo con herramientas
```
Slack → Agente:
  1. Busca incidencias similares en base de conocimiento
  2. Si encuentra solución → la ofrece
  3. Si no → crea ticket, asigna responsable, programa seguimiento
  4. Slack con resumen + acción tomada
```

> "El nivel 1 lo construisteis la semana pasada. El nivel 2 es un asistente. El nivel 3 es un agente. Hoy vais al nivel 3."

---

## 3. DEMO EN VIVO: CONSTRUIR UN AGENTE (01:00-01:30)

### 🛠 Demo 8: Agente "Asistente de Proyecto" desde cero

**Preparación:** n8n con OpenAI/Claude node configurado. APIs de Slack y Google Calendar preparadas.

**El agente:**
```
INPUT: Mensaje por Slack: "¿Cómo va el proyecto ClienteX?"
PROCESO:
  1. Agente decide qué necesita saber
  2. Busca en Jira/ClickUp el estado del proyecto (API)
  3. Consulta el calendario para próximos hitos
  4. Cruza con presupuesto (Google Sheets)
  5. Genera resumen ejecutivo
OUTPUT: Slack con estado actual, riesgos y próximos pasos
```

**Construcción en vivo (15 min):**
```
Nodo 1 — Slack Webhook (recibe mención)
Nodo 2 — AI Agent (OpenAI/Claude con tools)
    Tool 1: HTTP Request → Jira API "get project status"
    Tool 2: HTTP Request → Google Calendar API "get upcoming milestones"
    Tool 3: HTTP Request → Google Sheets API "get budget data"
Nodo 3 — AI Agent (genera resumen)
Nodo 4 — Slack (envía respuesta)
```

> *(Construyes nodo a nodo. Explicas cada tool. Muestras cómo el agente "decide" qué tool usar según la pregunta)*

**Prueba:**
> "Ahora le pregunto: '¿Cómo va el proyecto ClienteX?'"
>
> *(El agente: busca en Jira → consulta calendario → lee presupuesto → genera respuesta)*
>
> "Y ahora: '¿Tenemos reunión mañana?'"
>
> *(El agente: decide NO consultar Jira, consulta SOLO el calendario, responde)*
>
> "¿Veis? El mismo agente, decisiones diferentes según la pregunta. Eso es lo que lo diferencia de una automatización."

---

## 4. PAUSA CAFÉ (01:30-01:45)

---

## 5. TALLER: DISEÑA TU PRIMER AGENTE (01:45-02:30)

### 📝 Taller 6: Diseño de agente (45 min)

**Material:** Plantilla "Diseño de Agente" (papel + digital)

**Parte 1: Diseño individual (20 min)**

```
PLANTILLA DE DISEÑO DE AGENTE

NOMBRE DEL AGENTE: _________________

PROPÓSITO: ¿Qué problema resuelve?
_____________________________________

TRIGGER: ¿Qué inicia al agente?
[ ] Horario programado
[ ] Evento (email, Slack, webhook)
[ ] Petición explícita
[ ] Cambio en un sistema

INPUT: ¿Qué información necesita?
_____________________________________

HERRAMIENTAS (qué APIs/sistemas necesita consultar):
1. _________________________________
2. _________________________________
3. _________________________________

RAZONAMIENTO: ¿Qué decisiones debe tomar?
_____________________________________

ACCIONES: ¿Qué hace cuando decide?
1. _________________________________
2. _________________________________
3. _________________________________

PUNTOS DE CONTROL (dónde necesita permiso humano):
1. _________________________________
2. _________________________________

OUTPUT: ¿Cómo y dónde entrega el resultado?
_____________________________________

LÍMITES: ¿Qué NO debe hacer?
_____________________________________

MODO FALLO: ¿Qué pasa si falla?
_____________________________________

MÉTRICA DE ÉXITO: ¿Cómo sé que funciona?
_____________________________________
```

**Parte 2: Compartir en parejas (15 min)**
- Cada uno explica su agente al compañero
- El compañero busca: ¿falta algo? ¿demasiado ambicioso? ¿punto ciego de seguridad?

**Parte 3: Puesta en común (10 min)**
- 3-4 alumnos presentan su diseño
- Instructor da feedback práctico

---

## 6. TALLER: IMPLEMENTA TU AGENTE (02:30-03:00)

### 📝 Taller 7: Implementación guiada (30 min)

**Preparación:** n8n con template precargado de agente básico. Cada alumno personaliza.

**Plantilla base (se la das ya hecha):**
```json
{
  "name": "Agente Base",
  "nodes": [
    { "type": "Webhook", "name": "Trigger" },
    { "type": "AI Agent", "name": "Cerebro",
      "config": {
        "model": "gpt-4o-mini",
        "systemPrompt": "Eres un asistente de proyecto. Ayudas a [personalizar].",
        "tools": ["http-request", "code"] 
      }
    },
    { "type": "Respond to Webhook", "name": "Respuesta" }
  ]
}
```

**Ejercicio:**
> "Partiendo de esta plantilla, quiero que:
> 1. Personalicéis el system prompt para vuestro caso
> 2. Añadáis AL MENOS una herramienta (HTTP request a una API real o simulada)
> 3. Añadáis un punto de control humano
> 4. Lo probéis con un mensaje real"

**Ayuda individual:** Instructor circula resolviendo dudas técnicas.

**Objetivo:** Que cada alumno termine con un agente FUNCIONAL, por simple que sea.

---

## 7. INTEGRACIÓN CON HERRAMIENTAS EMPRESARIALES (03:00-03:15)

### 📍 Slides

| Slide | Contenido |
|-------|-----------|
| T21 | **Conectar con tu día a día** |
| T22 | Slack / Teams — notificaciones y comandos |
| T23 | Gmail / Outlook — leer y enviar correos |
| T24 | Jira / ClickUp / Asana — gestión de proyectos |
| T25 | Google Sheets / Excel Online — datos |
| T26 | Calendario — eventos y reuniones |
| T27 | **APIs: no asustan** — "URL + token + JSON. Eso es todo." |

### 🎬 Guión

> "Vale, tenéis un agente que funciona en n8n. ¿Y ahora?
>
> Para que sea útil, tiene que vivir donde trabajáis. Slack, correo, Jira...
>
> La buena noticia: n8n tiene conectores para casi todo. Slack, Gmail, Google Sheets, Jira... son todo nodos que arrastráis.
>
> La mala noticia: si vuestra empresa usa herramientas menos comunes, necesitaréis APIs. Y las APIs no asustan. Es solo: URL + token + JSON.
>
> Vamos a verlo: en 2 minutos conecto este agente a Slack."

*(Demo rápida: conecta el agente a un canal de Slack. El agente escucha menciones y responde)*

---

## 8. CIERRE (03:15-03:30)

### 📍 Slides

| Slide | Contenido |
|-------|-----------|
| T28 | **Resumen** |
| T29 | Un agente no es magia: es input + cerebro + herramientas + acción |
| T30 | Empieza con un asistente, escala a ejecutor |
| T31 | Puntos de control = confianza |
| T32 | **Ejercicio entre sesiones** |
| T33 | Implementa tu agente con datos reales |
| T34 | Mide: cuánto tiempo ahorra, errores, mejoras |
| T35 | **Semana que viene:** Estrategia. La parte seria. |
| T36 | Seguridad, costes, cómo vender esto a tu jefe |

### 🎬 Guión de cierre

> "Hoy habéis construido algo que piensa, decide y actúa. Eso no es poco.
>
> Entre hoy y la última sesión: implementadlo. Con datos reales. Con procesos reales. Medid: ¿cuánto tiempo ahorra? ¿qué errores comete? ¿qué mejoraríais?
>
> La semana que viene: la parte seria. Seguridad, costes, y cómo vender todo esto a tu jefe sin que te tome por loco.
>
> Porque un agente que nadie usa no sirve de nada."
>
> ¿Preguntas?"

---

## MATERIALES SESIÓN 3

- [ ] Presentación completa (PDF)
- [ ] Plantilla de diseño de agente (papel + digital)
- [ ] Plantilla de agente base para n8n (JSON para importar)
- [ ] Guía rápida de n8n para agentes
- [ ] Ejemplos de agents funcionales (3 casos: simple, medio, avanzado)
- [ ] Guía de APIs para no-programadores (una página)
- [ ] Checklist de seguridad para agentes
- [ ] Enlaces: documentación n8n, OpenAI API, Claude API

---

## CHECKLIST INSTRUCTOR

- [ ] n8n con node AI Agent configurado (OpenAI/Claude)
- [ ] 3 workflows preparados: automatización, asistente, agente
- [ ] APIs configuradas: Slack, Google Calendar, Jira (o simuladores)
- [ ] Plantilla de agente base lista para importar
- [ ] Cuenta de Slack workspace con bot configurado
- [ ] APIs de prueba funcionando (mock APIs si las reales no están disponibles)
- [ ] Ejercicios de reserva por si algún alumno termina antes
