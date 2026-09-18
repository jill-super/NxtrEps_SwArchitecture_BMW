(() => {
  const q = document.getElementById('score-search');
  const altSel = document.getElementById('score-alt');
  const stSel = document.getElementById('score-status');
  const count = document.getElementById('score-count');
  if (!q || !altSel || !stSel) return;
  const cards = [...document.querySelectorAll('[data-alt]')];
  function apply() {
    const query = q.value.trim().toLowerCase();
    const alt = altSel.value;
    const st = stSel.value;
    let total = 0, vis = 0;
    cards.forEach((card, i) => {
      const showCard = alt === 'both' || alt === String(i);
      card.style.display = showCard ? '' : 'none';
      if (!showCard) return;
      const rows = [...card.querySelectorAll('tbody tr')];
      total += rows.length;
      rows.forEach((r) => {
        const okQ = !query || r.innerText.toLowerCase().includes(query);
        const okS = !st || r.dataset.status === st;
        const ok = okQ && okS;
        r.dataset.hidden = ok ? 'false' : 'true';
        if (ok) vis++;
      });
    });
    if (count) count.textContent = `${vis} / ${total} rows`;
  }
  [q, altSel, stSel].forEach((e) => e.addEventListener('input', apply));
  apply();
})();
