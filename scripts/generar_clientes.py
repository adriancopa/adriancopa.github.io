"""Genera la version del portafolio para CLIENTES (carpeta clientes/) a partir de index.html y blog.html.

Objetivo: evitar conflicto de intereses. La version para clientes NO menciona al empleo actual
(Novaquimica): quita su logo, su puesto en la trayectoria y su nombre en logros y publicaciones
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


def comunes(h, ruta):
    h = h.replace("Gerente de Operaciones", "Consultor de Operaciones")
    h = re.sub(r"(?<![\w./-])assets/", "../assets/", h)           # los recursos viven en la raiz
    h = sub1(r'<link rel="canonical" href="[^"]*" />', f'<meta name="robots" content="noindex, nofollow" />\n  <link rel="canonical" href="{BASE}/clientes/{ruta}" />', h)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf"\g<1>{BASE}/clientes/{ruta}\2", h)
    h = re.sub(r'(<meta property="og:image" content=")[^"]*(")', r"\g<1>" + BASE + r"/assets/foto-perfil.jpg\2", h)
    return h


def index():
    h = (ROOT / "index.html").read_text(encoding="utf-8")
    # Trayectoria: quitar el puesto actual y dejar la consultoria como puesto vigente
    h = sub1(r'<article class="job open">.*?</article>\s*', "", h)
    h = rep(h, '<article class="job">\n          <div class="when">2024 — Hoy</div>', '<article class="job open">\n          <div class="when">2024 — Hoy</div>')
    h = rep(h, 'aria-expanded="false" aria-controls="job-d2"', 'aria-expanded="true" aria-controls="job-d2"')
    # Estructurados y textos
    h = rep(h, '"worksFor": {"@type": "Organization", "name": "Novaquimica SRL"}, ', "")
    h = rep(h, "<b>Unilever, Astrix y Novaquimica</b>", "<b>consumo masivo, en Unilever y Astrix,</b>")
    h = rep(h, '<span>Novaquimica</span>', "")
    h = rep(h, "+15 resultados medibles en Unilever, Novaquimica y Astrix.", "+15 resultados medibles en consumo masivo.")
    h = rep(h, "['factory', 'Gerente de Operaciones', 'Novaquimica SRL', 'o']", "['factory', 'Operaciones y mejora continua', 'Consumo masivo', 'o']")
    h = rep(h, '<button data-f="nova">Novaquimica</button>', '<button data-f="gop">Gerencia de operaciones</button>')
    h = h.replace('data-c="nova"', 'data-c="gop"')
    h = h.replace("<i>Novaquimica</i>", "<i>Consumo masivo</i>").replace("<small>Novaquimica</small>", "<small>Consumo masivo</small>")
    h = comunes(h, "")
    h = rep(h, f'{BASE}/clientes/"', f'{BASE}/clientes/"')  # canonical ya apunta a la carpeta
    return h


def blog():
    h = (ROOT / "blog.html").read_text(encoding="utf-8")
    return comunes(h, "blog.html")


def posts():
    t = (ROOT / "data" / "posts.json").read_text(encoding="utf-8")
    t = re.sub(r"En Novaquimica\b", "En una planta de consumo masivo", t)
    t = re.sub(r"Novaquimica( SRL)?", "una planta de consumo masivo", t)
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
