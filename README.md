# Portafolio de Adrian Copa

Gerente de Operaciones · Consumo masivo (Home & Personal Care).
Sitio estático publicado con GitHub Pages.

- `index.html` — portafolio principal.
- `blog.html` — blog con todas las publicaciones de LinkedIn y TikTok, filtrables por tema.
- `data/posts.json` — contenido del blog.
- `scripts/importar_linkedin.py` — importa publicaciones de LinkedIn y las clasifica por segmento.

## Actualizar el blog con publicaciones nuevas de LinkedIn

1. Obtén tus publicaciones: pídele a Claude "actualiza el blog" (las lee desde tu sesión de LinkedIn),
   o descarga la exportación oficial (LinkedIn → Configuración → Privacidad de datos →
   Obtener una copia de tus datos → Publicaciones) y ubica el archivo `Shares.csv`.
2. Ejecuta:

   ```
   python scripts/importar_linkedin.py ruta/a/Shares.csv
   ```

   Solo agrega las publicaciones nuevas; nunca duplica.
3. Sube los cambios (`git add -A && git commit -m "Blog: nuevas publicaciones" && git push`).
   GitHub Pages publica la actualización en uno o dos minutos.

Los videos nuevos de TikTok aparecen solos en la pestaña «Lo más reciente» de la sección de videos.
