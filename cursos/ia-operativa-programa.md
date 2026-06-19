# IA Operativa — Automatización Inteligente para Equipos de Trabajo

**Instructor:** David — PM IT experto en IA | GFT Technologies
**Formato:** 4 sesiones de 3.5h (total 14h)
**Modalidad:** Presencial o videoconferencia
**Precio objetivo:** 800-1500€ por persona | 3000-6000€ por empresa (grupo hasta 15)

---

## Estructura General

| Sesión | Título | Duración | Enfoque |
|--------|--------|----------|---------|
| 1 | Fundamentos y Estrategia | 3.5h | Por qué, qué, dónde |
| 2 | Herramientas Prácticas | 3.5h | Cómo: el día a día |
| 3 | Flujos y Agentes | 3.5h | Automatización real |
| 4 | Estrategia y Gobernanza | 3.5h | Escalar con cabeza |

Cada sesión: 50% teoría → 25% demo en vivo → 25% taller práctico.

---

## SESIÓN 1: Fundamentos y Estrategia

**Objetivo:** Que el alumno entienda QUÉ es la IA hoy, POR QUÉ importa y DÓNDE aplicarla en su empresa.

### Timeline

**00:00-00:10 — Hook inicial**
- Una demo impactante: automatizo un proceso de 2h en 30 segundos delante de ellos
- "Esto no es el futuro. Es lo que puedes hacer esta tarde."

**00:10-00:30 — IA sin hype: qué es realmente**
- Mito vs realidad (no, no va a sustituirte a ti)
- Los 3 tipos que importan hoy:
  - **Generativa** (texto, imagen, código)
  - **Predictiva** (datos, patrones, forecasts)
  - **Agentes** (automatización autónoma)
- Demo: el mismo problema resuelto con cada tipo

**00:30-01:00 — Mapa de oportunidades**
- Dónde aplicar IA en tu empresa (checklist):
  - Reuniones: transcripción, resumen, action items
  - Correos: drafting, priorización, respuestas automáticas
  - Documentación: informes, actas, documentación técnica
  - Datos: análisis, dashboards, detección de anomalías
  - Código: revisión, generación, debugging
- **Taller exprés:** Cada alumno identifica 3 procesos de su trabajo que se puedan automatizar

**01:00-01:15 — Pausa café**

**01:15-01:45 — Casos reales (de mi día a día como PM IT)**
- Caso 1: Automatización de actas de comité de empresa (lo que realmente hago)
- Caso 2: Monitorización de proyectos con agentes autónomos
- Caso 3: Análisis de sentimiento en feedback de empleados
- Cada caso con: problema → solución → resultado → tiempo ahorrado

**01:45-02:30 — Taller: diagnóstico de tu equipo**
- Plantilla: "Mapa de automatización"
- Cada alumno rellena: proceso, tiempo actual, dolor, complejidad, impacto
- Puesta en común y priorización

**02:30-03:00 — Demo en vivo: construyo una automatización desde cero**
- Cogemos un proceso real de un alumno
- Lo automatizamos en directo (herramienta: n8n + Claude/GPT)
- Ven el antes y el después

**03:00-03:30 — Cierre y preparación**
- Resumen de la sesión
- Ejercicio entre sesiones: traer 5 procesos de su trabajo documentados
- Q&A

### Materiales necesarios
- Presentación (slides estilo Apple/MasterClass)
- Plantilla "Mapa de automatización" (PDF/Notion)
- Checklist de oportunidades IA (PDF)
- Guía de recursos para explorar entre sesiones

---

## SESIÓN 2: Herramientas Prácticas

**Objetivo:** Que el alumno maneje con soltura las herramientas clave del día a día.

### Timeline

**00:00-00:10 — Apertura**
- Resumen de la sesión anterior
- Los 3 hallazgos más interesantes de los ejercicios entre sesiones

**00:10-00:50 — El ecosistema actual (quién es quién)**
- **ChatGPT vs Claude vs Gemini vs Copilot**
  - Cuándo usar cada uno
  - Costes reales (no "es gratis")
  - Lo que NO te cuentan
- **Demo comparativa:** el mismo prompt en 4 herramientas
- **Caso práctico:** cómo uso CADA una en mi día

**00:50-01:15 — Prompting profesional (no es magia, es ingeniería)**
- Framework: Contexto + Tarea + Formato + Ejemplo
- Técnicas clave:
  - Chain-of-thought
  - Few-shot
  - Role prompting
  - Structured output
- **Demo:** del prompt cutre al prompt profesional en 3 iteraciones

**01:15-01:30 — Pausa**

**01:30-02:00 — Taller: prompting aplicado a tu trabajo**
- Ejercicios con datos reales (anónimos) de los alumnos:
  - Resumir un correo complejo
  - Extraer action items de una transcripción
  - Generar un informe ejecutivo
  - Analizar datos de una hoja de cálculo

**02:00-02:30 — Automatización de tareas diarias (sin código)**
- Hazel / Keyboard Maestro / Shortcuts (según ecosistema)
- Zapier / Make para conexiones sin código
- **Demo en vivo:** conecto el correo → IA → CRM en 10 min

**02:30-03:00 — Taller: construye tu primer automatismo**
- Cada alumno conecta 2 herramientas con un flujo IA
- Plantilla: "De la tarea al workflow"
- Asistencia individual

**03:00-03:30 — Cierre**
- Ejercicio entre sesiones: automatizar UN proceso real de su trabajo
- Mostrarlo en la siguiente sesión
- Q&A

### Materiales necesarios
- Guía comparativa de herramientas (PDF)
- Cheatsheet de prompting (PDF de una cara)
- Plantilla "Del prompt cutre al prompt profesional"
- Plantilla "De la tarea al workflow" (para Make/n8n básico)

---

## SESIÓN 3: Flujos y Agentes

**Objetivo:** Que el alumno diseñe y construya automatizaciones con agentes IA.

### Timeline

**00:00-00:15 — Apertura**
- Review de automatismos de los alumnos (los mejores se comparten)
- Concepto: de la automatización lineal al agente autónomo

**00:15-01:00 — El salto: automatización → agentes**
- ¿Qué es un agente IA? (no, no es un chatbot)
- Componentes: input → razonamiento → herramientas → acción
- Tipos de agentes:
  - Asistentes (responden cuando les llamas)
  - Vigilantes (monitorizan y alertan)
  - Ejecutores (hacen tareas sin supervisión)
  - Orquestadores (coordinan otros agentes)
- **Demo:** el mismo proceso hecho con automatización vs con agente

**01:00-01:30 — Demo en vivo: construyo un agente desde cero**
- Usando n8n o similar
- Agente que:
  1. Recibe un email
  2. Analiza el contenido con IA
  3. Lo categoriza
  4. Busca info relevante
  5. Redacta respuesta
  6. La envía (con supervisión humana)

**01:30-01:45 — Pausa**

**01:45-02:30 — Taller: diseña tu primer agente**
- Plantilla de diseño de agentes
- Cada alumno:
  1. Define un proceso que quiere delegar
  2. Diseña el flujo del agente
  3. Identifica las herramientas que necesita
  4. Define puntos de control humano
- Presentación de los mejores diseños

**02:30-03:00 — Integración con herramientas empresariales**
- Slack, Teams, email, CRM, ERP
- APIs: qué son y por qué no asustan
- Demo: agente que lee Slack, consulta CRM y responde
- Consideraciones de seguridad

**03:00-03:30 — Cierre**
- Ejercicio entre sesiones: implementar el agente diseñado
- Q&A
- Avance de la sesión 4: "la parte seria"

### Materiales necesarios
- Plantilla de diseño de agentes (PDF/Miro)
- Guía rápida de n8n para no-programadores
- Ejemplos de agentes funcionales (para compartir)
- Checklist de seguridad para agentes

---

## SESIÓN 4: Estrategia y Gobernanza

**Objetivo:** Que el alumno pueda liderar la adopción de IA en su equipo con criterio.

### Timeline

**00:00-00:15 — Apertura**
- Review de agentes implementados
- El problema real: "vale, funciona, ¿y ahora?"

**00:15-00:45 — Seguridad y privacidad**
- ¿Qué datos NO debes meter en una IA?
- GDPR / LOPD: lo que necesitas saber
- Proveedores: ¿dónde se procesan tus datos?
- Modelos locales vs cloud: cuándo cada uno
- **Demo:** cómo filtrar datos sensibles automáticamente

**00:45-01:15 — Costes reales**
- Cuánto cuesta operar un agente:
  - APIs: GPT, Claude, DeepSeek (comparativa real)
  - Infraestructura: local vs cloud
  - Mantenimiento
- Calculadora de ROI para tu equipo
- **Ejercicio:** calcular el coste de una automatización vs el tiempo que ahorra

**01:15-01:30 — Pausa**

**01:30-02:15 — Plan de adopción para tu equipo**
- Fases:
  1. Descubrimiento (semana 1-2)
  2. Piloto (semana 3-4)
  3. Escalado controlado (mes 2)
  4. Integración (mes 3+)
- Gestión del cambio: cómo vender la IA a tu jefe
- Gestión del miedo: cómo venderla a tu equipo
- **Taller:** escribe el plan de adopción para tu departamento

**02:15-02:45 — Proyecto final: roadmap personalizado**
- Cada alumno define:
  - Qué va a implementar en los próximos 30 días
  - Qué necesita (herramientas, permisos, presupuesto)
  - Cómo va a medir el éxito
  - Plan de escalado a 3 meses
- Presentación de los roadmaps

**02:45-03:15 — Mesa redonda / Q&A**
- Dudas abiertas
- Experiencias compartidas
- Siguientes pasos
- Comunidad post-curso

**03:15-03:30 — Cierre**
- Certificado de finalización
- Acceso a comunidad privada (Telegram/Discord)
- Materiales completos para siempre
- "No paran de salir cosas nuevas — esto es solo el principio"

### Materiales necesarios
- Guía de seguridad y cumplimiento (PDF)
- Calculadora de ROI (Google Sheets)
- Plantilla de plan de adopción
- Template de roadmap 30-60-90 días
- Certificado de finalización

---

## Materiales Transversales

### Para cada alumno (incluido en el precio)
1. Presentaciones completas (PDF)
2. Plantillas y checklists (5 documentos)
3. Acceso a comunidad privada post-curso (3 meses)
4. Certificado de finalización
5. Grabaciones de las sesiones (si online)

### Para el instructor (lo que necesitas tú)
1. Presentación en PowerPoint/Keynote/HTML (estilo MasterClass)
2. Guía del instructor con notas para cada slide
3. Escenarios de demo preparados y probados
4. FAQs y respuestas a preguntas difíciles
5. Ejercicios con soluciones

### Infraestructura necesaria
- Cuenta demo de herramientas (ChatGPT, Claude, n8n)
- Proyecto base en n8n (para no empezar de cero)
- Entorno de pruebas para agentes
- Opcional: pantalla dual para hacer demos

---

## Propuesta Comercial

### Para empresas (paquete)

| Concepto | Precio |
|----------|--------|
| Curso completo (14h, grupo hasta 15 pers.) | 4.500€ |
| Sesión individual de diagnóstico previo | 500€ |
| Seguimiento post-curso (1 mes) | 1.000€ |
| **Pack completo** | **6.000€** |

### Para individuales

| Concepto | Precio |
|----------|--------|
| Curso completo (14h, grupos abiertos) | 800€/persona |
| Early bird (primeros 10) | 500€/persona |

### Targets iniciales (tu red)
1. **GFT** — formación interna para tu equipo y afines
2. **Comité de empresa** — otras empresas del sector
3. **Contactos de Stuttgart** — empresas alemanas con need digital
4. **LinkedIn** — tu red de PMs y IT
5. **Asociaciones de PM** — charla gratuita → leads → curso

---

## Siguiente paso

¿Empiezo por la **presentación** (slides Apple/MasterClass), por la **landing page**, o prefieres que ajustemos el programa primero?
