import { applyFilter, filters } from '/static/js/result_cards.js';

document.addEventListener('DOMContentLoaded', () => {

    //Sidebar toggle mechanism
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');

    function closeSidebar() {
    sidebar.classList.remove('open');
    overlay.classList.remove('open');
    }

    document.querySelector('#sidebar-toggle').addEventListener('click', () => {
    sidebar.classList.toggle('open');
    overlay.classList.toggle('open');
    });

    overlay.addEventListener('click', closeSidebar);


    // Filter toggles within sidebar
    const switchDuunitori = document.querySelector('#duunitori-btn');

    switchDuunitori.addEventListener('click', () => {
      switchDuunitori.classList.toggle('on');

        if (switchDuunitori.classList.contains('on')) {
    applyFilter({ boards: [...filters.boards, 'Duunitori'] });
        } else {
    applyFilter({ boards: filters.boards.filter(b => b !== 'Duunitori') });
        }
    });

    // Display selected minimum score at the filter label
    const minScore = document.getElementById('minScore');
    const minScoreDisplay = document.getElementById('minScoreDisplay');

    minScore.addEventListener('input', () => {
        minScoreDisplay.textContent = minScore.value;
      });
});