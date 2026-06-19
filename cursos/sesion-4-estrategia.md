# IA Operativa — Sesión 4: Estrategia y Gobernanza

**Duración:** 3.5h (210 min)
**Formato:** 40% teoría → 30% taller → 30% plan de acción

---

## 1. APERTURA Y REVIEW (00:00-00:15)

### 📍 Slides

| Slide | Contenido | Notas |
|-------|-----------|-------|
| T1 | "Bienvenidos al último día" | |
| T2 | **Review de agentes** — los 3 mejores implementados | "De la teoría a la realidad" |
| T3 | **El reto real** | |
| T4 | "Vale, funciona. ¿Y ahora?" | "El 90% de los proyectos mueren aquí" |

### 🎬 Guión

> "Tres semanas. Habéis aprendido a identificar procesos, a usar herramientas, a construir agentes.
>
> Y ahora viene lo difícil. Lo que separa a los que realmente transforman su trabajo de los que se quedan con una cuenta de ChatGPT que usan dos veces al mes.
>
> Hoy: cómo hacer que esto ESCALE en tu equipo sin que te echen de IT, sin violar GDPR, sin que te odien tus compañeros."

---

## 2. SEGURIDAD Y PRIVACIDAD (00:15-00:45)

### 📍 Slides

| Slide | Contenido | Notas |
|-------|-----------|-------|
| T5 | **La pregunta que te van a hacer:** "¿Y los datos?" | |
| T6 | **Lo que SÍ puedes meter:** | Código interno (no crítico), documentación pública, procesos genéricos, datos anonimizados |
| T7 | **Lo que NO debes meter:** | Datos personales de clientes/empleados, secretos empresariales, contraseñas/tokens, información financiera sin anonimizar, estrategia no pública |
| T8 | **GDPR / LOPD en 5 puntos:** | |
| T9 | 1. Tus datos no pueden entrenar modelos sin consentimiento | "El 'modo gratis' entrena con tus datos" |
| T10 | 2. Derecho de supresión: puedes borrar tus datos | "No todos los proveedores lo permiten" |
| T11 | 3. Transferencia internacional: fuera de UE = más requisitos | "OpenAI = USA = requiere cláusulas contractuales" |
| T12 | 4. Decisión automatizada: derecho a revisión humana | "Un agente no puede despedirte" |
| T13 | 5. Registro de tratamientos: documenta qué haces | "Si no está documentado, no existe" |
| T14 | **Modelos locales vs cloud:** árbol de decisión | |
| T15 | Cloud: barato, potente, requiere conexión, datos fuera | |
| T16 | Local: privado, lento (6GB VRAM = 45% GPU), caro en hardware | "Os suena de algo, ¿verdad?" |
| T17 | **Demo:** filtrar datos sensibles automáticamente | |

### 🛠 Demo 9: Filtro de datos sensibles

**Preparación:** n8n con un flujo que recibe texto y detecta datos sensibles antes de enviarlos a la IA.

**El flujo:**
```
INPUT: "El cliente Pérez, con DNI 12345678Z, ha solicitado un presupuesto de 50.000€"

PASO 1: Regex + IA detecta: nombre, DNI, importe
PASO 2: Anonimiza: "El cliente [NOMBRE], con DNI [DOCUMENTO], ha solicitado un presupuesto de [IMPORTE]€"
PASO 3: Envía texto anonimizado a la IA
PASO 4: La IA responde
PASO 5: Si la respuesta necesita datos reales, los re-introduce controladamente
```

> "Esto es crítico. La mayoría de empresas no adoptan IA por miedo a la seguridad. Con este patrón, puedes usar IA en cloud sin exponer datos sensibles."

---

## 3. COSTES REALES (00:45-01:15)

### 📍 Slides

| Slide | Contenido | Notas |
|-------|-----------|-------|
| T18 | **¿Cuánto cuesta realmente la IA?** | |
| T19 | **APIs más comunes:** | Tabla de precios reales |
| T20 | GPT-4o: ~2.50-10$/M tokens | "Potente pero caro" |
| T21 | Claude 3.5 Sonnet: ~3-15$/M tokens | "Analítico, precio similar" |
| T22 | DeepSeek V4 Flash: ~0.50-2$/M tokens | "El económico que funciona" |
| T23 | Gemini: ~1-3$/M tokens | "Bien integrado con Google" |
| T24 | **Modelos locales:** | |
| T25 | Hardware: 1.000-3.000€ por GPU | "Y se queda obsoleta en 2 años" |
| T26 | Electricidad: ~100-300€/año | |
| T27 | Mantenimiento: ~10h/mes | "Actualizaciones, parches, reinicios" |
| T28 | **Calculadora de ROI** — Google Sheets interactivo | Se comparte con los alumnos |
| T29 | Ejemplo: proceso de 5h/semana × 50€/h = 250€/semana | |
| T30 | Automatizado con API DeepSeek: 2€/semana | ROI: 12.500% |

### 📝 Taller 8: Calcula tu ROI

**Enunciado:**
```
CALCULADORA DE ROI

PROCESO A AUTOMATIZAR: ________________

TIEMPO ACTUAL (h/semana): ___
COSTE POR HORA (tu salario/hora estimado): ___ €
COSTE SEMANAL ACTUAL: ___ €
COSTE ANUAL ACTUAL: ___ €

COSTE DE AUTOMATIZACIÓN:
  API calls/semana: ___
  Coste/1K calls: ___ €
  Coste semanal API: ___ €
  n8n hosting: ___ €/mes
  Coste semanal TOTAL: ___ €

AHORRO SEMANAL: ___ €
AHORRO ANUAL: ___ €
ROI: ___ %

TIEMPO DE IMPLEMENTACIÓN: ___ horas
COSTE DE IMPLEMENTACIÓN (tu tiempo): ___ €
RECUPERACIÓN DE INVERSIÓN: ___ días
```

> "La mayoría descubre que una automatización que le ahorra 2h/semana se paga sola en menos de un mes. Con APIs baratas como DeepSeek, en una semana."

---

## 4. PAUSA CAFÉ (01:15-01:30)

---

## 5. PLAN DE ADOPCIÓN (01:30-02:15)

### 📍 Slides

| Slide | Contenido | Notas |
|-------|-----------|-------|
| T31 | **El plan de adopción** | |
| T32 | **Fase 1: Descubrimiento** (semana 1-2) | |
| T33 | Mapear procesos → identificar candidatos → priorizar | "Lo que hicimos en la sesión 1" |
| T34 | **Fase 2: Piloto** (semana 3-4) | |
| T35 | Elegir 1 proceso → automatizar → medir → iterar | "Lo que habéis hecho estas semanas" |
| T36 | **Fase 3: Escalado controlado** (mes 2) | |
| T37 | 3-5 procesos → documentar → formar a 1-2 personas más | |
| T38 | **Fase 4: Integración** (mes 3+) | |
| T39 | Procesos críticos → gobierno → mejora continua | |
| T40 | **Gestión del cambio: cómo vender la IA** | |
| T41 | **A tu jefe:** "Esto ahorra X€/año" | Datos, no emociones |
| T42 | **A tu equipo:** "Esto elimina tareas aburridas, no personas" | Seguridad, no amenaza |
| T43 | **A IT:** "Cumple seguridad, usamos APIs controladas, datos anonimizados" | Control, no riesgo |
| T44 | **A RRHH:** "Formación, no sustitución" | Desarrollo, no despido |

### 🎬 Guión (importante: es la parte más práctica del curso)

> "Vale. Sabes hacerlo. ¿Cómo se lo cuentas a los demás?
>
> **A tu jefe:** No le hables de 'transformación digital'. Háblale de dinero. 'Este proceso cuesta X. Automatizarlo cuesta Y. Recuperamos la inversión en Z días.' Punto.
>
> **A tu equipo:** La gente tiene miedo. No de la IA, de quedarse sin trabajo. El mensaje correcto: 'Esto hace las tareas aburridas. Tú harás cosas más interesantes.' Y demuéstralo.
>
> **A IT:** Van a decir que no. Prepárate: 'API con autenticación. Datos anonimizados antes de enviar. Sin almacenamiento externo. Logs de cada acción. Punto de control humano.' Si dices esto, te dejarán.
>
> **A RRHH:** 'Esto es formación, no un despido. La gente aprende habilidades nuevas. La empresa retiene talento.'"

---

## 6. TALLER: ROADMAP PERSONALIZADO (02:15-02:45)

### 📝 Taller 9: Plan de acción 30-60-90 (30 min)

**Material:** Plantilla "Roadmap 30-60-90" (papel + digital)

```
MI PLAN DE ADOPCIÓN IA — 30-60-90 DÍAS

NOMBRE: ______________  EMPRESA: ______________  FECHA: ______________

PRÓXIMOS 30 DÍAS:
Prioridad 1: _________________________________
  Acción concreta: ___________________________
  Recursos necesarios: _______________________
  Cómo mido éxito: ___________________________

Prioridad 2: _________________________________
  Acción concreta: ___________________________
  Recursos necesarios: _______________________
  Cómo mido éxito: ___________________________

DÍAS 31-60:
  ____________________________________________
  ____________________________________________
  ____________________________________________

DÍAS 61-90:
  ____________________________________________
  ____________________________________________
  ____________________________________________

OBSTÁCULOS PREVISTOS:
  1. _________________________________
  2. _________________________________
  3. _________________________________

CÓMO SUPERARLOS:
  1. _________________________________
  2. _________________________________
  3. _________________________________

¿QUIÉN MÁS NECESITO IMPLICAR?
  1. _________________________________
  2. _________________________________

PRÓXIMA REVISIÓN: ___/___/_____ (conmigo o en comunidad)
```

**Dinámica:**
- 15 min: individual. Cada alumno completa su roadmap
- 10 min: compartir en parejas y dar feedback
- 5 min: compromiso público. Cada uno dice su prioridad 1

---

## 7. MESA REDONDA / Q&A (02:45-03:15)

### Formato

**No hay slides. Es conversación.**

**Preguntas para romper el hielo si nadie habla:**
- "¿Qué fue lo más útil del curso?"
- "¿Qué fue lo más difícil?"
- "¿Qué vais a hacer mañana mismo cuando lleguéis al trabajo?"
- "¿Qué duda os queda que no hayáis preguntado?"

**Prepárate para estas preguntas duras:**
- "¿Y si mi empresa no me deja instalar nada?"
- "¿Cuánto tarda en amortizarse un agente complejo?"
- "¿Y si la IA se equivoca y causa un problema grave?"
- "¿Realmente merece la pena para equipos pequeños?"

---

## 8. CIERRE Y CERTIFICADOS (03:15-03:30)

### 📍 Slides

| Slide | Contenido |
|-------|-----------|
| T45 | **Gracias** — Fondo negro, texto dorado grande |
| T46 | **Lo que has aprendido en 4 semanas** — Resumen visual del viaje |
| T47 | De no saber qué es una API a construir un agente |
| T48 | De tener miedo a la IA a tener un plan de adopción |
| T49 | **Qué sigue:** |
| T50 | Comunidad privada (Telegram / Discord) — seguimiento 3 meses |
| T51 | Materiales completos disponibles siempre |
| T52 | Próximos pasos: taller avanzado de agentes (nivel 2) |
| T53 | **Certificado de finalización** |
| T54 | QR: Únete a la comunidad |

### 🎬 Guión de cierre

> *(Tono más personal. Menos instructor, más persona)*
>
> "Hace 4 semanas, la mayoría no sabíais qué era un prompt. Hoy tenéis un agente funcionando y un plan para los próximos 3 meses.
>
> Esto no termina aquí. El grupo de Telegram sigue abierto. Los materiales son vuestros para siempre. Y cuando tengáis dudas —y las vais a tener— preguntad.
>
> Una cosa más: lo que hace que esto funcione no es la tecnología. Son las personas que deciden usarla. Vosotros.
>
> Gracias. Y ahora, a implementar."
>
> *(Entregas certificados. Fotos. Despedida)*

---

## CERTIFICADO DE FINALIZACIÓN

```
[LOGO NEO LABS]

CERTIFICADO DE FINALIZACIÓN

IA OPERATIVA — Automatización Inteligente para Equipos de Trabajo

Otorgado a: [NOMBRE ALUMNO]

Por completar 14 horas de formación en:
- Fundamentos y estrategia de IA
- Herramientas prácticas y prompting profesional
- Construcción de flujos y agentes autónomos
- Seguridad, costes y plan de adopción empresarial

Fecha: [FECHA]
Duración: 14 horas

David [APELLIDO]
PM IT | GFT Technologies
Instructor IA Operativa

[FIRMA DIGITAL]
```

---

## MATERIALES SESIÓN 4

- [ ] Presentación completa (PDF)
- [ ] Guía de seguridad y cumplimiento GDPR/LOPD (PDF)
- [ ] Calculadora de ROI (Google Sheets, editable)
- [ ] Plantilla de plan de adopción 30-60-90
- [ ] Template de roadmap personal
- [ ] Certificado de finalización (PDF editable)
- [ ] Resumen ejecutivo del curso (una página para compartir con jefes)
- [ ] Enlace a comunidad privada (Telegram/Discord)
- [ ] Encuesta de satisfacción

---

## MATERIAL TRANSVERSAL (entregar al final del curso)

- [ ] Diploma de finalización (personalizado)
- [ ] PDF con todas las presentaciones
- [ ] Pack de plantillas (checklist, mapa, diseño agente, roadmap)
- [ ] Guía de recursos (enlaces, lecturas, herramientas, comunidades)
- [ ] Acceso a comunidad privada (3 meses)
- [ ] Grabaciones de las sesiones

---

## CHECKLIST INSTRUCTOR (DÍA ANTES)

- [ ] Certificados generados con nombres de los alumnos
- [ ] Enlaces a comunidad privada preparados
- [ ] Calculadora de ROI funcionando
- [ ] Encuesta de satisfacción lista
- [ ] Material transversal empaquetado (ZIP o carpeta compartida)
- [ ] Fotos del grupo al final (si presencial)
- [ ] Tarjetas personales / linkedin para conectar
- [ ] Próximos pasos preparados (cursos nivel 2, consultoría)

---

## POST-CURSO (día siguiente)

- [ ] Enviar email de agradecimiento con materiales
- [ ] Publicar resumen del curso en LinkedIn
- [ ] Pedir testimonios a alumnos destacados
- [ ] Analizar encuestas de satisfacción
- [ ] Identificar leads para siguiente edición / consultoría
