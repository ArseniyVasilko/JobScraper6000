let grid;
let page = 1;
let loading = false;
let exhausted = false;

export const filters = {
  boards: [],
  types: ["filtered_jobs", 'discarded_jobs', 'failed_evaluations']
};

document.addEventListener('DOMContentLoaded', () => {
  grid = document.querySelector('.card-grid');
  console.log(grid);
  addCards();
});

async function addCards() {
  if (loading || exhausted) return;
  loading = true;

  const params = new URLSearchParams({ page });
  filters.boards.forEach(b => params.append('boards', b));
  filters.types.forEach(t => params.append('type', t));

  const res = await fetch(`/api/get_cards?${params}`);
  const data = await res.json();

  data.cards.forEach(job => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
                        <div class="card-title"><h2><a href="${job.link}" target="_blank">${job.title}</a></h2></div>
                        <div class="card-status"><h3>Status: ${job.status}</h3></div>
                        <div class="card-list"><ul>
                            <li>Keywords: insert_keywords</li>
                            <li>Published: ${job.date}</li>
                            <li>Location: ${job.location}</li>
                            <li>Job Board: ${job.board}</li>
                        </ul></div>
                        <div class="card-button">
                            <button type="button">Details</button>
                        </div>
                     `;
    grid.appendChild(card);
  });

  page++;
  loading = false;
  if (!data.has_more) { exhausted = true; observer.disconnect(); }
  else observeLast();
}

const observer = new IntersectionObserver((entries) => {
  if (entries[0].isIntersecting) {
    observer.disconnect();
    addCards();
  }
}, { rootMargin: '200px' });

function observeLast() {
  const cards = grid.querySelectorAll('.card');
  if (cards.length) observer.observe(cards[cards.length - 1]);
}

export function applyFilter(newFilters) {
  Object.assign(filters, newFilters);
  page = 1;
  exhausted = false;
  grid.innerHTML = '';
  addCards();
}