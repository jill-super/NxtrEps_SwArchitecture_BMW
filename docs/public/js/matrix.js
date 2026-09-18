(() => {
  const table = document.getElementById('mx-table');
  const input = document.getElementById('mx-search');
  const count = document.getElementById('mx-count');
  if (!table || !input) return;
  const rows = [...table.querySelectorAll('tbody tr')];
  const heads = [...table.querySelectorAll('thead th[data-col]')];
  function highlight(name) {
    table.querySelectorAll('.hl').forEach((e) => e.classList.remove('hl'));
    if (!name) return;
    const esc = window.CSS && CSS.escape ? CSS.escape(name) : name;
    table.querySelectorAll(`[data-col-cell="${esc}"]`).forEach((e) => e.classList.add('hl'));
    table.querySelectorAll(`th[data-col="${esc}"]`).forEach((e) => e.classList.add('hl'));
    table.querySelectorAll(`tr[data-row="${esc}"] td`).forEach((e) => e.classList.add('hl'));
  }
  heads.forEach((h) => {
    h.style.cursor = 'pointer';
    h.addEventListener('mouseenter', () => highlight(h.dataset.col));
    h.addEventListener('click', () => highlight(h.dataset.col));
  });
  table.querySelectorAll('[data-rowhead]').forEach((h) => {
    h.style.cursor = 'pointer';
    h.addEventListener('mouseenter', () => highlight(h.dataset.rowhead));
    h.addEventListener('click', () => highlight(h.dataset.rowhead));
  });
  table.addEventListener('mouseleave', () => highlight(''));
  function apply() {
    const q = input.value.trim().toLowerCase();
    let n = 0;
    for (const r of rows) {
      const ok = !q || r.innerText.toLowerCase().includes(q);
      r.dataset.hidden = ok ? 'false' : 'true';
      if (ok) n++;
    }
    heads.forEach((h) => {
      const hit = !q || h.textContent.toLowerCase().includes(q);
      h.style.display = hit ? '' : 'none';
      const idx = heads.indexOf(h) + 2;
      rows.forEach((r) => { const cell = r.children[idx]; if (cell) cell.style.display = hit ? '' : 'none'; });
    });
    if (count) count.textContent = `${n} / ${rows.length} rows`;
  }
  input.addEventListener('input', apply);
  apply();
})();
