document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const resultsDiv = document.getElementById('results');
    const paginationDiv = document.getElementById('pagination');

    let currentPage = 1;
    let totalPages = 1;
    let currentQuery = '';

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = searchInput.value.trim();

        if (query) {
            currentQuery = query;
            currentPage = 1;
            await fetchResults(query, currentPage);
        } else {
            resultsDiv.innerHTML = `<p>Please enter one or more keywords for the search.</p>`;
            paginationDiv.innerHTML = '';
        }
    });

    async function fetchResults(query, page) {
        resultsDiv.innerHTML = `<p>Results for "<strong>${query}</strong>":</p>`;
        paginationDiv.innerHTML = '';

        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query, page: page, size: 10 })
            });

            if (!response.ok) {
                const errorData = await response.json();
                resultsDiv.innerHTML += `<p>Erreur : ${errorData.error}</p>`;
                return;
            }

            const data = await response.json();
            displayResults(data.results);
            setupPagination(data.page, data.total_pages);
        } catch (error) {
            console.error('An Error occurred during the search :', error);
            resultsDiv.innerHTML += `<p>Une erreur est survenue lors de la recherche.</p>`;
        }
    }

    function displayResults(results) {
        if (results.length === 0) {
            resultsDiv.innerHTML += '<p>No results.</p>';
            return;
        }

        const ul = document.createElement('ul');

        results.forEach(item => {
            const li = document.createElement('li');
            const titre = document.createElement('h3');
            const description = document.createElement('p');

            titre.innerHTML = `<a href="${item.url}" target="_blank">${item.title}</a>`;
            description.textContent = item.content.substring(0, 200) + '...';

            li.appendChild(titre);
            li.appendChild(description);
            ul.appendChild(li);
        });

        resultsDiv.appendChild(ul);
    }

    function setupPagination(page, total) {
        currentPage = page;
        totalPages = total;

        if (totalPages <= 1) {
            paginationDiv.innerHTML = '';
            return;
        }

        paginationDiv.innerHTML = '';

        const prevButton = document.createElement('button');
        prevButton.textContent = 'Previous';
        prevButton.disabled = (currentPage === 1);
        prevButton.addEventListener('click', () => {
            if (currentPage > 1) {
                fetchResults(currentQuery, currentPage - 1);
            }
        });
        paginationDiv.appendChild(prevButton);

        const pageList = document.createElement('div');
        pageList.className = 'page-list';

        const pagesToDisplay = getPagesToDisplay(currentPage, totalPages);

        pagesToDisplay.forEach(p => {
            if (p === '...') {
                const span = document.createElement('span');
                span.textContent = '...';
                span.className = 'pagination-ellipsis';
                pageList.appendChild(span);
            } else {
                const pageButton = document.createElement('button');
                pageButton.textContent = p;
                pageButton.disabled = (p === currentPage);
                pageButton.addEventListener('click', () => {
                    fetchResults(currentQuery, p);
                });
                pageList.appendChild(pageButton);
            }
        });

        paginationDiv.appendChild(pageList);

        const nextButton = document.createElement('button');
        nextButton.textContent = 'Next';
        nextButton.disabled = (currentPage === totalPages);
        nextButton.addEventListener('click', () => {
            if (currentPage < totalPages) {
                fetchResults(currentQuery, currentPage + 1);
            }
        });
        paginationDiv.appendChild(nextButton);
    }

    function getPagesToDisplay(currentPage, totalPages) {
        const pages = [];
        const maxVisible = 7;

        if (totalPages <= maxVisible) {
            for (let i = 1; i <= totalPages; i++) {
                pages.push(i);
            }
            return pages;
        }

        pages.push(1);

        let start = Math.max(2, currentPage - 2);
        let end = Math.min(totalPages - 1, currentPage + 2);

        if (start > 2) {
            pages.push('...');
        }

        for (let i = start; i <= end; i++) {
            pages.push(i);
        }

        if (end < totalPages - 1) {
            pages.push('...');
        }

        pages.push(totalPages);

        return pages;
    }
});
