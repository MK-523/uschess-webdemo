//uses publications.json and provides search UI

async function loadData() {
  const res = await fetch('publications.json');
  const data = await res.json();
  return data;
}

function renderCards(items) {
  const container = document.getElementById('results');
  container.innerHTML = '';
  if (items.length === 0) {
    container.innerHTML = '<p>No results found.</p>';
    return;
  }
  items.forEach(it => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <h3>${it.title}</h3>
      <div class="meta">${it.author} • ${it.category}</div>
      <div class="summary">${it.summary}</div>
    `;
    container.appendChild(card);
  });
}

function populateCategories(data) {
  const select = document.getElementById('categoryFilter');
  const cats = Array.from(new Set(data.map(d => d.category))).sort();
  cats.forEach(c => {
    const o = document.createElement('option');
    o.value = c;
    o.textContent = c;
    select.appendChild(o);
  });
}

function filterData(data, q, category) {
  q = (q || '').trim().toLowerCase();
  return data.filter(item => {
    if (category && item.category !== category) return false;
    if (!q) return true;
    const hay = (item.title + ' ' + item.summary + ' ' + item.content).toLowerCase();
    return hay.includes(q);
  });
}

(async function init(){
  const data = await loadData();
  populateCategories(data);
  renderCards(data);

  document.getElementById('btnSearch').addEventListener('click', () => {
    const q = document.getElementById('searchBox').value;
    const cat = document.getElementById('categoryFilter').value;
    const filtered = filterData(data, q, cat);
    renderCards(filtered);
  });

  document.getElementById('btnReset').addEventListener('click', () => {
    document.getElementById('searchBox').value = '';
    document.getElementById('categoryFilter').value = '';
    renderCards(data);
  });

  document.getElementById('searchBox').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('btnSearch').click();
  });
})();
