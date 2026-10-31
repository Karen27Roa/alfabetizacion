/* Búho guía · interacciones. Todo respeta prefers-reduced-motion. */
(function () {
  const reducir = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const raf2 = (fn) => requestAnimationFrame(() => requestAnimationFrame(fn));

  /* ---- Números que cuentan hasta su valor ---- */
  function contar(el) {
    const fin = Number(el.dataset.count);
    if (reducir || !isFinite(fin)) { el.textContent = fin; return; }
    const dur = 1000; let t0 = null;
    el.textContent = 0;
    (function paso(t) {
      if (t0 === null) t0 = t;
      const p = Math.min((t - t0) / dur, 1);
      el.textContent = Math.round(fin * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(paso);
    })(performance.now());
  }

  /* ---- Barras de variables (ancho inicial en el HTML; aquí solo se anima) ---- */
  function barras(root) {
    root.querySelectorAll('.fila-var .relleno').forEach((el) => {
      const meta = el.style.width; el.style.width = '0';
      raf2(() => { el.style.width = meta; });
    });
  }

  /* ---- Anillo del puntaje ---- */
  function anillos(root) {
    root.querySelectorAll('.anillo').forEach((a) => {
      const pct = (Number(a.dataset.score) - 18) / 72, c = a.querySelector('.valor-a');
      c.style.strokeDashoffset = 565.49;
      raf2(() => { c.style.strokeDashoffset = 565.49 * (1 - pct); });
    });
  }

  /* ---- Termómetro de niveles con la posición de la persona ---- */
  function termometros(root) {
    root.querySelectorAll('.termometro').forEach((t) => {
      const s = +t.dataset.score, b = +t.dataset.bajo, m = +t.dataset.medio;
      const partes = [b - 17, m - b, 90 - m];
      t.querySelectorAll('.tramos i, .limites span').forEach((el, i) => { el.style.flex = partes[i % 3]; });
      const tu = t.querySelector('.tu'); tu.style.left = '0%';
      raf2(() => { tu.style.left = ((s - 17.5) / 72 * 100) + '%'; });
    });
  }

  function iniciar(root) {
    root.querySelectorAll('[data-count]').forEach(contar);
    barras(root); anillos(root); termometros(root);
  }
  document.addEventListener('DOMContentLoaded', () => iniciar(document));
  document.addEventListener('htmx:afterSettle', (e) => iniciar(e.target || document));

  /* ---- Paralaje suave del escenario del búho ---- */
  if (!reducir) {
    let x = 0, y = 0, pendiente = false;
    addEventListener('mousemove', (e) => {
      x = (e.clientX / innerWidth - .5) * 2; y = (e.clientY / innerHeight - .5) * 2;
      if (pendiente) return; pendiente = true;
      requestAnimationFrame(() => {
        document.querySelectorAll('.escenario').forEach((s) => { s.style.setProperty('--mx', x.toFixed(3)); s.style.setProperty('--my', y.toFixed(3)); });
        pendiente = false;
      });
    }, { passive: true });
  }

  /* ---- Cuestionario por partes ---- */
  document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('formulario');
    if (!form) return;
    const pasos = [...form.querySelectorAll('.paso')];
    const total = Number(form.dataset.total || 18);
    const btnAtras = document.getElementById('atras'), btnSig = document.getElementById('siguiente'), btnEnviar = document.getElementById('enviar');
    const relleno = document.getElementById('relleno'), marcador = document.getElementById('marcador');
    const progreso = document.getElementById('progreso'), cont = document.getElementById('contador'), txtParte = document.getElementById('textoParte');
    let actual = 0;

    const respondidas = () => new Set([...form.querySelectorAll('input.respuesta:checked')].map((r) => r.name)).size;
    function pintar(salto) {
      const n = respondidas(), pct = n / total * 100;
      relleno.style.width = pct + '%'; marcador.style.left = pct + '%';
      cont.textContent = n; progreso.setAttribute('aria-valuenow', n);
      progreso.classList.toggle('completo', n === total);
      if (salto && !reducir) { marcador.classList.remove('salta'); void marcador.offsetWidth; marcador.classList.add('salta'); }
    }
    function mostrar(i, desplazar) {
      actual = i;
      pasos.forEach((p, k) => p.classList.toggle('activo', k === i));
      btnAtras.hidden = i === 0; btnSig.hidden = i === pasos.length - 1; btnEnviar.hidden = i !== pasos.length - 1;
      txtParte.textContent = 'Parte ' + (i + 1) + ' de ' + pasos.length;
      if (desplazar) scrollTo({ top: form.offsetTop - 150, behavior: reducir ? 'auto' : 'smooth' });
    }
    function pendientes(i) {
      return [...pasos[i].querySelectorAll('[data-requerido]')].filter((card) => {
        const ok = card.querySelector('select') ? card.querySelector('select').value !== '' : !!card.querySelector('input:checked');
        card.classList.toggle('falta', !ok);
        return !ok;
      });
    }

    form.querySelectorAll('input.respuesta:checked').forEach((r) => r.closest('.pregunta').classList.add('hecha'));
    pintar(false);
    mostrar(Math.max(0, pasos.findIndex((p) => p.querySelector('.falta'))), false);

    form.addEventListener('change', (e) => {
      const card = e.target.closest('.pregunta'); if (!card) return;
      if (e.target.matches('input.respuesta')) {
        card.classList.add('hecha'); card.classList.remove('falta'); pintar(true);
        const sig = [...pasos[actual].querySelectorAll('.pregunta')].find((c, k, todas) => k > todas.indexOf(card) && !c.querySelector('input:checked') && c.querySelector('input'));
        if (sig) setTimeout(() => sig.scrollIntoView({ block: 'center', behavior: reducir ? 'auto' : 'smooth' }), 350);
      } else { card.classList.remove('falta'); }
    });
    btnSig.addEventListener('click', () => {
      const falta = pendientes(actual);
      if (falta.length) { falta[0].scrollIntoView({ block: 'center', behavior: reducir ? 'auto' : 'smooth' }); return; }
      mostrar(actual + 1, true);
    });
    btnAtras.addEventListener('click', () => mostrar(actual - 1, true));
    form.addEventListener('submit', (e) => {
      for (let i = 0; i < pasos.length; i++) {
        const falta = pendientes(i);
        if (falta.length) { e.preventDefault(); mostrar(i, false); falta[0].scrollIntoView({ block: 'center' }); return; }
      }
    });
  });

  /* ---- Limpieza reactiva de campos con error al escribir ---- */
  document.addEventListener('input', (e) => {
    if (e.target.classList && e.target.classList.contains('is-invalid')) {
      e.target.classList.remove('is-invalid');
      const mb = e.target.closest('.mb-3');
      if (mb) {
        mb.querySelectorAll('.invalid-feedback').forEach((el) => { el.style.display = 'none'; });
      }
    }
  });
})();

