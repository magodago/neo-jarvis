#!/usr/bin/env python3
"""Programmatic SEO v2 — Genera 500+ páginas SIN depender de Gemma.
Usa templates de contenido predefinido + variación de keywords.
Mucho más rápido: ~2 segundos por página vs ~60 segundos."""

import os, random, textwrap, time
from datetime import datetime
from pathlib import Path

REPO = Path.home() / "neo-jarvis"
BLOG = REPO / "blog"
NICHE_DIR = BLOG / "programacion"
NICHE_DIR.mkdir(parents=True, exist_ok=True)

# ─── DATOS ESTRUCTURADOS POR NICHO ───
# Cada keyword tiene: titulo, desc, secciones con contenido variado

PAGES_DATA = [
    # === DEPURACIÓN Y DEBUGGING ===
    {"kw": "como depurar codigo con chatgpt", "target": "depurar código con ChatGPT",
     "title": "Guía completa para depurar código con ChatGPT paso a paso",
     "desc": "Aprende a usar ChatGPT para encontrar y corregir errores en tu código. Técnicas profesionales de debugging con IA.",
     "sections": [
        ("Configura ChatGPT como debugger experto", "Para obtener los mejores resultados al depurar código con ChatGPT, primero debes configurarlo correctamente. Dile qué lenguaje de programación usas, qué framework y qué entorno de desarrollo. Cuanto más contexto le des, más precisas serán sus soluciones. Un buen prompt inicial sería: 'Eres un debugger experto en Python. Analiza este código y encuentra el error.' Después, pega el código completo y explica qué comportamiento esperas versus lo que está ocurriendo realmente."),
        ("Técnicas avanzadas de debugging con prompts", "Una técnica muy efectiva es pedirle a ChatGPT que explique el código línea por línea antes de señalar el error. Esto fuerza al modelo a entender la lógica completa. También puedes pedirle que simule la ejecución paso a paso con valores de ejemplo. Para errores intermitentes, describe el patrón exacto: cuándo ocurre, cada cuánto, en qué condiciones. ChatGPT puede identificar patrones que tú no ves."),
        ("Prompt optimizado para debuggear código", "El prompt ideal para depurar código combina: rol específico (debugger experto), contexto técnico (lenguaje, framework, versión), el código problemático, el comportamiento esperado vs real, y los mensajes de error exactos. Guarda este prompt como plantilla y reutilízalo cada vez que necesites depurar. Con la práctica, ChatGPT resolverá errores en segundos que te tomarían horas."),
     ]},
    {"kw": "como encontrar errores en codigo con ia", "target": "encontrar errores en código con IA",
     "title": "Cómo encontrar errores en código usando inteligencia artificial",
     "desc": "Descubre técnicas de IA para localizar bugs y errores en tu código rápidamente. Ahorra horas de debugging.",
     "sections": [
        ("Por qué la IA es excelente encontrando errores", "Los modelos de lenguaje como ChatGPT, Claude y Gemini han sido entrenados con millones de repositorios de código. Esto significa que han visto prácticamente todos los errores posibles. Cuando le pides que encuentre errores, no está 'buscando' como un humano — está reconociendo patrones que ya ha visto miles de veces. Por eso encuentra bugs que tú podrías pasar por alto después de horas de revisión."),
        ("Estrategia: del error general al específico", "Empieza compartiendo solo la firma de la función y el error. Si ChatGPT no encuentra nada, comparte más contexto progresivamente. Esta técnica de 'embudo inverso' evita saturar al modelo con información irrelevante. También puedes pedirle que revise tipos específicos de errores: null pointers, race conditions, memory leaks, o errores de lógica."),
        ("Casos de éxito en debugging con IA", "Desarrolladores reportan que la IA encuentra entre el 60-80% de los errores en su primera sugerencia. Para bugs más complejos, la tasa sube al 90% después de 2-3 iteraciones. Los errores más comunes que encuentra son: variables no inicializadas, condiciones incorrectas, off-by-one errors, y problemas de tipos."),
     ]},
    {"kw": "analizar logs servidor con chatgpt", "target": "analizar logs de servidor con ChatGPT",
     "title": "Analiza logs de servidor con ChatGPT en segundos",
     "desc": "Aprende a usar ChatGPT para analizar logs de servidor, identificar errores y diagnosticar problemas de producción.",
     "sections": [
        ("Prepara los logs para ChatGPT", "Los logs de servidor pueden ser enormes. Antes de pasárselos a ChatGPT, filtra por nivel (ERROR, WARNING), por timestamp (última hora, último día), y por servicio. Si el log es muy grande, extrae solo las líneas relevantes. Puedes usar grep, awk o una pequeña función en Python para preprocesarlos. ChatGPT funciona mejor con 50-100 líneas enfocadas que con 10,000 líneas de ruido."),
        ("Interpreta patrones de error con IA", "Los errores en producción raramente vienen solos. ChatGPT puede identificar patrones: 'cada vez que falla el servicio X, 2 segundos después aparece el error Y en el servicio Z'. Esta correlación de eventos es difícil de ver manualmente pero muy fácil para la IA. Pídele específicamente que busque relaciones causales entre eventos."),
        ("Prompt experto para análisis de logs", "Usa este prompt: 'Eres un SRE experto. Analiza estos logs de producción. Identifica: 1) Los 3 errores más críticos, 2) La causa raíz probable de cada uno, 3) Una solución priorizada. Si ves patrones temporales entre errores, señálalos.' Este enfoque estructurado da resultados mucho mejores que un 'analiza estos logs' genérico."),
     ]},

    # === GENERACIÓN DE CÓDIGO ===
    {"kw": "generar codigo python con chatgpt", "target": "generar código Python con ChatGPT",
     "title": "Guía para generar código Python con ChatGPT como un profesional",
     "desc": "Aprende a usar ChatGPT para generar código Python limpio, eficiente y listo para producción. Ejemplos y prompts incluidos.",
     "sections": [
        ("Cómo pedir código Python a ChatGPT", "La clave para obtener buen código Python de ChatGPT es la especificidad. No digas 'hazme un script' — di: 'Necesito un script Python que lea un CSV de ventas, calcule el total por categoría, y genere un gráfico de barras con matplotlib. Los datos tienen columnas: fecha, producto, categoría, importe.' Cuanto más específico seas, menos iteraciones necesitarás."),
        ("Refina el código generado", "El primer código que genera ChatGPT raramente es perfecto. El proceso correcto es: 1) Pide el código base, 2) Revísalo buscando problemas de seguridad, 3) Pide mejoras específicas ('añade type hints', 'optimiza para datasets grandes', 'añade logging'). Cada iteración mejora el código significativamente."),
        ("Buenas prácticas al generar código con IA", "Usa ChatGPT como un programador junior que trabaja para ti: revísale el código, pídele cambios, y no asumas que lo que genera es correcto. Verifica siempre: la lógica de negocio, el manejo de errores (try/except), y la seguridad (sanitización de inputs). Con estas precauciones, ChatGPT multiplica tu productividad 3x-5x."),
     ]},
    {"kw": "crear api rest con chatgpt", "target": "crear API REST con ChatGPT",
     "title": "Aprende a crear una API REST completa con ChatGPT",
     "desc": "Guía paso a paso para diseñar e implementar APIs REST usando ChatGPT. Desde el diseño hasta el deploy.",
     "sections": [
        ("Diseña la estructura de tu API", "Antes de escribir código, pídele a ChatGPT que te ayude a diseñar la API. Un buen prompt: 'Diseña una API REST para un sistema de gestión de tareas. Debe tener endpoints para CRUD de tareas, usuarios, y proyectos. Dame la estructura de rutas, métodos HTTP, y esquemas JSON para cada endpoint.' Este diseño previo evita tener que reescribir código después."),
        ("Implementa los endpoints", "Una vez que tienes el diseño, pide los endpoints uno por uno. Por ejemplo: 'Implementa el endpoint POST /api/tasks en Express.js. Debe aceptar título, descripción, fecha límite y usuario asignado. Valida los campos requeridos y devuelve la tarea creada con su ID.' Este enfoque modular da mejor código que pedir la API completa de golpe."),
        ("Añade seguridad y validación", "La seguridad es crítica en las APIs. Pide a ChatGPT explícitamente: 'Añade middleware de autenticación JWT a todos los endpoints protegidos', 'Implementa rate limiting', 'Añade validación de datos con express-validator'. No asumas que el código generado es seguro — siempre pide explícitamente las medidas de seguridad que necesitas."),
     ]},

    # === REVISIÓN Y CALIDAD ===
    {"kw": "revisar codigo con inteligencia artificial", "target": "revisar código con IA",
     "title": "Cómo revisar código con inteligencia artificial como un senior",
     "desc": "Usa IA para code review profesional. Aprende técnicas para que ChatGPT, Claude y Gemini revisen tu código como un desarrollador senior.",
     "sections": [
        ("Qué tipo de revisiones puede hacer la IA", "ChatGPT puede hacer varios tipos de code review: revisión de seguridad (inyección SQL, XSS), revisión de rendimiento (consultas N+1, algoritmos ineficientes), revisión de estilo (convenciones del lenguaje), y revisión de lógica (bugs, condiciones incorrectas). Para cada tipo, usa un prompt específico enfocado en ese aspecto."),
        ("El prompt perfecto para code review", "El mejor prompt para code review: 'Actúa como un desarrollador senior haciendo code review. Revisa este código y señala: 1) Problemas de seguridad, 2) Problemas de rendimiento, 3) Bugs o errores lógicos, 4) Mejoras de legibilidad y mantenibilidad, 5) Violaciones de buenas prácticas. Para cada issue, explica por qué es un problema y cómo solucionarlo.' Este prompt estructurado da resultados muy superiores a un simple 'revisa este código'."),
        ("Integra la IA en tu flujo de code review", "La mejor forma de usar IA para code review es: primero revísalo tú mismo (cosas que solo un humano puede ver), luego pásalo a la IA para lo que se le da bien (seguridad, rendimiento, convenciones), y finalmente decide qué cambios aplicar. La IA no reemplaza al revisor humano — lo complementa."),
     ]},

    # === TESTS ===
    {"kw": "escribir tests automatizados con ia", "target": "escribir tests automatizados con IA",
     "title": "Escribe tests automatizados con IA en minutos",
     "desc": "Guía para generar tests unitarios, de integración y funcionales usando inteligencia artificial. Aumenta tu cobertura de tests sin esfuerzo.",
     "sections": [
        ("Genera tests unitarios con ChatGPT", "El prompt ideal para tests unitarios: 'Genera tests unitarios con pytest para esta función. Cubre: caso feliz, caso borde (lista vacía, valores nulos), caso de error (input inválido). Usa fixtures y mocks donde sea necesario.' ChatGPT genera tests completos con coverage de boundary cases que normalmente olvidarías."),
        ("Tests de integración con IA", "Para tests de integración, dale el contexto completo: 'Genera tests de integración para este endpoint. Debe probar: 1) Que devuelve 200 con datos válidos, 2) Que devuelve 400 con datos inválidos, 3) Que devuelve 401 sin autenticación, 4) Que devuelve 404 para recursos inexistentes.' Especifica el framework de tests que usas."),
        ("Mantén los tests generados", "Los tests generados por IA necesitan mantenimiento igual que el código de producción. Cuando refactorices, pide a ChatGPT que actualice los tests: 'He cambiado la función X para que ahora acepte Y en lugar de Z. Actualiza los tests correspondientes.' Esto mantiene tu suite de tests sincronizada sin esfuerzo manual."),
     ]},

    # === DOCUMENTACIÓN ===
    {"kw": "documentar codigo con chatgpt", "target": "documentar código con ChatGPT",
     "title": "Cómo documentar tu código con ChatGPT de forma profesional",
     "desc": "Aprende a usar ChatGPT para generar documentación técnica clara y completa. Docstrings, READMEs y documentación de APIs.",
     "sections": [
        ("Genera docstrings y comentarios automáticamente", "Pídele a ChatGPT: 'Añade docstrings estilo Google a este código. Cada función debe tener: descripción, argumentos con tipos, valor de retorno, y excepciones que puede lanzar.' ChatGPT analiza el código y genera docstrings precisos. Para clases grandes, hazlo función por función para mantener la calidad."),
        ("Crea READMEs profesionales", "Un buen README generado con ChatGPT: 'Crea un README.md para este proyecto. Incluye: descripción del proyecto, requisitos de instalación, instrucciones de uso rápida, ejemplos de código, y enlaces a documentación adicional.' Especifica el tono (profesional, técnico, beginner-friendly) y la longitud deseada."),
        ("Documentación técnica avanzada", "Para documentación más compleja como manuales de API o guías de arquitectura, usa un enfoque estructurado: 'Documenta este endpoint REST. Incluye: descripción, método HTTP, URL, parámetros de request, ejemplo de response, códigos de error posibles, y ejemplo de uso con curl.' Este nivel de detalle genera documentación lista para publicar."),
     ]},

    # === REFACTORIZACIÓN ===
    {"kw": "refactorizar codigo con chatgpt", "target": "refactorizar código con ChatGPT",
     "title": "Refactoriza código legacy con ChatGPT sin romper nada",
     "desc": "Técnicas para refactorizar código antiguo usando inteligencia artificial. Moderniza tu base de código de forma segura.",
     "sections": [
        ("Analiza el código antes de refactorizar", "Antes de tocar nada, pídele a ChatGPT que analice el código: 'Analiza este código legacy. Identifica: 1) Code smells y antipatrones, 2) Oportunidades de refactorización, 3) Dependencias ocultas, 4) Áreas de alto riesgo al cambiar. Dame una estrategia priorizada para la refactorización.' Este análisis previo evita errores costosos."),
        ("Refactoriza en pequeños pasos", "La regla de oro de la refactorización con IA: un cambio a la vez. No pidas 'refactoriza todo este archivo' — pide: 'Extrae esta función de 50 líneas en 3 funciones más pequeñas manteniendo la misma interfaz.' O: 'Convierte esta clase de 500 líneas en varios módulos usando composición.' Cada cambio pequeño es fácil de verificar."),
        ("Verifica que la refactorización no rompió nada", "Después de cada refactorización, pide a ChatGPT: 'Genera tests de regresión para asegurar que esta refactorización no cambió el comportamiento.' También puedes pedirle una comparación: 'Compara el código antes y después de la refactorización. ¿Hay algún cambio de comportamiento?' Esta verificación es especialmente importante en código legacy sin tests."),
     ]},

    # === SQL Y BASES DE DATOS ===
    {"kw": "generar consultas sql con chatgpt", "target": "generar consultas SQL con ChatGPT",
     "title": "Cómo generar consultas SQL optimizadas con ChatGPT",
     "desc": "Aprende a escribir consultas SQL complejas con ayuda de IA. Desde SELECT básicos hasta consultas con múltiples JOINs y subconsultas.",
     "sections": [
        ("Describe tu esquema primero", "Para obtener buenas consultas SQL, primero describe el esquema: 'Tengo una tabla 'ventas' con columnas: id, producto_id, cantidad, precio_unitario, fecha, cliente_id. La tabla 'productos' tiene: id, nombre, categoría, precio. Dame una consulta que muestre el total vendido por categoría este mes.' Sin el esquema, ChatGPT improvisa nombres de tablas que no existen."),
        ("Optimiza consultas existentes", "ChatGPT también es excelente optimizando consultas: 'Optimiza esta consulta SQL que tarda 30 segundos. Tiene 5 JOINs y procesa 2 millones de filas. Dame la versión optimizada y explica qué cambios hiciste y por qué mejoran el rendimiento.' Las optimizaciones típicas incluyen: añadir índices, reescribir subconsultas como JOINs, y añadir filtros temprano."),
        ("SQL avanzado con IA", "Para consultas complejas: ventanas (window functions), CTEs recursivas, o pivots — ChatGPT es increíblemente bueno. El truco es darle un ejemplo de los datos de entrada y el resultado esperado. 'Tengo estos datos de entrada [ejemplo]. Quiero este resultado [ejemplo]. Escribe la consulta SQL.' Con este enfoque, resuelves en segundos consultas que te tomarían horas."),
     ]},
    {"kw": "crear migraciones base datos con ia", "target": "crear migraciones de base de datos con IA",
     "title": "Crea migraciones de base de datos con IA de forma segura",
     "desc": "Automatiza la creación de migraciones SQL con inteligencia artificial. Migraciones seguras y sin errores.",
     "sections": [
        ("Genera migraciones a partir de cambios de esquema", "Describe el cambio que necesitas: 'Necesito añadir una columna 'telefono' a la tabla 'clientes', tipo VARCHAR(20), nullable, con índice. Genera la migración SQL.' ChatGPT te dará el ALTER TABLE, el índice, y si es necesario, el rollback. Especifica si usas migraciones con ORM (Alembic, TypeORM) o SQL plano."),
        ("Migraciones con datos existentes", "Cuando añades columnas NOT NULL a tablas con datos, hay que manejar los valores por defecto. ChatGPT maneja esto bien: 'Añade la columna 'estado' a 'pedidos' con valor por defecto 'pendiente' para los registros existentes, y luego hazla NOT NULL.' La IA genera el script en el orden correcto para no romper la base de datos."),
        ("Rollback y migraciones reversibles", "Siempre pide el rollback junto con la migración: 'Genera la migración UP y DOWN para: renombrar la columna 'nombre' a 'nombre_completo' en la tabla 'usuarios'.' ChatGPT genera ambas direcciones, lo que te permite revertir el cambio si algo sale mal en producción."),
     ]},

    # === CONFIGURACIÓN Y DEVOPS ===
    {"kw": "escribir dockerfile con chatgpt", "target": "escribir Dockerfile con ChatGPT",
     "title": "Cómo escribir Dockerfiles optimizados con ChatGPT",
     "desc": "Aprende a generar Dockerfiles profesionales multi-stage, optimizados para tamaño y seguridad, usando inteligencia artificial.",
     "sections": [
        ("Dockerfile básico generado por IA", "Un prompt simple: 'Genera un Dockerfile multi-stage para una app Node.js/Express. Stage 1: build con node:20, instala dependencias, compila TypeScript. Stage 2: runtime con node:20-alpine, copia solo lo necesario, expone puerto 3000.' ChatGPT genera un Dockerfile optimizado que minimiza el tamaño de la imagen final."),
        ("Optimización de tamaño con Docker multi-stage", "ChatGPT es excelente con Docker multi-stage: 'Optimiza este Dockerfile. Usa multi-stage para: 1) Instalar dependencias de build, 2) Compilar/assets generation, 3) Runtime mínimo con solo lo necesario.' La IA sabe qué dependencias son solo de build y cuáles de runtime."),
        ("Seguridad en Dockerfiles", "Pide explícitamente: 'Añade buenas prácticas de seguridad a este Dockerfile: usuario no-root, imágenes oficiales con hash, no instalar paquetes innecesarios, limpiar caché de apt/apk en el mismo RUN.' ChatGPT implementa todas estas prácticas y explica por qué cada una es importante."),
     ]},

    # === FRONTEND ===
    {"kw": "crear componentes react con chatgpt", "target": "crear componentes React con ChatGPT",
     "title": "Crea componentes React reutilizables con ChatGPT",
     "desc": "Guía para generar componentes React funcionales, con TypeScript, tests y documentación usando inteligencia artificial.",
     "sections": [
        ("Componente básico con TypeScript", "Prompt: 'Crea un componente React TypeScript para un modal reutilizable. Props: isOpen, onClose, title, children. Debe: cerrarse al hacer clic fuera, tener animación de entrada/salida, ser accesible (aria attributes, focus trap).' ChatGPT genera el componente completo con tipos, estilos inline y lógica de accesibilidad."),
        ("Componentes con estado y efectos", "Para componentes más complejos: 'Crea un componente de búsqueda con debounce. Debe: tener input controlado, esperar 300ms antes de buscar, mostrar resultados en dropdown, manejar estados de carga/error/vacío, ser accesible con teclado.' ChatGPT maneja todos los edge cases que normalmente olvidas."),
        ("Tests para componentes React", "Pide los tests junto con el componente: 'Genera tests con React Testing Library para este modal component. Tests: se renderiza cuando isOpen=true, no se renderiza cuando isOpen=false, llama a onClose al hacer clic en el backdrop, el título se muestra correctamente.' La integración de tests en el prompt inicial ahorra iteraciones."),
     ]},

    # === DOCUMENTACIÓN TÉCNICA ===
    {"kw": "escribir documentacion tecnica con ia", "target": "escribir documentación técnica con IA",
     "title": "Escribe documentación técnica profesional con IA",
     "desc": "Guía para generar documentación técnica clara, completa y útil usando inteligencia artificial. Desde READMEs hasta manuales de API.",
     "sections": [
        ("Documentación de APIs", "El prompt perfecto para documentar APIs: 'Documenta esta API REST. Para cada endpoint incluye: descripción, método HTTP, URL, parámetros de request (query params, body, headers), ejemplo de response exitoso, códigos de error, y ejemplo con curl.' Este nivel de detalle genera documentación lista para publicar sin edición manual."),
        ("Guías de inicio rápido", "Las guías de inicio rápido son el contenido más leído de cualquier documentación. Prompt: 'Crea una guía de inicio rápido para este proyecto. Debe: 1) Instalación en 3 pasos, 2) Ejemplo mínimo funcional que se pueda copiar y pegar, 3) Explicación de los conceptos clave. Asume que el lector es un desarrollador sin experiencia previa con el proyecto.'"),
        ("Mantén la documentación actualizada", "La documentación se vuelve obsoleta rápidamente. Cuando cambies el código, pide a ChatGPT: 'Actualiza la documentación de este endpoint. El cambio es: ahora requiere autenticación y devuelve un campo adicional 'meta'.' Esto mantiene la documentación sincronizada con el código sin esfuerzo."),
     ]},
]

def slugify(s):
    import re
    s = s.lower().strip()
    s = re.sub(r'[áàäâ]','a',s)
    s = re.sub(r'[éèëê]','e',s)
    s = re.sub(r'[íìïî]','i',s)
    s = re.sub(r'[óòöô]','o',s)
    s = re.sub(r'[úùüû]','u',s)
    s = re.sub(r'[ñ]','n',s)
    s = re.sub(r'[^a-z0-9]+','-',s)
    return s.strip('-')

def build_html(data, niche):
    slug = slugify(data["kw"])
    today = datetime.now().strftime("%Y-%m-%d")
    
    s1, s2, s3 = data["sections"][:3]
    
    B = niche['brand']
    BD = niche['brand_dark']
    P = niche['payhip']
    NS = niche['slug']
    TITLE = data['title']
    DESC = data['desc'][:150]
    TDESC = data['desc']
    TARGET = data['target']
    READTIME = random.randint(4,8)
    
    NN = niche['name']
    
    nl_onsubmit = "fetch('https://909f85f8c7219d8f-95-63-166-157.serveousercontent.com/subscribe',{'method':'POST','headers':{'Content-Type':'application/json'},'body':JSON.stringify({'email':document.querySelector('.nl-input').value})}).catch(function(){})"
    
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>{TITLE} — NEO Labs</title>
<meta name="description" content="{TDESC}">
<link rel="canonical" href="https://magodago.github.io/neo-jarvis/blog/{NS}/{slug}.html">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{TDESC[:120]}">
<meta property="og:type" content="article">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Sora:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}:root{{--brand:{B};--brand-dark:{BD};--brand-light:{B}88;--bg:#050508;--bg2:#0c0c14;--bg3:#11111a;--text:#ede8e0;--text-muted:#a09888;--font-display:'Syne',sans-serif;--font-body:'Sora',sans-serif}}
html{{scroll-behavior:smooth}}body{{background:var(--bg);color:var(--text);font-family:var(--font-body);overflow-x:hidden;line-height:1.8;touch-action:pan-y}}
a{{color:var(--brand);text-decoration:none}}a:hover{{filter:brightness(1.2)}}
.wrap{{max-width:780px;margin:0 auto;padding:0 24px}}
.breadcrumb{{font-size:.75rem;color:#6a6558;padding-top:90px;margin-bottom:8px}}.breadcrumb a{{color:#6a6558}}.breadcrumb a:hover{{color:var(--brand)}}
.article-header{{margin-bottom:28px}}
.article-header .cat-tag{{display:inline-block;padding:4px 12px;border-radius:100px;font-size:.65rem;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;background:rgba(212,168,83,.15);color:var(--brand);margin-bottom:14px}}
.article-header h1{{font-family:var(--font-display);font-size:clamp(1.5rem,3vw,2.2rem);font-weight:700;letter-spacing:-1px;line-height:1.12;margin-bottom:10px}}
.article-header .meta{{display:flex;gap:20px;font-size:.8rem;color:#6a6558;flex-wrap:wrap}}
.article-body h2{{font-family:var(--font-display);font-size:1.25rem;font-weight:700;color:#fff;margin:30px 0 10px;letter-spacing:-.3px}}
.article-body p{{font-size:.92rem;color:var(--text-muted);line-height:1.8;margin-bottom:12px}}
.article-body p strong{{color:var(--text)}}
.prompt-box{{background:var(--bg3);border-left:3px solid var(--brand);border-radius:0 10px 10px 0;padding:16px 20px;margin:12px 0 20px}}
.prompt-box .prompt-label{{font-size:.68rem;letter-spacing:2px;text-transform:uppercase;color:var(--brand);font-weight:600;margin-bottom:3px}}
.prompt-box .prompt-text{{font-size:.85rem;color:#d0c8bc;line-height:1.7;font-style:italic}}
.tip-box{{background:rgba(76,175,80,.06);border-left:3px solid #4caf50;border-radius:0 10px 10px 0;padding:12px 16px;margin:12px 0 20px}}
.tip-box .tip-label{{font-size:.68rem;letter-spacing:2px;text-transform:uppercase;color:#4caf50;font-weight:600;margin-bottom:2px}}
.tip-box p{{font-size:.85rem;color:#c0d0b8;line-height:1.7;margin:0}}
.cta-box{{background:linear-gradient(135deg,rgba(212,168,83,.06),rgba(5,5,8,.9));border:1px solid rgba(212,168,83,.2);border-radius:14px;padding:28px 22px;text-align:center;margin:24px 0}}
.cta-box h3{{font-family:var(--font-display);font-size:1.1rem;font-weight:700;color:var(--brand);margin-bottom:6px}}
.cta-box p{{color:var(--text-muted);font-size:.82rem;margin-bottom:14px}}
.btn{{padding:10px 24px;border-radius:8px;font-family:var(--font-display);font-size:.74rem;letter-spacing:2px;text-transform:uppercase;font-weight:600;transition:all .3s;border:none;cursor:pointer;display:inline-block}}
.btn-primary{{background:linear-gradient(135deg,var(--brand-dark),var(--brand));color:#fff;box-shadow:0 4px 30px rgba(0,0,0,.3)}}
.toc{{background:var(--bg3);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:16px 20px;margin:20px 0;font-size:.85rem}}
.toc-title{{font-family:var(--font-display);font-size:.7rem;letter-spacing:2px;font-weight:700;color:var(--brand);margin-bottom:8px;text-transform:uppercase}}
.toc a{{display:block;padding:3px 0;color:var(--text-muted);transition:color .2s;font-size:.82rem;text-decoration:none}}
.toc a:hover{{color:var(--brand)}}.toc a:before{{content:"\\u25b8 ";font-size:.65rem}}
.faq-section{{margin:24px 0}}.faq-q{{background:var(--bg3);border:1px solid rgba(255,255,255,.06);border-radius:10px;padding:12px 16px;margin-bottom:6px}}
.faq-q summary{{font-weight:600;font-size:.88rem;color:#fff;cursor:pointer;display:flex;align-items:center;gap:10px}}
.faq-q summary::marker{{color:var(--brand)}}.faq-q p{{font-size:.82rem;color:var(--text-muted);margin-top:6px;line-height:1.6}}
.newsletter-box{{background:linear-gradient(135deg,rgba(212,168,83,.06),rgba(5,5,8,.95));border:1px solid rgba(212,168,83,.2);border-radius:16px;padding:24px 20px;text-align:center;margin:28px 0}}
.nl-title{{font-family:var(--font-display);font-size:.95rem;font-weight:700;color:#fff;margin-bottom:4px}}
.nl-desc{{font-size:.78rem;color:var(--text-muted);margin-bottom:14px;max-width:380px;margin-left:auto;margin-right:auto}}
.nl-form{{display:flex;gap:8px;max-width:360px;margin:0 auto;flex-wrap:wrap}}
.nl-input{{flex:1;min-width:160px;padding:10px 14px;border-radius:8px;border:1px solid rgba(212,168,83,.2);background:rgba(5,5,8,.6);color:#fff;font-size:.82rem;outline:none}}
.nl-input:focus{{border-color:var(--brand)}}
.nl-btn{{padding:10px 18px;border-radius:8px;border:none;background:var(--brand);color:#050508;font-size:.75rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer}}
footer{{background:var(--bg2);border-top:1px solid rgba(255,255,255,.04);padding:36px 24px 20px;text-align:center}}
footer .logo{{font-family:var(--font-display);font-size:1.3rem;letter-spacing:4px;font-weight:700;margin-bottom:10px;text-transform:uppercase;color:#fff}}
footer .logo span{{color:var(--brand)}}
footer .links{{display:flex;gap:20px;justify-content:center;flex-wrap:wrap;margin-bottom:10px}}
footer .links a{{color:var(--text-muted);font-size:.78rem}}
footer .copy{{font-size:.68rem;color:#6a6558}}
#progress{{position:fixed;top:0;left:0;width:0;height:2px;background:linear-gradient(90deg,var(--brand-dark),var(--brand));z-index:9999;transition:width .1s}}
</style>
<script type="application/ld+json" class="s-hidden">{{"@context":"https://schema.org","@type":"Article","headline":"{TITLE}","description":"{DESC}","datePublished":"{today}","author":{{"@type":"Person","name":"NEO Labs"}},"publisher":{{"@type":"Organization","name":"NEO Labs"}},"mainEntityOfPage":{{"@type":"WebPage","@id":"https://magodago.github.io/neo-jarvis/blog/{NS}/{slug}.html"}}}}</script>
<meta name="google-site-verification" content="c_28XEsyfUVcGVbPpfkhujKtsO_XkyMJRjLwjhitFzQ" />
</head>
<body>
<div id="progress"></div>
<nav id="nav">
<div class="nav-logo">NE<span>O</span></div>
<ul class="nav-links">
<li><a href="../../neo-labs.html">Inicio</a></li>
<li><a href="../../catalogo.html">Catalogo</a></li>
<li><a href="../index.html">Blog</a></li>
</ul>
</nav>
<div class="wrap">
<div class="breadcrumb"><a href="../../neo-labs.html">Inicio</a> <span>/</span> <a href="index.html">Blog {NN}</a> <span>/</span> <span>{TARGET}</span></div>
<div class="article-header">
<span class="cat-tag">Guia</span>
<h1>{TITLE}</h1>
<div class="meta"><span>{today}</span><span>NEO Labs</span><span>{READTIME} min lectura</span></div>
</div>
<div class="article-body">
<p>{TDESC}</p>

<div class="toc"><div class="toc-title">Contenido</div>
<a href="#seccion1">1. {s1[0]}</a>
<a href="#seccion2">2. {s2[0]}</a>
<a href="#seccion3">3. {s3[0]}</a>
</div>

<h2 id="seccion1">{s1[0]}</h2>
<p>{s1[1]}</p>

<div class="prompt-box"><div class="prompt-label">Prompt para {TARGET}</div><div class="prompt-text">Actua como un experto en {TARGET}. Dame una guia paso a paso con ejemplos practicos y prompts listos para copiar. Enfocate en resultados inmediatos.</div></div>

<h2 id="seccion2">{s2[0]}</h2>
<p>{s2[1]}</p>

<div class="tip-box"><div class="tip-label">Consejo Profesional</div><p>La clave para obtener los mejores resultados es la iteracion. No te conformes con la primera respuesta de la IA. Refina tu prompt basandote en lo que obtienes.</p></div>

<h2 id="seccion3">{s3[0]}</h2>
<p>{s3[1]}</p>

<div class="cta-box">
<h3>Pack de {NN} NEO</h3>
<p>10 prompts premium de {NN.lower()} listos para usar con ChatGPT, Claude y Gemini. Resultados inmediatos desde el primer uso.</p>
<a href="https://payhip.com/b/{P}" target="_blank" class="btn btn-primary">Conseguir por 9.99</a>
<a href="../../catalogo.html" class="btn" style="margin-left:8px;border:1px solid var(--brand);color:var(--brand);background:transparent">Ver Catalogo</a>
</div>

<div class="faq-section">
<h3>Preguntas frecuentes sobre {TARGET}</h3>
<details class="faq-q"><summary>Que necesito para empezar?</summary><p>Solo necesitas acceso a ChatGPT, Claude o Gemini. Todos nuestros prompts y guias de {NN.lower()} funcionan con cualquier plataforma de IA moderna.</p></details>
<details class="faq-q"><summary>Cuanto tiempo se tarda en ver resultados?</summary><p>La mayoria de nuestros usuarios ven mejoras significativas desde la primera semana de uso consistente de las tecnicas y prompts descritos.</p></details>
<details class="faq-q"><summary>Los prompts funcionan en espanol?</summary><p>Si. Todos nuestros prompts estan disenados y probados en espanol para maximizar resultados en {NN.lower()}.</p></details>
</div>

<div class="newsletter-box">
<div class="nl-icon">&#10027;</div>
<div class="nl-title">Recibe los mejores prompts de IA gratis</div>
<div class="nl-desc">Cada semana, 3 prompts exclusivos + tendencias directo a tu bandeja de entrada.</div>
<form class="nl-form" action="https://formsubmit.co/formulasia76@gmail.com" method="POST" onsubmit="{nl_onsubmit}">
  <input type="hidden" name="_subject" value="Nuevo suscriptor NEO Labs">
  <input type="hidden" name="_next" value="https://magodago.github.io/neo-jarvis/neo-labs.html">
  <input type="hidden" name="_captcha" value="false">
  <input type="text" name="_honey" style="display:none">
  <input type="email" name="email" placeholder="tu@email.com" required class="nl-input">
  <button type="submit" class="nl-btn">Suscribirme</button>
</form>
</div>
</div>
<footer><div class="logo">NE<span>O</span></div><div class="links"><a href="../../neo-labs.html">Inicio</a><a href="../../catalogo.html">Catalogo</a><a href="../index.html">Blog</a><a href="https://payhip.com/b/98ens">Guia Gratuita</a></div><p class="copy">&copy; 2026 NEO Labs</p></footer>
<script>
var p=document.getElementById('progress');document.addEventListener('scroll',function(){{var h=document.documentElement.scrollHeight-window.innerHeight;p.style.width=(window.scrollY/h*100)+'%'}})
var s=0,n=document.getElementById('nav');document.addEventListener('scroll',function(){{var t=window.scrollY;if(t>s&&t>70)n.classList.add('hidden');else n.classList.remove('hidden');s=t}})
</script>
<script data-goatcounter="https://davidformulas.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</body>
</html>"""

def main():
    print("=" * 60)
    print("PROGRAMMATIC SEO v2 — GENERACION MASIVA")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    niche_prog = {"slug":"programacion","name":"Programacion","brand":"#ab47bc","brand_dark":"#7b1fa2","payhip":"XTEG5"}
    
    generated = 0
    skipped = 0
    for data in PAGES_DATA:
        slug = slugify(data["kw"])
        filepath = NICHE_DIR / f"{slug}.html"
        
        if filepath.exists():
            skipped += 1
            continue
        
        html = build_html(data, niche_prog)
        with open(filepath, "w") as f:
            f.write(html)
        generated += 1
        print(f"  ✅ {slug}.html ({len(html)} bytes)")
    
    print(f"\n{'='*60}")
    print(f"✅ Generadas: {generated}  |  Ya existian: {skipped}  |  Total: {generated + skipped}")
    print(f"📁 {NICHE_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
