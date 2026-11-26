// Se ejecuta en la consola de https://www.linkedin.com/in/adrian-copa-jara/recent-activity/all/ (sesion iniciada).
// Deja las publicaciones PROPIAS en window.__res = [{fecha, url, texto}] y pone un boton verde "COPIAR DATOS"
// que, al hacer clic real, copia el JSON al portapapeles. Cambia ULTIMO_ID por el id mas reciente ya importado.
(async () => {
  const ULTIMO_ID = window.ULTIMO_ID || '0';
  for (let i = 0; i < 6; i++) { window.scrollTo(0, document.body.scrollHeight); await new Promise(r => setTimeout(r, 1500)); }
  window.scrollTo(0, 0);
  [...document.querySelectorAll('button')].filter(b => /^…?\s*más$|ver más|see more/i.test(b.innerText.trim())).forEach(b => b.click());
  await new Promise(r => setTimeout(r, 1500));
  const sel = 'a[href*="post-summary"]';
  const res = [];
  for (const a of document.querySelectorAll(sel)) {
    const id = a.href.match(/activity:(\d+)/)[1];
    if (!(id > ULTIMO_ID)) continue;
    let c = a;
    while (c.parentElement && c.parentElement.querySelectorAll(sel).length <= 1) c = c.parentElement;
    const lines = c.innerText.split('\n').map(s => s.trim());
    if (!/Tú/.test(lines.slice(0, 8).join('|'))) continue;           // solo publicaciones propias
    if (/han compartido esto/.test(lines.slice(0, 4).join(' '))) continue; // no reposts
    const i = lines.findIndex((l, k) => k > 2 && /^(\d+\s*(min|h|d|sem|semana|semanas|mes|meses|a|año|años))\s*•/.test(l));
    if (i < 0) continue;
    const body = [];
    for (let k = i + 1; k < lines.length; k++) {
      const l = lines[k];
      if (/^(\d[\d.,]*|Recomendar|Comentar|Compartir|Enviar|Me gusta|Ver analíticas|Ver más analíticas)$/.test(l) || /^\d[\d.,]*\s*(impresiones|comentarios|visualizaciones)/i.test(l)) break;
      body.push(l);
    }
    const texto = body.join('\n').replace(/\n{3,}/g, '\n\n').replace(/…\s*más\s*$/, '').trim();
    res.push({ fecha: new Date(Number(BigInt(id) >> 22n)).toISOString().slice(0, 10), url: 'https://www.linkedin.com/feed/update/urn:li:activity:' + id + '/', texto });
  }
  window.__res = res;
  const b = document.createElement('button');
  b.id = 'cpbtn'; b.textContent = 'COPIAR DATOS';
  b.style.cssText = 'position:fixed;top:80px;left:20px;z-index:99999;padding:20px 30px;font-size:22px;background:#0a0;color:#fff';
  b.onclick = () => navigator.clipboard.writeText(JSON.stringify(window.__res)).then(() => { b.textContent = 'COPIADO ' + window.__res.length; }, e => { b.textContent = 'ERR ' + e.message; });
  document.body.appendChild(b);
  return res.length;
})();
