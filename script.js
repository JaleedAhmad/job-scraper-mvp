document.addEventListener('DOMContentLoaded', () => {
    const searchBtn = document.getElementById('searchBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const categorySelect = document.getElementById('jobCategory');
    const loader = document.getElementById('loader');
    const loaderText = document.getElementById('loaderText');
    const resultsContainer = document.getElementById('resultsContainer');
    const tableBody = document.getElementById('tableBody');
    const noResultsMsg = document.getElementById('noResultsMsg');
    const dataSourceBadge = document.getElementById('dataSourceBadge');

    let currentCategory = '';

    // Advanced loader texts to make the short wait feel dynamic
    const loaderMessages = [
        "Initializing Scraper Engine...",
        "Bypassing Cloudflare Protections...",
        "Navigating to Indeed Search...",
        "Extracting Job Data Packets...",
        "Structuring Intelligence Payload..."
    ];
    let loaderInterval;

    searchBtn.addEventListener('click', async () => {
        const category = categorySelect.value;
        if (!category) return;
        
        currentCategory = category;

        // Reset UI Context
        resultsContainer.style.display = 'none';
        noResultsMsg.style.display = 'none';
        tableBody.innerHTML = '';
        downloadBtn.classList.add('disabled');
        downloadBtn.disabled = true;
        
        // Show Loader Sequence
        loader.style.display = 'block';
        let msgIndex = 0;
        loaderText.textContent = loaderMessages[0];
        loaderInterval = setInterval(() => {
            msgIndex = (msgIndex + 1) % loaderMessages.length;
            loaderText.textContent = loaderMessages[msgIndex];
        }, 3000); // cycle text every 3s

        // Make API Call
        try {
            const response = await fetch(`/api/jobs?category=${encodeURIComponent(category)}`);
            const json = await response.json();
            
            clearInterval(loaderInterval);
            loader.style.display = 'none';
            
            // Build the table!
            renderTable(json);

        } catch (error) {
            console.error("API Error:", error);
            clearInterval(loaderInterval);
            loader.style.display = 'none';
            alert("Failed to fetch jobs. Is the FastAPI server running?");
        }
    });

    // Handle Download Export
    downloadBtn.addEventListener('click', () => {
        if (!currentCategory) return;
        // Direct browser download via native navigation
        window.location.href = `/api/download?category=${encodeURIComponent(currentCategory)}`;
    });

    function renderTable(responseJson) {
        const jobs = responseJson.data;
        const source = responseJson.source; // "cache" or "live"
        
        resultsContainer.style.display = 'block';

        // Update Badge Design based on Cache/Live Hit
        dataSourceBadge.style.display = 'inline-block';
        if (source === 'cache') {
            dataSourceBadge.textContent = '⚡ Served instantly from Cache';
            dataSourceBadge.style.color = '#34d399'; // Emerald
            dataSourceBadge.style.background = 'rgba(16, 185, 129, 0.2)';
            dataSourceBadge.style.borderColor = 'rgba(16, 185, 129, 0.4)';
        } else {
            dataSourceBadge.textContent = '📡 Scraped Live from Source';
            dataSourceBadge.style.color = '#f87171'; // Red
            dataSourceBadge.style.background = 'rgba(239, 68, 68, 0.2)';
            dataSourceBadge.style.borderColor = 'rgba(239, 68, 68, 0.4)';
        }

        if (!jobs || jobs.length === 0) {
            noResultsMsg.style.display = 'block';
            return;
        }

        // Enable Export Feature once we have data
        downloadBtn.classList.remove('disabled');
        downloadBtn.disabled = false;

        // Render Rows
        jobs.forEach((job) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${job.Title || 'N/A'}</strong></td>
                <td><span class="text-muted"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" class="bi bi-building me-1" viewBox="0 0 16 16"><path d="M4 2.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1Zm3 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1Zm3.5-.5a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5h-1ZM4 5.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1Zm3 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1Zm3.5-.5a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5h-1ZM4 8.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1Zm3 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1Zm3.5-.5a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5h-1Zm-7 3a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1Zm3 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1Zm3.5-.5a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5h-1ZM14 14V1c0-.55-.45-1-1-1H3c-.55 0-1 .45-1 1v13H.5a.5.5 0 0 0 0 1h15a.5.5 0 0 0 0-1H14Zm-1 0H3V1h10v13Z"/></svg>${job.Company || 'N/A'}</span></td>
                <td><small>${job.Location || 'N/A'}</small></td>
                <td><a href="${job.Link}" target="_blank" class="job-link">View Listing ↗</a></td>
            `;
            tableBody.appendChild(tr);
        });
    }
});
