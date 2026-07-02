#!/usr/bin/env python3
"""Analisis de sectores para NEO Leads Pro"""
print("=" * 75)
print("  ANALISIS DE SECTORES — NEO LEADS PRO")
print("=" * 75)
print()

sectores = [
    # (nombre, datos, dolor, poder, escala, analisis)
    # B2B
    ("B2B - Clinicas dentales",  8, 8, 8, 7, "Alto poder adquisitivo. Ya gastan 300-1000EUR/mes en Ads. Buenos datos (66% email)."),
    ("B2B - Talleres mecanicos",  7, 9, 5, 8, "DOLOR MAXIMO (temporada baja=0 clientes). Poder bajo pero hay MUCHISIMOS."),
    ("B2B - Restaurantes",        9, 7, 4, 10,"Excelentes datos (434 leads). Dolor moderado. Presupuesto bajo."),
    ("B2B - Peluquerias",         8, 8, 3, 9, "Muchos leads. Presupuesto casi nulo para marketing."),
    ("B2B - Inmobiliarias",       2, 9, 9, 5, "MAXIMO poder (un lead=miles EUR). Pero SOLO 15 leads en DB."),
    ("B2B - Clinicas estetica",   7, 7, 8, 6, "Tratamientos 100-500EUR. Buenos datos. Pagan bien."),
    # B2C
    ("B2C - Clinicas dentales",   8, 8, 9, 7, "Paciente nuevo=500-2000EUR/ano. Pagarian 200-500EUR/mes. EL MEJOR."),
    ("B2C - Inmobiliarias",       2, 9, 10,5, "Comision por venta=miles EUR. Pagarian 500-2000EUR/mes. Faltan datos."),
    ("B2C - Clinicas estetica",   7, 7, 8, 6, "Tratamientos 100-500EUR. Buenos datos. Pagan bien."),
    ("B2C - Restaurantes",        9, 6, 3, 10,"Muchos datos pero margen bajo. No pagarian mucho."),
]

print(f"{'SECTOR':35s} {'DATOS':>5s} {'DOLOR':>5s} {'PODER':>5s} {'ESCALA':>5s}  {'TOTAL':>5s}")
print("-" * 65)
for s, d, dol, p, e, analisis in sectores:
    total = d + dol + p + e
    barra = "#" * (total // 2) + "." * ((35 - total // 2))
    print(f"{s:35s} {d:>5d} {dol:>5d} {p:>5d} {e:>5d}  {total:>5d}  {barra}")

print()
print("=" * 75)
print("  TOP 3 POR PUNTUACION TOTAL")
print("=" * 75)
sorted_s = sorted(sectores, key=lambda x: -(x[1]+x[2]+x[3]+x[4]))
for i, (s, d, dol, p, e, analisis) in enumerate(sorted_s[:3], 1):
    total = d + dol + p + e
    print(f"\n  #{i}  {s}")
    print(f"       Puntuacion: {total}/40")
    print(f"       {analisis}")

print()
print("=" * 75)
print("  CONCLUSION")
print("=" * 75)
print()
print("  LINEA 1 (AHORA): B2B para Clinicas dentales + Talleres + Restaurantes")
print("  Fuente: Google Places API (GRATIS)")
print("  Precio: 97-397EUR/mes")
print("  Margen: 100%")
print()
print("  LINEA 2 (DESPUES): B2C para Clinicas dentales + Inmobiliarias")
print("  Fuente: Datos comprados (0.02-3EUR/lead) o scraping reviews")
print("  Precio: 197-597EUR/mes")
print("  Margen: 50-90%")
print()
print("  RECOMENDACION: Arrancar con LINEA 1 que ya funciona a coste 0.")
print("  Cuando tengas clientes estables, expandir a LINEA 2.")
