"""Importa publicaciones de LinkedIn al blog (data/posts.json), clasificadas por segmento.

Fuentes aceptadas:
  - Shares.csv de la exportación oficial de LinkedIn (Configuración > Privacidad de datos >
    Obtener una copia de tus datos > "Publicaciones/Shares").
  - Un JSON [{ "fecha": "YYYY-MM-DD", "url": "...", "texto": "..." }] (lectura desde el perfil).

Uso:  python scripts/importar_linkedin.py <Shares.csv | publicaciones.json>
Se puede ejecutar cada vez que haya publicaciones nuevas: no duplica las que ya existen.
"""
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "data" / "posts.json"

# Segmento -> palabras clave (sin tildes, en minúscula). El de más coincidencias gana.
SEGMENTOS = {
    "Costos y rentabilidad": ["costo", "margen", "rentab", "precio", "ganancia", "utilidad", "dinero", "caja", "flujo", "ahorro", "gasto"],
    "Inventarios y logística": ["inventario", "stock", "almacen", "bodega", "despacho", "logistic", "compras", "proveedor", "rotacion"],
    "Calidad": ["calidad", "iso", "auditor", "no conformidad", "rechazo", "reclamo", "inocuidad", "defecto", "control de calidad"],
    "Producción y mejora continua": ["produccion", "planta", "merma", "rendimiento", "lean", "six sigma", "kaizen", "proceso", "eficiencia", "fabrica", "manufactura", "mejora continua", "mejora", "poka", "yoke", "5s", "deming", "pdca", "optimiz", "innovac", "desperdicio"],
    "Planificación, datos e IA": ["planificacion", "s&op", "mrp", "dato", "dashboard", "indicador", "kpi", "erp", "sap", "inteligencia artificial", " ia ", "automatiz", "claude", "excel"],
    "Liderazgo y equipos": ["lider", "equipo", "jefe", "supervis", "delegar", "responsab", "cultura", "motivac", "mando"],
    "Carrera profesional": ["carrera", "trabajo", "empleo", "cv", "curriculum", "entrevista", "ascenso", "aprendizaje", "curso", "certific", "libro"],
    "Pymes y emprendimiento": ["pyme", "dueno", "emprend", "negocio", "empresa", "crecer", "crecimiento", "ventas", "cliente"],
}


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def segmentar(texto, titulo=""):
    # El tema del título pesa el triple que el del cuerpo: es lo que la publicación promete.
    t, tt = f" {norm(texto)} ", f" {norm(titulo)} "
    puntajes = {seg: sum(t.count(k) + 3 * tt.count(k) for k in claves) for seg, claves in SEGMENTOS.items()}
    orden = sorted(puntajes.items(), key=lambda kv: -kv[1])
    segs = [s for s, p in orden if p > 0][:2]
    return segs or ["Pymes y emprendimiento"]


def slugify(s, usados):
    base = re.sub(r"[^a-z0-9]+", "-", norm(s)).strip("-")[:60].strip("-") or "publicacion"
    slug, n = base, 2
    while slug in usados:
        slug, n = f"{base}-{n}", n + 1
    usados.add(slug)
    return slug


def limpiar(texto):
    # NFKC convierte las "negritas" Unicode (𝗘𝘀𝘁𝗮𝗺𝗼𝘀) en texto normal, legible para buscadores.
    texto = unicodedata.normalize("NFKC", texto).replace("\r", "")
    texto = re.sub(r"\n?hashtag\n?#", " #", texto)
    texto = re.sub(r'""', '"', texto)
    return texto.strip()


def a_post(fecha, url, texto, usados):
    texto = limpiar(texto)
    parrafos = [p.strip() for p in re.split(r"\n\s*\n|\n", texto) if p.strip()]
    sin_tags = [p for p in parrafos if not re.fullmatch(r"(#\S+\s*)+", p)]
    primera = sin_tags[0] if sin_tags else texto[:90]
    titulo = re.split(r"(?<=[.!?])\s", primera)[0].strip(' "“”«»¨-–—•*')
    titulo = (titulo[:95] + "…") if len(titulo) > 96 else titulo
    resto = " ".join(sin_tags[1:]) or primera
    resumen = (resto[:220] + "…") if len(resto) > 220 else resto
    return {
        "slug": slugify(titulo, usados),
        "fecha": fecha,
        "titulo": titulo,
        "resumen": resumen,
        "etiquetas": segmentar(texto, titulo),
        # El título ya se muestra como encabezado: no se repite como primer párrafo.
        "cuerpo": sin_tags[1:] if sin_tags and sin_tags[0].strip(' "“”«»¨').startswith(titulo.rstrip('…')) else sin_tags,
        "tiktok": "",
        "linkedin": url,
        "fuente": "linkedin",
    }


def leer(origen):
    ruta = Path(origen)
    if ruta.suffix.lower() == ".csv":
        with ruta.open(encoding="utf-8-sig", newline="") as f:
            for fila in csv.DictReader(f):
                texto = fila.get("ShareCommentary") or ""
                if not texto.strip():
                    continue  # repost sin comentario propio
                yield (fila.get("Date") or "")[:10], fila.get("ShareLink") or "", texto
    else:
        for p in json.loads(ruta.read_text(encoding="utf-8")):
            if (p.get("texto") or "").strip():
                yield p.get("fecha", "")[:10], p.get("url", ""), p["texto"]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    actuales = json.loads(POSTS.read_text(encoding="utf-8")) if POSTS.exists() else []
    urls = {p.get("linkedin") for p in actuales if p.get("linkedin")}
    usados = {p["slug"] for p in actuales}
    nuevos = [a_post(f, u, t, usados) for f, u, t in leer(sys.argv[1]) if not (u and u in urls)]
    todos = sorted(actuales + nuevos, key=lambda p: p["fecha"], reverse=True)
    POSTS.write_text(json.dumps(todos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    conteo = {}
    for p in nuevos:
        conteo[p["etiquetas"][0]] = conteo.get(p["etiquetas"][0], 0) + 1
    print(f"{len(nuevos)} publicaciones nuevas importadas ({len(todos)} en total).")
    for seg, n in sorted(conteo.items(), key=lambda kv: -kv[1]):
        print(f"  {seg}: {n}")


if __name__ == "__main__":
    main()
