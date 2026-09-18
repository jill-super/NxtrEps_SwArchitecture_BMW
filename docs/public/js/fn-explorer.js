(() => {
  const input = document.getElementById('fn-search');
  const count = document.getElementById('fn-count');
  const cards = [...document.querySelectorAll('.fn-card')];
  if (!input) return;
  function apply() {
    const q = input.value.trim().toLowerCase();
    let n = 0;
    for (const c of cards) {
      const ok = !q || (c.dataset.search || '').includes(q);
      c.style.display = ok ? '' : 'none';
      if (ok) n++;
    }
    if (count) count.textContent = `${n} / ${cards.length} shown`;
  }
  input.addEventListener('input', apply);
  apply();
  const hash = location.hash.slice(1);
  if (hash) document.getElementById(hash)?.scrollIntoView();
})();
