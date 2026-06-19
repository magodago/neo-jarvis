# IA Operativa — Sesión 2: Herramientas Prácticas

**Duración:** 3.5h (210 min)
**Formato:** 40% teoría → 30% demo → 30% taller práctico

---

## 1. APERTURA Y REVIEW (00:00-00:15)

### 📍 Slides

| Slide | Contenido | Notas |
|-------|-----------|-------|
| T1 | "Bienvenidos al día 2" — Fondo negro, título dorado | |
| T2 | **La semana entre sesiones** — 3 hallazgos compartidos | Elegir los 3 más interesantes de los ejercicios |
| T3 | **Hoy:** De espectadores a pilotos | "Hoy tocáis. Literalmente." |

### 🎬 Guión

> "La semana pasada os fuisteis con una tarea: documentar 5 procesos.
>
> He visto vuestros mapas. Hay patrones muy claros. Los tres más comunes han sido..."
>
> *(Mencionas 3 hallazgos. Ej: "casi todos marcasteis correos y reuniones como top prioridad", "nadie marcó código aunque el 40% tiene equipo técnico", etc.)*
>
> "Hoy vamos a pasar de identificar a HACER. Vais a escribir prompts, vais a configurar herramientas, vais a construir vuestro primer automatismo."
>
> *(Transición a la siguiente sección)*

---

## 2. EL ECOSISTEMA: QUIÉN ES QUIÉN (00:15-00:50)

### 📍 Slides

| Slide | Contenido | Notas |
|-------|-----------|-------|
| T4 | **El ecosistema IA hoy** — Mapa visual con logos | "No necesitas conocerlos todos" |
| T5 | **ChatGPT** (OpenAI) — El todoterreno | "El que mejor código escribe" |
| T6 | **Claude** (Anthropic) — El analítico | "El que mejor documentos largos procesa" |
| T7 | **Gemini** (Google) — El integrador | "El que mejor se conecta con Gmail, Drive..." |
| T8 | **Copilot** (Microsoft) — El laboral | "El que está en tu Office 365" |
| T9 | **DeepSeek** — El económico | "El que te saca del apuro cuando los otros están caídos" |
| T10 | **Tabla comparativa** — Precios, límites, puntos fuertes, débiles | "Guarda esta slide" |
| T11 | **Lo que NO te cuentan:** | Viñetas clave |
| T12 | "Gratis" = tus datos entrenan al modelo | "Si no pagas, el producto eres tú" |
| T13 | Límites de contexto: no es memoria infinita | "Claude 200K no significa que recuerde todo" |
| T14 | Las alucinaciones bajan con mejor prompting | "El 80% de los errores son tuyos, no de la IA" |

### 🛠 Demo 4: Comparativa en vivo

**Preparación:** 4 pestañas abiertas. ChatGPT, Claude, Gemini, DeepSeek. Mismo prompt en todas.

**Prompt de prueba:**
```
Tengo una reunión con un cliente del sector logística que está frustrado porque su implementación de ERP lleva 3 meses retrasada. Necesito preparar una agenda para una reunión de 30 minutos que:
1. Reconozca su frustración sin ser defensivo
2. Presente un plan de recuperación realista
3. Defina hitos concretos para las próximas 2 semanas

Formato: email profesional, máximo 200 palabras, con asunto y saludo.
```

**Lo que dices:**
> "Mismo problema, 4 herramientas. No os voy a decir cuál es mejor. Cada una tiene un superpoder diferente. Quiero que veáis las diferencias en tiempo real."
>
> *(Ejecutas prompt en cada una, una tras otra)*
>
> "ChatGPT es más directo. Claude estructura mejor. Gemini... bueno, existe. DeepSeek sorprende para lo que cuesta."
>
> "La clave: NO uséis una sola. Tened las 4. Cada problema tiene su herramienta."

### 📝 Taller 3: Prueba a ciegas (10 min)

**Enunciado:**
> "Voy a pasar 3 respuestas de diferentes IAs sin decir cuál es cuál. Tenéis que adivinar cuál es cada una."

Muestras 3 respuestas (sin logos). Los alumnos votan. Revelas. La mayoría acierta Claude vs ChatGPT, pocos aciertan Gemini.

---

## 3. PROMPTING PROFESIONAL (00:50-01:15)

### 📍 Slides

| Slide | Contenido | Notas |
|-------|-----------|-------|
| T15 | **Prompting no es magia, es ingeniería** | |
| T16 | **El framework CTFE:** | Contexto + Tarea + Formato + Ejemplo |
| T17 | **Contexto:** Quién eres, situación, antecedentes | "La IA no sabe nada. Tienes que contárselo." |
| T18 | **Tarea:** Qué quieres exactamente | "Sé específico. 'Resume' ≠ 'Extrae los 3 puntos clave en una frase'" |
| T19 | **Formato:** Cómo quieres la respuesta | "JSON, bullet points, email, tabla..." |
| T20 | **Ejemplo:** Una muestra de lo que esperas | "El truco más infravalorado. Un ejemplo vale más que 100 instrucciones." |
| T21 | **Técnicas clave** | visual |
| T22 | **Chain-of-thought:** "Piensa paso a paso" | "No le pidas la respuesta final. Pídele el razonamiento." |
| T23 | **Few-shot:** 3 ejemplos antes de pedir | "La IA aprende de patrones. Dale patrones." |
| T24 | **Role prompting:** "Eres un PM experto..." | "El role no es decoración. Cambia el output drásticamente." |
| T25 | **Structured output:** "Devuelve JSON" | "Para conectarlo con otras herramientas" |

### 🛠 Demo 5: Del prompt cutre al prompt profesional

**Preparación:** Una ventana con Claude o ChatGPT. 3 prompts preparados.

**Prompt cutre:**
> "Resume esto"

*(La IA devuelve algo genérico)*

> "Esto no sirve. Vamos a mejorarlo."

**Prompt mejorado:**
> "Eres un PM IT con 10 años de experiencia. Te paso el acta de una reunión de seguimiento de proyecto. Necesito que extraigas: decisiones tomadas, action items con responsables, riesgos identificados, y próximos hitos. Formato: tabla. Aquí tienes un ejemplo del formato que quiero: [ejemplo]"

*(La IA devuelve algo útil)*

> "¿Veis la diferencia? No es magia. Es estructura."

---

## 4. PAUSA CAFÉ (01:15-01:30)

---

## 5. TALLER: PROMPTING APLICADO (01:30-02:00)

### 📝 Taller 4: 4 ejercicios prácticos (30 min)

**Preparación:** Los alumnos usan su propia cuenta de ChatGPT/Claude o les pasas una cuenta demo.

**Ejercicio 1: Resumir un correo complejo** (7 min)
```
Tienes este correo de un cliente: [CORREO LARGO CON QUEJA + PETICIÓN + FECHAS]
Pídele a la IA que:
1. Extraiga el problema principal
2. Identifique las 3 peticiones concretas
3. Redacte un borrador de respuesta
4. Marque las fechas clave en un calendario imaginario

Evaluación: ¿La IA entendió bien el tono del cliente?
```

**Ejercicio 2: Extraer action items de una transcripción** (7 min)
```
Tienes esta transcripción de reunión: [TRANSCRIPCIÓN DE 10 MIN]
Pídele a la IA que genere una tabla con: Quién, Qué, Cuándo.
¿Faltó algún action item?
```

**Ejercicio 3: Análisis de datos (sin código)** (8 min)
```
Tienes estos datos de ventas: [CSV CON 50 FILAS]
Pídele a la IA que:
1. Encuentre patrones en los datos
2. Identifique el mes con mejor rendimiento y por qué
3. Sugiera 3 acciones para mejorar

¿Las conclusiones son correctas? ¿Pides los datos correctamente?
```

**Ejercicio 4: Preparar una reunión** (8 min)
```
Eres PM. Mañana tienes reunión con stakeholders sobre un proyecto retrasado.
Dale contexto a la IA y pídele:
1. Agenda de la reunión
2. Posibles preguntas difíciles
3. Datos que deberías tener preparados

Compara tu prompt con el del compañero. ¿Quién dio mejor contexto?
```

**Dinámica:** Cada ejercicio 5-7 min + 2 min compartir resultado

---

## 6. AUTOMATIZACIÓN SIN CÓDIGO (02:00-02:30)

### 📍 Slides

| Slide | Contenido | Notas |
|-------|-----------|-------|
| T26 | **Automatización sin código: el puente** | |
| T27 | **Zapier** — 7000+ apps, fácil, caro si escalas | "Para empezar" |
| T28 | **Make** — Más flexible, curvas de aprendizaje, más barato | "Para crecer" |
| T29 | **n8n** — Open source, auto-hosteado, ilimitado | "Para dominio total" |
| T30 | **Hazel / Keyboard Maestro** — Automatización local | "Para tu PC" |
| T31 | **Shortcuts (Mac/iOS)** — Gratis, nativo | "Para cosas rápidas" |
| T32 | **Cuándo usar cada uno** — Árbol de decisión visual | |

### 🛠 Demo 6: Conectar correo → IA → CRM en 10 min

**Preparación:** n8n abierto. Cuentas conectadas (Gmail, Google Sheets o CRM simulado).

**Flujo:**
```
1. Gmail: watch inbox (nuevo correo de cliente)
2. AI: clasificar correo (urgencia, categoría, acción requerida)
3. Google Sheets: añadir fila con datos
4. Slack: notificar al responsable si urgencia = alta
5. AI: redactar borrador de respuesta
6. Gmail: guardar borrador (sin enviar)
```

**Lo que dices:**
> "Voy a conectar 3 herramientas sin escribir una línea de código. Solo arrastrar nodos."
>
> *(Construyes en vivo. Cada nodo: 1 min. Total: 7-8 min)*
>
> "Ahora, cada vez que un cliente envié un correo, este flujo: clasifica, registra, alerta y redacta respuesta. Yo solo reviso y pulso 'enviar'."
>
> "¿Cuánto tiempo me ahorra esto a la semana? 3-4 horas fácil. Y no he escrito ni una línea de código."

---

## 7. TALLER: PRIMER AUTOMATISMO (02:30-03:00)

### 📝 Taller 5: Construye tu primer flujo (30 min)

**Preparación:** n8n accesible para todos (misma instancia compartida o cada uno la suya). Plantillas de flujo precargadas.

**Enunciado:**
> "Vamos a construir juntos vuestro primer automatismo. Elegid uno de los procesos que identificasteis la semana pasada. El que tenga menor complejidad técnica."

**Flujo guiado (todos hacen lo mismo, pero cada uno con su proceso):**
```
PASO 1: Trigger → ¿Qué inicia el proceso? (email, webhook, schedule, Slack)
PASO 2: Datos → ¿Qué información necesito?
PASO 3: IA → ¿Qué tiene que decidir/clasificar/analizar la IA?
PASO 4: Acción → ¿Qué tiene que pasar después?
PASO 5: Output → ¿Dónde se guarda/envía el resultado?
```

**Ayuda individual:** 15 min de circulación entre los alumnos resolviendo dudas.

**Objetivo:** Que cada uno termine con UN flujo funcional, por simple que sea.

---

## 8. CIERRE (03:00-03:30)

### 📍 Slides

| Slide | Contenido |
|-------|-----------|
| T33 | **Resumen del día** |
| T34 | Elegir herramienta según el problema, no al revés |
| T35 | Estructurar prompts cambia todo |
| T36 | Un automatismo simple hoy > uno perfecto en un mes |
| T37 | **Ejercicio entre sesiones:** Automatizar UN proceso real |
| T38 | Usar el flujo que construiste hoy con datos reales |
| T39 | Traer los resultados: qué funcionó, qué no, qué aprendiste |
| T40 | **Semana que viene:** Agentes. El siguiente nivel. |

### 🎬 Guión de cierre

> "Hoy habéis pasado de espectadores a pilotos. Habéis escrito prompts que funcionan. Habéis conectado herramientas. Habéis construido vuestro primer automatismo.
>
> El ejercicio para la próxima semana: usadlo. Con datos reales. Con procesos reales. No hace falta que sea perfecto. Quiero que veáis qué funciona, qué no, qué duele.
>
> La semana que viene: agentes. Si hoy conectasteis herramientas, la semana que viene vais a crear algo que toma decisiones por sí mismo.
>
> ¿Preguntas?"

---

## MATERIALES SESIÓN 2

- [ ] Presentación completa (PDF)
- [ ] Guía comparativa de herramientas (una cara)
- [ ] Cheatsheet de prompting (una cara, plastificada idealmente)
- [ ] Plantilla "Del prompt cutre al prompt profesional" (ejercicios)
- [ ] Plantillas de flujos n8n para importar
- [ ] Enlaces: ChatGPT, Claude, Gemini, DeepSeek, n8n, Make, Zapier
- [ ] Ejercicios resueltos (para los que se quedan atrás)

---

## CHECKLIST INSTRUCTOR

- [ ] Cuentas activas: ChatGPT Plus, Claude Pro, Gemini, DeepSeek
- [ ] 4 pestañas abiertas con las 4 herramientas
- [ ] Prompt de prueba preparado en cada una
- [ ] 3 respuestas para el "test a ciegas" preparadas (capturas)
- [ ] n8n con workflow correo→IA→Sheets→Slack funcionando
- [ ] n8n accesible para alumnos (URL compartida)
- [ ] Plantillas de flujo precargadas en n8n
- [ ] Ejemplos de correo largo y transcripción para ejercicios
- [ ] CSV de ventas de ejemplo
- [ ] Cuenta demo de Google Sheets preparada
- [ ] Slack workspace con canal de pruebas
