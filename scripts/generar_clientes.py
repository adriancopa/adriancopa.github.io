"""Genera la version del portafolio para CLIENTES (carpeta clientes/) a partir de index.html y blog.html.

Objetivo: evitar conflicto de intereses. La version para clientes NO menciona al empleo actual
(empleo actual): quita su logo, su puesto en la trayectoria y su nombre en logros y publicaciones
(los resultados quedan atribuidos a "Consumo masivo"), y se presenta como Consultor de Operaciones.
No se indexa en buscadores (noindex). Se ejecuta automaticamente al publicar (scripts/publicar.ps1).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "clientes"
BASE = "https://adriancopa.github.io"
PROHIBIDO = re.compile(r"novaqu", re.I)


def sub1(patron, repl, texto, flags=re.S):
    nuevo, n = re.subn(patron, repl, texto, count=1, flags=flags)
    if n != 1:
        sys.exit(f"ERROR: no se encontro el patron: {patron[:70]}")
    return nuevo


def rep(texto, viejo, nuevo):
    if viejo not in texto:
        sys.exit(f"ERROR: no se encontro: {viejo[:70]}")
    return texto.replace(viejo, nuevo)


EMP = "Empresa líder de productos de limpieza"


def comunes(h, ruta):
    h = re.sub(r"(?<![\w./-])assets/", "../assets/", h)           # los recursos viven en la raiz
    h = sub1(r'<link rel="canonical" href="[^"]*" />', f'<meta name="robots" content="noindex, nofollow" />\n  <link rel="canonical" href="{BASE}/clientes/{ruta}" />', h)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf"\g<1>{BASE}/clientes/{ruta}\2", h)
    return h


def index():
    h = (ROOT / "index.html").read_text(encoding="utf-8")
    # Mismo contenido que el portafolio original; solo se reemplaza el nombre del empleo actual.
    h = rep(h, "<b>Novaquimica SRL</b>", f"<b>{EMP}</b>")
    h = rep(h, "'Novaquimica SRL'", "'Productos de limpieza'")
    h = rep(h, '"name": "Novaquimica SRL"', f'"name": "{EMP}"')
    h = rep(h, "<b>Unilever, Astrix y Novaquimica</b>", f"<b>Unilever, Astrix y una empresa líder de productos de limpieza</b>")
    h = rep(h, "<span>Novaquimica</span>", "<span>Líder en limpieza</span>")
    h = rep(h, "Unilever, Novaquimica y Astrix.", "Unilever, una empresa líder de limpieza y Astrix.")
    h = rep(h, 'data-f="nova">Novaquimica<', 'data-f="nova">Empresa líder de limpieza<')
    h = h.replace("<i>Novaquimica</i>", "<i>Empresa líder de limpieza</i>").replace("<small>Novaquimica</small>", "<small>Empresa líder de limpieza</small>")
    return comunes(h, "").replace("../assets/CV_Adrian_Copa_2026.pdf", "../assets/CV_Adrian_Copa_Clientes.pdf")

def blog():
    h = (ROOT / "blog.html").read_text(encoding="utf-8")
    return comunes(h, "blog.html")


def posts():
    t = (ROOT / "data" / "posts.json").read_text(encoding="utf-8")
    t = re.sub(r"En Novaquimica\b", "En una empresa líder de productos de limpieza", t)
    t = re.sub(r"Novaquimica( SRL)?", "una empresa líder de productos de limpieza", t)
    json.loads(t)  # valida
    return t


def main():
    (OUT / "data").mkdir(parents=True, exist_ok=True)
    salidas = {OUT / "index.html": index(), OUT / "blog.html": blog(), OUT / "data" / "posts.json": posts()}
    for ruta, txt in salidas.items():
        if PROHIBIDO.search(txt):
            sys.exit(f"ERROR: {ruta.name} todavia menciona al empleo actual")
        ruta.write_text(txt, encoding="utf-8", newline="\n")
    print("clientes/ generado:", ", ".join(p.relative_to(ROOT).as_posix() for p in salidas))


if __name__ == "__main__":
    main()
