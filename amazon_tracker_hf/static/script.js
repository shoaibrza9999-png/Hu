document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('addItemForm');
    const tableBody = document.getElementById('itemsTableBody');
    const statusDiv = document.getElementById('addStatus');
    const modal = document.getElementById('chartModal');
    const closeBtn = document.querySelector('.close');
    let priceChart = null;

    // Load initial items
    fetchItems();

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const url = document.getElementById('url').value;
        const targetPrice = document.getElementById('targetPrice').value;
        const submitBtn = form.querySelector('button');

        submitBtn.disabled = true;
        submitBtn.textContent = 'Adding...';
        statusDiv.style.display = 'none';

        try {
            const response = await fetch('/api/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url, target_price: targetPrice })
            });

            const data = await response.json();

            if (response.ok) {
                showStatus('Item added successfully!', 'success');
                form.reset();
                fetchItems();
            } else {
                showStatus(`Error: ${data.error}`, 'error');
            }
        } catch (error) {
            showStatus('Network error occurred.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Track Item';
        }
    });

    // Close modal
    closeBtn.onclick = () => {
        modal.style.display = "none";
    }

    window.onclick = (event) => {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    function showStatus(message, type) {
        statusDiv.textContent = message;
        statusDiv.className = `status-${type}`;
        statusDiv.style.display = 'block';
    }

    async function fetchItems() {
        try {
            const response = await fetch('/api/items');
            const items = await response.json();
            renderTable(items);
        } catch (error) {
            console.error('Failed to fetch items:', error);
        }
    }

    function escapeHTML(str) {
        return document.createElement('div').appendChild(document.createTextNode(str)).parentNode.innerHTML;
    }

    function renderTable(items) {
        tableBody.innerHTML = '';

        if (items.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No items tracked yet.</td></tr>';
            return;
        }

        items.forEach(item => {
            const tr = document.createElement('tr');

            // Format prices
            const currentPrice = item.latest_price !== null ? item.latest_price.toFixed(2) : 'N/A';
            const targetPrice = parseFloat(item.target_price).toFixed(2);

            // Status logic
            let statusText = 'Tracking';
            let statusClass = '';

            if (item.latest_price !== null) {
                if (item.latest_price <= item.target_price) {
                    statusText = 'Target Reached!';
                    statusClass = 'status-good';
                } else {
                    statusText = 'Above Target';
                    statusClass = 'status-bad';
                }
            }

            const safeTitle = escapeHTML(item.title || 'Loading...');
            const safeUrl = escapeHTML(item.url);

            tr.innerHTML = `
                <td>
                    <div class="item-title" title="${safeTitle}">${safeTitle}</div>
                    <a href="${safeUrl}" target="_blank" style="font-size: 0.8em; color: #007185;">View on Amazon</a>
                </td>
                <td>${currentPrice}</td>
                <td>${targetPrice}</td>
                <td class="${statusClass}">${statusText}</td>
                <td>
                    <button class="view-btn" data-item='${escapeHTML(JSON.stringify(item))}'>View Graph</button>
                </td>
            `;
            tableBody.appendChild(tr);
        });

        // Add event listeners to new buttons
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const itemData = JSON.parse(e.target.getAttribute('data-item'));
                showChart(itemData);
            });
        });
    }

    function showChart(item) {
        const safeTitle = escapeHTML(item.title || 'Unknown');
        document.getElementById('modalTitle').textContent = `Price History: ${safeTitle}`;
        modal.style.display = "block";

        const ctx = document.getElementById('priceChart').getContext('2d');

        // Destroy existing chart if it exists
        if (priceChart) {
            priceChart.destroy();
        }

        // Prepare data
        const labels = item.history.map(h => new Date(h.timestamp).toLocaleDateString() + ' ' + new Date(h.timestamp).toLocaleTimeString());
        const data = item.history.map(h => h.price);

        // Target price line
        const targetData = Array(labels.length).fill(item.target_price);

        priceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Current Price',
                        data: data,
                        borderColor: '#232f3e',
                        backgroundColor: 'rgba(35, 47, 62, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.1
                    },
                    {
                        label: 'Target Price',
                        data: targetData,
                        borderColor: '#b12704',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Price'
                        }
                    },
                    x: {
                        ticks: {
                            maxTicksLimit: 10
                        }
                    }
                }
            }
        });
    }
});
