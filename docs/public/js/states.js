(() => {
  const svg = document.getElementById('state-svg');
  const table = document.getElementById('tr-table');
  if (!svg || !table) return;
  const rows = [...table.querySelectorAll('tbody tr')];
  let active = '';
  function apply() {
    let n = 0;
    for (const r of rows) {
      const ok = !active || r.dataset.from === active || r.dataset.to === active;
      r.dataset.hidden = ok ? 'false' : 'true';
      if (ok) n++;
    }
    const c = document.querySelector('[data-filter-count="tr-table"]');
    if (c) c.textContent = active ? `${n} / ${rows.length} for ${active}` : `${n} / ${rows.length} shown`;
    svg.querySelectorAll('.node').forEach((el) => el.classList.toggle('active', el.dataset.state === active));
  }
  svg.querySelectorAll('.node').forEach((el) => {
    el.addEventListener('click', () => { active = active === el.dataset.state ? '' : el.dataset.state; apply(); });
  });
  apply();
})();
